#!/usr/bin/env python3
"""Solar meridian-altitude roots, daily transits, and nighttime search windows.

Skyfield apparent geocentric coordinates of date; no refraction or solar
parallax. Rotation uses GAST and a fixed, explicit TT-UT1 offset. Other scripts
import dependency-lazy helpers here. Historical accuracy requires validation.
"""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path

DAY = 86400.0
PHI, LON, DT = 29.9792, 31.1342, 61033.0


def number(x):
    x = float(x)
    if not math.isfinite(x):
        raise ValueError('Nonfinite input')
    return x


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')


def save_csv(path, rows):
    if not rows:
        raise ValueError('No output rows')
    with Path(path).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def calendar_jd(year, month, day=1.0):
    if not 1 <= month <= 12:
        raise ValueError('Invalid month')
    if month <= 2:
        year, month = year-1, month+12
    return math.floor(365.25*(year+4716))+math.floor(30.6001*(month+1))+day-1524.5


def julian_label(jd, scale):
    # Proleptic Julian calendar, astronomical year numbering; not UTC.
    z = math.floor(jd+0.5)
    seconds = round((jd+0.5-z)*DAY)
    if seconds == 86400:
        z, seconds = z+1, 0
    c = z+1524
    d = math.floor((c-122.1)/365.25)
    e = math.floor(365.25*d)
    g = math.floor((c-e)/30.6001)
    day = c-e-math.floor(30.6001*g)
    month = g-1 if g < 13.5 else g-13
    year = d-4716 if month > 2.5 else d-4715
    era = f'{1-year} BCE' if year <= 0 else f'{year} CE'
    return f'{day:02d}-{month:02d}-{era} {seconds//3600:02d}:{seconds%3600//60:02d}:{seconds%60:02d} {scale}'


def next_midnight(noon_ut1, longitude):
    return math.floor(noon_ut1+longitude/360-0.5)+1.5-longitude/360


def bisect(f, a, b, tolerance_seconds=0.001):
    if not a < b or tolerance_seconds <= 0:
        raise ValueError('Invalid root interval/tolerance')
    fa, fb = number(f(a)), number(f(b))
    if fa == 0:
        return a
    if fb == 0:
        return b
    if fa*fb > 0:
        raise ValueError('Root not bracketed')
    for _ in range(150):
        m = (a+b)/2
        if m == a or m == b:
            break
        fm = number(f(m))
        if fm == 0:
            return m
        if fa*fm <= 0:
            b = m
        else:
            a, fa = m, fm
        if (b-a)*DAY <= tolerance_seconds:
            break
    return (a+b)/2


def roots(f, start, end):
    if end <= start:
        raise ValueError('Search interval must increase')
    found, a = [], start
    while a < end:
        b = min(a+1, end)
        fa, fb = number(f(a)), number(f(b))
        r = a if fa == 0 else bisect(f, a, b) if fa*fb < 0 else b if b == end and fb == 0 else None
        if r is not None and (not found or abs(r-found[-1])*DAY > 0.01):
            found.append(r)
        a = b
    return found


class Engine:
    def __init__(self, kernel, latitude=PHI, longitude=LON, delta_t=DT):
        from skyfield.api import load, load_file, wgs84
        self.phi, self.lon, self.dt = map(number, (latitude, longitude, delta_t))
        if not -90 < self.phi < 90 or abs(self.lon) > 180:
            raise ValueError('Invalid location')
        self.path = Path(kernel).expanduser().resolve()
        if not self.path.is_file():
            raise FileNotFoundError('Provide a LOCAL BSP covering the historical interval')
        self.ts = load.timescale(delta_t=self.dt, builtin=True)
        self.eph = load_file(str(self.path))
        self.earth, self.sun = self.eph['earth'], self.eph['sun']
        self.observer = self.earth+wgs84.latlon(self.phi, self.lon, elevation_m=0)

    def solar(self, jd_tt):
        t = self.ts.tt_jd(jd_tt)
        ra, dec, _ = self.earth.at(t).observe(self.sun).apparent().radec(epoch='date')
        return float(ra.hours)*15, float(dec.degrees)

    def altitude(self, jd_tt):
        return 90-abs(self.phi-self.solar(jd_tt)[1])

    def noon(self, midnight_ut1):
        center = midnight_ut1+0.5-self.lon/360
        def hour_angle(jd):
            t = self.ts.ut1_jd(jd)
            ra, _ = self.solar(float(t.tt))
            return (float(t.gast)*15+self.lon-ra+180)%360-180
        a, b = center-3/24, center+3/24
        if not -90 < hour_angle(a) < 0 < hour_angle(b) < 90:
            raise RuntimeError('Upper transit not safely bracketed')
        return bisect(hour_angle, a, b)

    def metadata(self):
        return {'kernel_sha256':digest(self.path), 'skyfield':importlib.metadata.version('skyfield'),
                'latitude_deg':self.phi, 'longitude_deg_east':self.lon, 'delta_t_seconds':self.dt,
                'delta_t_model':'fixed TT minus UT1', 'calendar':'proleptic Julian',
                'solar_frame':'apparent geocentric, true equator/equinox of date; no refraction/parallax',
                'historical_accuracy':'not independently validated'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ephemeris', required=True)
    p.add_argument('--output-dir', default='results/solar')
    for name, default in [('start-tt',790335.5),('end-tt',790475.5),('latitude',PHI),('longitude',LON),('delta-t',DT),('king-angle',45.0),('queen-angle',39.6078),('band',0.2)]:
        p.add_argument('--'+name, type=float, default=default)
    p.add_argument('--modern-sanity', action='store_true', help='Check broad J2000 solar declination; requires J2000 kernel coverage')
    a = p.parse_args()
    for value in [a.start_tt,a.end_tt,a.king_angle,a.queen_angle,a.band]:
        number(value)
    if a.start_tt >= a.end_tt or a.band <= 0 or not all(0 < x < 90 for x in [a.king_angle,a.queen_angle]):
        p.error('Invalid interval, inclinations, or band')
    engine = Engine(a.ephemeris,a.latitude,a.longitude,a.delta_t)
    try:
        if a.modern_sanity and not -24 < engine.solar(2451545.0)[1] < -22:
            raise RuntimeError('J2000 January solar-declination sanity check failed')
        central, boundaries, noons, windows = [], [], [], []
        for chamber, alpha in [('Kings',a.king_angle),('Queens',a.queen_angle)]:
            levels = [roots(lambda jd, target=target:engine.altitude(jd)-target,a.start_tt,a.end_tt) for target in [alpha,alpha-a.band,alpha+a.band]]
            if any(len(level) != 2 for level in levels):
                raise RuntimeError(f'{chamber}: expected two roots on each level; got {[len(x) for x in levels]}')
            for branch, (tt, low, high) in enumerate(zip(*levels),1):
                if engine.solar(tt)[1] >= engine.phi:
                    raise ValueError('South-of-zenith solar culmination required')
                ut = tt-engine.dt/DAY
                central.append({'chamber':chamber,'branch':branch,'elevation_deg':alpha,'root_jd_tt':tt,'root_jd_ut1':ut,'tt_label':julian_label(tt,'TT'),'ut1_label':julian_label(ut,'UT1'),'residual_deg':engine.altitude(tt)-alpha})
                boundaries.append({'chamber':chamber,'branch':branch,'lower_altitude_root_tt':low,'upper_altitude_root_tt':high,'sensitivity_start_tt':min(low,high),'sensitivity_end_tt':max(low,high),'band_deg':a.band})
                day = math.floor(ut-0.5)+0.5
                nearby = []
                for offset in [-1,0,1]:
                    noon = engine.noon(day+offset)
                    alt = engine.altitude(noon+engine.dt/DAY)
                    nearby.append({'chamber':chamber,'branch':branch,'noon_jd_ut1':noon,'noon_jd_tt':noon+engine.dt/DAY,'ut1_label':julian_label(noon,'UT1'),'local_mean_label':julian_label(noon+engine.lon/360,'local mean solar time'),'altitude_deg':alt,'residual_deg':alt-alpha,'distance_from_root_seconds':abs(noon-ut)*DAY,'selected':False})
                best = min(nearby,key=lambda r:r['distance_from_root_seconds'])
                best['selected'] = True
                noons.extend(nearby)
                center = next_midnight(best['noon_jd_ut1'],engine.lon)
                windows.append({'case_id':f'{chamber}_{branch}','chamber':chamber,'elevation_deg':alpha,'azimuth_deg':180.0,'root_jd_tt':tt,'selected_noon_jd_ut1':best['noon_jd_ut1'],'center_jd_ut1':center,'start_jd_ut1':center-1/24,'end_jd_ut1':center+1/24,'local_midnight_label':julian_label(center+engine.lon/360,'local mean solar time')})
        out = Path(a.output_dir)
        out.mkdir(parents=True,exist_ok=True)
        save_csv(out/'solar_roots.csv',central)
        save_csv(out/'sensitivity_boundaries.csv',boundaries)
        save_csv(out/'daily_solar_noons.csv',noons)
        metadata = engine.metadata()
        metadata.update({'script_sha256':digest(__file__),'modern_sanity_run':a.modern_sanity,'root_tolerance_seconds':0.001,'noon_selection':'closest transit in TIME, then following local mean midnight','inclination_band_deg':a.band,'search_interval_jd_tt':[a.start_tt,a.end_tt],'reference_elevations_deg':[a.king_angle,a.queen_angle]})
        save_json(out/'run_metadata.json',metadata)
        save_json(out/'stellar_windows.json',{'schema':'pyramid-windows-v2','metadata':metadata,'windows':windows})
        print(f'Wrote {len(central)} roots and {len(windows)} windows to {out}')
    finally:
        engine.eph.close()


if __name__ == '__main__':
    main()
