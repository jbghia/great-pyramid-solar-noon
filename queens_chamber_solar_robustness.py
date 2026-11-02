#!/usr/bin/env python3
"""Queen's Chamber inclination sensitivity from consecutive PyEphem transits.

Dates are PyEphem UT; internal Delta T is retained and reported. Altitudes are
apparent topocentric solar-center values with pressure=0. Crossings interpolate
daily transits; they are not continuous geocentric TT declination roots.
"""
import argparse
import importlib.metadata
import math
from pathlib import Path
from pyramid_solar_alignment import DAY, PHI, LON, number, digest, save_csv, save_json, julian_label


def sample_transits(next_event, start, end):
    start, end = number(start),number(end)
    if end <= start:
        raise ValueError('Increasing UT interval required')
    rows, cursor = [], start
    while cursor < end:
        row = next_event(cursor)
        event = number(row['jd_ut'])
        number(row['altitude_deg'])
        if event <= cursor:
            raise RuntimeError('Transit did not advance')
        if event > end:
            break
        if rows and not 0.9 < event-rows[-1]['jd_ut'] < 1.1:
            raise RuntimeError('Skipped or repeated daily transit')
        rows.append(row)
        cursor = event+1/DAY
    if len(rows) < 3:
        raise RuntimeError('Too few daily transits')
    return rows


def crossings(samples, target):
    target = number(target)
    if len(samples) < 2:
        raise ValueError('At least two ordered samples required')
    found = []
    for a,b in zip(samples,samples[1:]):
        if b['jd_ut'] <= a['jd_ut']:
            raise ValueError('Transit dates must increase')
        f0, f1 = a['altitude_deg']-target,b['altitude_deg']-target
        r = a['jd_ut'] if f0 == 0 else a['jd_ut']+(b['jd_ut']-a['jd_ut'])*f0/(f0-f1) if f0*f1 < 0 else None
        if r is not None and (not found or abs(r-found[-1]) > 1e-8):
            found.append(r)
    if samples[-1]['altitude_deg'] == target and (not found or abs(samples[-1]['jd_ut']-found[-1]) > 1e-8):
        found.append(samples[-1]['jd_ut'])
    return found


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name, default in [('start-ut',790334.5),('end-ut',790475.5),('latitude',PHI),('longitude',LON),('primary',39.6078),('alternative',40.0),('band',0.2)]:
        p.add_argument('--'+name,type=float,default=default)
    p.add_argument('--output-dir',default='results/queen_sensitivity')
    a = p.parse_args()
    for value in [a.latitude,a.longitude,a.primary,a.alternative,a.band]:
        number(value)
    if not -90 < a.latitude < 90 or abs(a.longitude) > 180 or a.band <= 0 or not all(0 < x < 90 for x in [a.primary,a.alternative]):
        p.error('Invalid geometry/band')
    import ephem
    observer = ephem.Observer()
    observer.lat, observer.lon = str(a.latitude),str(a.longitude)
    observer.elevation, observer.pressure = 0,0
    sun = ephem.Sun()
    def next_event(cursor):
        observer.date = ephem.Date(cursor-2415020.0)
        transit = observer.next_transit(sun)
        observer.date = transit
        sun.compute(observer)
        ut = float(transit)+2415020.0
        dt = float(ephem.delta_t(transit))
        return {'jd_ut':ut,'ut_label':julian_label(ut,'UT (PyEphem)'),'altitude_deg':math.degrees(float(sun.alt)),'pyephem_delta_t_seconds':dt,'jd_tt_using_pyephem_delta_t':ut+dt/DAY}
    samples = sample_transits(next_event,a.start_ut,a.end_ut)
    rows, cases = [], {}
    for case, alpha in [('primary',a.primary),('alternative',a.alternative)]:
        levels = [crossings(samples,target) for target in [alpha,alpha-a.band,alpha+a.band]]
        if any(len(x) != 2 for x in levels):
            raise RuntimeError(f'{case}: expected two crossings per level; got {[len(x) for x in levels]}')
        cases[case] = levels[0]
        for branch, (ut,low,high) in enumerate(zip(*levels),1):
            dt = float(ephem.delta_t(ephem.Date(ut-2415020.0)))
            nearest = min(samples,key=lambda row:abs(row['jd_ut']-ut))
            rows.append({'case':case,'branch':branch,'elevation_deg':alpha,'interpolated_crossing_jd_ut':ut,'ut_label':julian_label(ut,'UT (PyEphem)'),'pyephem_delta_t_seconds':dt,'interpolated_crossing_tt_using_pyephem_delta_t':ut+dt/DAY,'lower_altitude_crossing_ut':low,'upper_altitude_crossing_ut':high,'sensitivity_start_ut':min(low,high),'sensitivity_end_ut':max(low,high),'nearest_transit_jd_ut':nearest['jd_ut'],'nearest_transit_residual_deg':nearest['altitude_deg']-alpha})
    shifts = [{'branch':i+1,'alternative_minus_primary_days_ut':y-x} for i,(x,y) in enumerate(zip(cases['primary'],cases['alternative']))]
    out = Path(a.output_dir)
    out.mkdir(parents=True,exist_ok=True)
    save_csv(out/'daily_transits.csv',samples)
    save_csv(out/'inclination_crossings.csv',rows)
    save_csv(out/'inclination_shifts.csv',shifts)
    save_json(out/'run_metadata.json',{'script_sha256':digest(__file__),'ephem':importlib.metadata.version('ephem'),'latitude_deg':a.latitude,'longitude_deg_east':a.longitude,'interval_jd_ut':[a.start_ut,a.end_ut],'primary_deg':a.primary,'alternative_deg':a.alternative,'band_deg':a.band,'samples':len(samples),'time_scale':'PyEphem UT; internal Delta T retained and reported','quantity':'airless apparent topocentric solar-center transit altitude','method':'linear interpolation of consecutive daily transits','historical_accuracy':'not independently validated'})
    print(f'Wrote {len(samples)} consecutive transits and two sensitivity shifts')


if __name__ == '__main__':
    main()
