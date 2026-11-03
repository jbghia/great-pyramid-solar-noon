#!/usr/bin/env python3
"""Epoch sensitivity of the stellar meridian-altitude correspondences.

For every year of a construction-epoch range, the apparent declination of each
Hipparcos star (V < 2.5) is evaluated at local mean midnight of the same
calendar night as in the principal analysis, and converted to an airless
meridian altitude h = 90 - |phi - dec|. The residual h - alpha is the angular
separation from an idealized due-south shaft direction at the star's meridian
transit (Section 3.10 of the paper): at transit the altitude match depends only
on declination, so no solar root or night-time search is repeated.

Same ephemeris, catalogue, astrometry, location and fixed TT-UT1 as the
principal scripts. Parallax and radial velocity are zero, refraction is
neglected. Historical accuracy requires validation.
"""
import argparse
import importlib.metadata
from pathlib import Path

from pyramid_solar_alignment import Engine, calendar_jd, digest, number, save_csv, save_json
from stellar_alignment_search import NAMES, TARGETS, catalogue

PETRIE_KINGS = 45 + 13 / 60

# (case_id, chamber, inclination, source, reference night (month, day))
CASES = [
    ('Kings_adopted', 'Kings', 45.0, 'adopted reference value (paper)', (11, 22)),
    ('Kings_Petrie', 'Kings', PETRIE_KINGS, 'Petrie (1883), 45 deg 13 arcmin', (11, 22)),
    ('Queens_adopted', 'Queens', 39.6078, 'adopted reference value (paper)', (12, 11)),
    ('Queens_40', 'Queens', 40.0, 'alternative value (paper, Section 3.5)', (12, 11)),
]


def bce(year):
    """Astronomical year number to a BCE/CE label."""
    return f'{1 - year} BCE' if year <= 0 else f'{year} CE'


def midnight_ut1(year, month, day, longitude):
    """UT1 Julian date of 00:00 local mean solar time on a proleptic Julian date."""
    return calendar_jd(year, month, day) - longitude / 360


def meridian_altitude(dec, phi):
    return 90 - abs(phi - dec)


def slope_per_century(years, residuals, centre, half_width=50):
    """Least-squares slope (deg per century) over centre +/- half_width years.

    A fit is used because single-year differences jitter by about +/-30 % with
    the four-year Julian leap cycle (annual aberration on a fixed calendar date).
    """
    pts = [(y, r) for y, r in zip(years, residuals) if abs(y - centre) <= half_width]
    if len(pts) < 3:
        raise ValueError('Too few years for the slope fit')
    my = sum(y for y, _ in pts) / len(pts)
    mr = sum(r for _, r in pts) / len(pts)
    return 100 * sum((y - my) * (r - mr) for y, r in pts) / sum((y - my) ** 2 for y, _ in pts)


def best_epoch(years, residuals):
    """Zero crossings of residual(year) by linear interpolation, else the minimum."""
    crossings = []
    for (y0, r0), (y1, r1) in zip(zip(years, residuals), zip(years[1:], residuals[1:])):
        if r0 == 0:
            crossings.append(float(y0))
        elif r0 * r1 < 0:
            crossings.append(y0 + (y1 - y0) * r0 / (r0 - r1))
    if residuals and residuals[-1] == 0:
        crossings.append(float(years[-1]))
    if crossings:
        return crossings, 'zero crossing'
    i = min(range(len(years)), key=lambda k: abs(residuals[k]))
    return [float(years[i])], 'minimum |residual| (no crossing in range)'


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--ephemeris', required=True)
    p.add_argument('--catalogue', required=True, help='Archived CSV; no automatic downloads or fallback')
    p.add_argument('--output-dir', default='results/epoch_scan')
    p.add_argument('--first-year', type=int, default=-2849, help='Astronomical year (default -2849 = 2850 BCE)')
    p.add_argument('--last-year', type=int, default=-2149, help='Astronomical year (default -2149 = 2150 BCE)')
    p.add_argument('--reference-year', type=int, default=-2549, help='Epoch of the principal analysis')
    p.add_argument('--vmag-limit', type=float, default=2.5)
    p.add_argument('--expected-count', type=int, default=93)
    p.add_argument('--bands', default='0.1,0.2', help='Residual levels (deg) for the catalogue baseline counts')
    a = p.parse_args()
    if not a.first_year < a.reference_year < a.last_year:
        raise ValueError('Reference year must lie inside the scanned range')
    if a.first_year < -3000 or a.last_year > 2999:
        raise ValueError('Range exceeds DE422 coverage')
    bands = [number(b) for b in a.bands.split(',')]
    stars, excluded = catalogue(a.catalogue, number(a.vmag_limit), a.expected_count)
    for chamber, hips in TARGETS.items():
        if not hips.issubset({s['HIP'] for s in stars}):
            raise ValueError(f'Targets for {chamber} missing from catalogue')
    years = list(range(a.first_year, a.last_year + 1))
    engine = Engine(a.ephemeris)
    try:
        from skyfield.api import Star
        nights = sorted({c[4] for c in CASES})
        times = {n: engine.ts.ut1_jd([midnight_ut1(y, *n, engine.lon) for y in years]) for n in nights}
        dec = {}
        for s in stars:
            star = Star(ra_hours=s['RAICRS'] / 15, dec_degrees=s['DEICRS'], ra_mas_per_year=s['pmRA'],
                        dec_mas_per_year=s['pmDE'], epoch=2451545 + (s['epoch_jyear'] - 2000) * 365.25,
                        parallax_mas=0, radial_km_per_s=0)
            for n, t in times.items():
                _, d, _ = engine.earth.at(t).observe(star).apparent().radec(epoch='date')
                dec[s['HIP'], n] = [float(x) for x in d.degrees]

        scan, best, baseline = [], [], []
        for case_id, chamber, alpha, source, night in CASES:
            dreq = alpha + engine.phi - 90
            for hip in sorted(TARGETS[chamber]):
                if max(dec[hip, night]) >= engine.phi:
                    raise ValueError('Target does not culminate south of the zenith')
                res = [meridian_altitude(d, engine.phi) - alpha for d in dec[hip, night]]
                for y, d, r in zip(years, dec[hip, night], res):
                    scan.append({'case_id': case_id, 'chamber': chamber, 'inclination_deg': alpha,
                                 'required_dec_deg': dreq, 'HIP': hip, 'name': NAMES[hip],
                                 'year_astronomical': y, 'year_label': bce(y),
                                 'apparent_dec_deg': d, 'meridian_altitude_deg': meridian_altitude(d, engine.phi),
                                 'residual_deg': r})
                k = years.index(a.reference_year)
                slope = slope_per_century(years, res, a.reference_year)
                epochs, method = best_epoch(years, res)
                for e in epochs:
                    best.append({'case_id': case_id, 'chamber': chamber, 'inclination_deg': alpha,
                                 'inclination_source': source, 'HIP': hip, 'name': NAMES[hip],
                                 'best_year_astronomical': round(e, 1), 'best_year_label': bce(round(e)),
                                 'method': method, 'residual_at_reference_deg': res[k],
                                 'residual_change_deg_per_century': slope,
                                 'min_abs_residual_in_range_deg': min(abs(r) for r in res)})
            for i, y in enumerate(years):
                # Southern shafts: only stars culminating south of the zenith (dec < phi).
                ranked = sorted(((abs(meridian_altitude(dec[s['HIP'], night][i], engine.phi) - alpha), s)
                                 for s in stars if dec[s['HIP'], night][i] < engine.phi),
                                key=lambda x: (x[0], x[1]['HIP']))
                row = {'case_id': case_id, 'chamber': chamber, 'inclination_deg': alpha,
                       'year_astronomical': y, 'year_label': bce(y),
                       'closest_HIP': ranked[0][1]['HIP'], 'closest_name': ranked[0][1]['name'],
                       'closest_abs_residual_deg': ranked[0][0]}
                for b in bands:
                    row[f'stars_within_{b:g}_deg'] = sum(1 for r, _ in ranked if r <= b)
                baseline.append(row)

        out = Path(a.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        save_csv(out / 'target_residuals_by_year.csv', scan)
        save_csv(out / 'best_epochs.csv', best)
        save_csv(out / 'catalogue_baseline_by_year.csv', baseline)
        metadata = engine.metadata()
        metadata.update({
            'script_sha256': digest(__file__), 'catalogue_sha256': digest(a.catalogue),
            'count': len(stars), 'excluded_by_magnitude': excluded, 'strict_Vmag_limit': a.vmag_limit,
            'years_astronomical': [a.first_year, a.last_year], 'year_step': 1,
            'reference_year_astronomical': a.reference_year,
            'cases': [{'case_id': c[0], 'chamber': c[1], 'inclination_deg': c[2], 'source': c[3],
                       'reference_night_month_day': list(c[4])} for c in CASES],
            'evaluation_instant': '00:00 local mean solar time (UT1 + longitude/15 h) on the reference calendar night of each year, proleptic Julian',
            'quantity': 'apparent geocentric declination of date; meridian altitude 90 - |phi - dec|; residual = altitude - inclination',
            'interpretation': 'separation from an idealized due-south direction at meridian transit; no right-ascension or time-window filter',
            'best_epoch': 'linear interpolation of residual zero crossings between consecutive years',
            'baseline_bands_deg': bands, 'baseline_selection': 'catalogue stars with dec < latitude (south culmination)',
            'slope_fit': 'least squares over reference year +/- 50 years', 'parallax_mas': 0, 'radial_km_per_s': 0,
            'scipy': importlib.metadata.version('scipy')})
        save_json(out / 'run_metadata.json', metadata)
        print(f'Wrote {len(scan)} target rows, {len(best)} best epochs, {len(baseline)} baseline rows '
              f'for {len(years)} years and {len(stars)} stars')
    finally:
        engine.eph.close()


if __name__ == '__main__':
    main()
