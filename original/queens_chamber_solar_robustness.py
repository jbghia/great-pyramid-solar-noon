#!/usr/bin/env python3
"""
Robustness test: Queen's Chamber southern shaft solar-noon altitude correspondences.

Primary adopted inclination: 39.6078 deg
    Gantenbrink lower southern shaft average, 24 measurements over 28 m.
Sensitivity inclination: 40.0000 deg
    Bauval 1993 reported revised inclination.

Finds the two calendar days in the specified interval at which the Sun's
geometric altitude at upper culmination (solar noon / meridian transit)
at Giza equals each adopted inclination. Also reports the +/-0.200 deg band.

Dependency:
    pip install pyephem
"""

from datetime import datetime
import csv
import math

import ephem


# ----------------------------- configuration -----------------------------

LATITUDE = "29.9792"
LONGITUDE = "31.1342"
ALTITUDE_BAND_DEG = 0.200

# Search interval in Julian Day (TT).
# PyEphem internally uses UT-like Dynamical Time input. For this sensitivity
# test, the supplied JD(TT) instants are evaluated directly; the 16.95-hour
# TT-UT offset is therefore retained rather than separately modelled.
JD_TT_START = 790335.5
JD_TT_END = 790475.5

CASES = {
    "primary_39.6078": 39.6078,
    "sensitivity_40.0000": 40.0000,
}

OUTPUT_CSV = "queens_chamber_solar_robustness.csv"


# ------------------------------- helpers ---------------------------------


def jd_to_ephem_date(jd):
    """Convert a Julian Day to a PyEphem Date."""
    return ephem.Date(jd - 2415020.0)


def ephem_date_to_jd(date):
    """Convert a PyEphem Date back to Julian Day."""
    return float(date) + 2415020.0


def solar_noon_altitude(jd_start, observer):
    """
    Return the Julian Day and geometric solar altitude at the next solar
    meridian transit after jd_start.

    pressure = 0 disables atmospheric refraction, giving a geometric altitude.
    """
    sun = ephem.Sun()
    observer.date = jd_to_ephem_date(jd_start)

    transit_date = observer.next_transit(sun)
    observer.date = transit_date
    sun.compute(observer)

    return ephem_date_to_jd(transit_date), math.degrees(sun.alt)


def daily_noon_altitudes(observer):
    """
    Return parallel lists of Julian Days and solar-noon altitudes for every
    solar day in the configured interval.
    """
    jd = JD_TT_START
    jds = []
    altitudes = []

    while jd <= JD_TT_END:
        transit_jd, altitude = solar_noon_altitude(jd, observer)
        jds.append(transit_jd)
        altitudes.append(altitude)

        # Advance by one day. next_transit() will find the following transit.
        jd = transit_jd + 1.0

    return jds, altitudes


def find_roots(jds, altitudes, target_altitude):
    """
    Find dates at which daily solar-noon altitude crosses target_altitude.

    Returns a list of (jd_root, lower_band_jd_or_None, upper_band_jd_or_None).
    Linear interpolation is appropriate because consecutive daily noon
    altitudes change smoothly and by much less than one degree.
    """
    roots = []

    for i in range(1, len(altitudes)):
        f0 = altitudes[i - 1] - target_altitude
        f1 = altitudes[i] - target_altitude

        if f0 == 0.0:
            roots.append((jds[i - 1], None, None))
        elif f0 * f1 < 0.0:
            fraction = f0 / (f0 - f1)
            jd_root = jds[i - 1] + fraction * (jds[i] - jds[i - 1])
            roots.append((jd_root, None, None))

    # Handle an exact endpoint value.
    if altitudes and altitudes[-1] == target_altitude:
        roots.append((jds[-1], None, None))

    return roots


def find_band_boundaries(jds, altitudes, target_altitude):
    """Find crossings for target - band and target + band."""
    lower = find_roots(jds, altitudes, target_altitude - ALTITUDE_BAND_DEG)
    upper = find_roots(jds, altitudes, target_altitude + ALTITUDE_BAND_DEG)
    return lower, upper


def nearest_value(jd_root, candidate_jds, candidate_altitudes):
    """Return the nearest sampled daily-noon altitude to a root."""
    best_index = min(
        range(len(candidate_jds)),
        key=lambda i: abs(candidate_jds[i] - jd_root),
    )
    return (
        candidate_jds[best_index],
        candidate_altitudes[best_index],
    )


def format_ephem_date(jd):
    year, month, day, hour, minute, second = jd_to_ephem_date(jd).tuple()
    return (
        f"{year:04d}-{month:02d}-{day:02d}",
        f"{hour:02d}:{minute:02d}:{second:05.2f}",
    )


# --------------------------------- main ----------------------------------


def main():
    observer = ephem.Observer()
    observer.lat = LATITUDE
    observer.lon = LONGITUDE
    observer.elevation = 0
    observer.pressure = 0  # geometric altitude: no refraction
    observer.epoch = "2000"

    rows = []

    # Compute the daily solar-noon series once; reuse it for both inclinations.
    noon_jds, noon_altitudes = daily_noon_altitudes(observer)

    for case_name, inclination in CASES.items():
        print(f"\n=== {case_name}: adopted inclination {inclination:.4f} deg ===")

        central_roots = find_roots(noon_jds, noon_altitudes, inclination)
        lower_roots, upper_roots = find_band_boundaries(
            noon_jds, noon_altitudes, inclination
        )

        if len(central_roots) != 2:
            raise RuntimeError(
                f"Expected two central roots for {case_name}, "
                f"but found {len(central_roots)}: "
                f"{[r[0] for r in central_roots]}"
            )

        for i, (central_root, _, _) in enumerate(central_roots, start=1):
            lower_jd = lower_roots[i - 1][0] if i - 1 < len(lower_roots) else ""
            upper_jd = upper_roots[i - 1][0] if i - 1 < len(upper_roots) else ""

            nearest_jd, nearest_altitude = nearest_value(
                central_root, noon_jds, noon_altitudes
            )
            residual = nearest_altitude - inclination
            within_band = abs(residual) <= ALTITUDE_BAND_DEG

            calendar_day, transit_time = format_ephem_date(nearest_jd)

            row = {
                "case": case_name,
                "adopted_inclination_deg": inclination,
                "correspondence": i,
                "central_root_jd_tt": central_root,
                "lower_band_root_jd_tt": lower_jd,
                "upper_band_root_jd_tt": upper_jd,
                "nearest_noon_jd": nearest_jd,
                "nearest_noon_calendar_day": calendar_day,
                "nearest_noon_time": transit_time,
                "nearest_noon_altitude_deg": nearest_altitude,
                "nearest_noon_residual_deg": residual,
                "nearest_noon_within_band": within_band,
            }

            rows.append(row)

            print(f"\nCorrespondence {i}")
            print(f"  Central root JD: {central_root:.6f}")
            print(f"  Lower-band root JD: {lower_jd}")
            print(f"  Upper-band root JD: {upper_jd}")
            print(f"  Nearest daily solar noon: {calendar_day} {transit_time}")
            print(f"  Noon altitude: {nearest_altitude:.6f} deg")
            print(f"  Residual: {residual:+.6f} deg")
            print(
                f"  Within +/-{ALTITUDE_BAND_DEG:.3f} deg band: {within_band}"
            )

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} result rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
