#!/usr/bin/env python3

"""
Historical stellar-alignment search for the Great Pyramid shafts.

The script searches four independent historical cases:

1. 22 November 2550 BCE
   King's Chamber southern shaft
   Target inclination: 45.0000 degrees
   Target azimuth:     180.0000 degrees
   Expected target:    Orion's Belt

2. 11 December 2550 BCE
   Queen's Chamber southern shaft
   Target inclination: 39.6078 degrees
   Target azimuth:     180.0000 degrees
   Expected target:    Sirius

3. 2 March 2549 BCE
   King's Chamber southern shaft
   Target inclination: 45.0000 degrees
   Target azimuth:     180.0000 degrees
   Search mode:        open catalogue search (Hipparcos)

4. 11 February 2549 BCE
   Queen's Chamber southern shaft
   Target inclination: 39.6078 degrees
   Target azimuth:     180.0000 degrees
   Search mode:        open catalogue search (Hipparcos)

The search interval for every case is:
    23:00 through 01:00 LOCAL MEAN SOLAR TIME AT GIZA, around midnight.

Coordinate conventions:
    Latitude:   north positive
    Longitude:  east positive
    Azimuth:    0 = north, 90 = east, 180 = south, 270 = west
    Altitude:   degrees above the geometric horizon

Historical year convention:
    astronomical year 0     = 1 BCE
    astronomical year -2549 = 2550 BCE
    astronomical year -2548 = 2549 BCE

Time convention:
    A Julian Date is a Greenwich-based continuous day count. The labeled
    calendar date's local midnight at Giza occurs LONGITUDE/360 days
    before 00:00 UT of that date, and the search window is centered on it.

Scientific scope:
    This is an idealized meridian-plane comparison. It does not use measured
    shaft azimuths, complete shaft centerlines, or ray tracing through the
    physical shafts.

Astrometric approximation:
    - catalogue coordinates with a per-star reference epoch
    - first-order proper motion
    - compact (IAU 1976-style) precession polynomials
    - Greenwich mean sidereal time -> local sidereal time
    - geometric altitude and azimuth
    - no nutation, aberration, parallax, radial-velocity propagation,
      or atmospheric refraction

For publication:
    Validate the precession routine against an independent package
    (Astropy/ERFA, SOFA, NOVAS, a long-term model such as Vondrak 2011,
    or Stellarium). The IAU 1976 polynomials degrade over ~4500 years.

Requirements for the open search:
    pip install astroquery
"""


from dataclasses import dataclass
import csv
import math
import os


# =====================================================================
# Global configuration
# =====================================================================

# Giza geographic location
GIZA_LATITUDE_DEG = 29.9792
GIZA_LONGITUDE_DEG_EAST = 31.1342

# Idealized due-south shaft azimuth
SHAFT_AZIMUTH_DEG = 180.0000

# Shaft inclinations
KINGS_SHAFT_ALTITUDE_DEG = 45.0000
QUEENS_SHAFT_ALTITUDE_DEG = 39.6078

# Midnight search interval, in hours relative to LOCAL midnight at Giza
#     -1 hour = 23:00 on the preceding labeled date
#      0 hour = 00:00 on the labeled date
#     +1 hour = 01:00 on the labeled date
SEARCH_START_HOURS = -1.0
SEARCH_END_HOURS = +1.0

# Time step used for the search
SEARCH_STEP_MINUTES = 1.0

# Threshold used for open-search reporting
OPEN_SEARCH_THRESHOLD_DEG = 1.0

# Open-search catalogue: all Hipparcos stars brighter than this V magnitude
HIPPARCOS_VMAG_LIMIT = 2.5

# Reference epoch of Hipparcos positions (Julian year)
HIPPARCOS_EPOCH_JYEAR = 1991.25

# Printout limits (the threshold list always covers every star)
MAX_RANKED_PRINT = 30
MAX_DETAILED_PRINT = 10


# =====================================================================
# Star catalogue data structure
# =====================================================================

@dataclass
class Star:
    """
    Stellar astrometric input.

    ra_deg, dec_deg:
        Position in degrees at the catalogue reference epoch.

    pm_ra_cosdec_mas_yr:
        Proper motion in RA multiplied by cos(dec), in mas/yr.

    pm_dec_mas_yr:
        Proper motion in declination, in mas/yr.

    vmag:
        Visual magnitude (optional).

    epoch_jyear:
        Reference epoch of the position, in Julian years.
        2000.0 for J2000-like entries, 1991.25 for Hipparcos.
    """
    name: str
    ra_deg: float
    dec_deg: float
    pm_ra_cosdec_mas_yr: float
    pm_dec_mas_yr: float
    vmag: float = None
    epoch_jyear: float = 2000.0


# =====================================================================
# Preliminary bright-star list (used for the two predefined-target tests)
# =====================================================================

# Approximate J2000-like values. For a paper, replace these with a
# documented catalogue export (see load_hipparcos_stars below).

STARS = [
    # Orion's Belt
    Star(
        name="Alnitak (zeta Orionis)",
        ra_deg=85.1897,
        dec_deg=-1.9426,
        pm_ra_cosdec_mas_yr=3.99,
        pm_dec_mas_yr=2.54,
    ),
    Star(
        name="Alnilam (epsilon Orionis)",
        ra_deg=84.0534,
        dec_deg=-1.2019,
        pm_ra_cosdec_mas_yr=1.49,
        pm_dec_mas_yr=-1.06,
    ),
    Star(
        name="Mintaka (delta Orionis)",
        ra_deg=83.0017,
        dec_deg=-0.2991,
        pm_ra_cosdec_mas_yr=1.67,
        pm_dec_mas_yr=0.56,
    ),

    # Orion and nearby bright stars
    Star(
        name="Betelgeuse (alpha Orionis)",
        ra_deg=88.7929,
        dec_deg=7.4071,
        pm_ra_cosdec_mas_yr=27.54,
        pm_dec_mas_yr=10.86,
    ),
    Star(
        name="Rigel (beta Orionis)",
        ra_deg=78.6345,
        dec_deg=-8.2016,
        pm_ra_cosdec_mas_yr=1.87,
        pm_dec_mas_yr=-0.56,
    ),
    Star(
        name="Saiph (kappa Orionis)",
        ra_deg=86.9391,
        dec_deg=-9.6696,
        pm_ra_cosdec_mas_yr=1.55,
        pm_dec_mas_yr=-0.77,
    ),

    # Sirius and other bright comparison stars
    Star(
        name="Sirius (alpha Canis Majoris)",
        ra_deg=101.2872,
        dec_deg=-16.7161,
        pm_ra_cosdec_mas_yr=-546.01,
        pm_dec_mas_yr=-1223.07,
    ),
    Star(
        name="Canopus (alpha Carinae)",
        ra_deg=95.9879,
        dec_deg=-52.6957,
        pm_ra_cosdec_mas_yr=19.99,
        pm_dec_mas_yr=23.67,
    ),
    Star(
        name="Procyon (alpha Canis Minoris)",
        ra_deg=114.8255,
        dec_deg=5.2249,
        pm_ra_cosdec_mas_yr=-714.59,
        pm_dec_mas_yr=-1036.80,
    ),
    Star(
        name="Regulus (alpha Leonis)",
        ra_deg=152.0929,
        dec_deg=11.9672,
        pm_ra_cosdec_mas_yr=-249.40,
        pm_dec_mas_yr=5.59,
    ),
    Star(
        name="Pollux (beta Geminorum)",
        ra_deg=116.3289,
        dec_deg=28.0262,
        pm_ra_cosdec_mas_yr=-625.69,
        pm_dec_mas_yr=-45.95,
    ),
]


# =====================================================================
# Hipparcos catalogue loader (open search)
# =====================================================================

def load_hipparcos_stars(vmag_limit=HIPPARCOS_VMAG_LIMIT, cache_dir="."):
    """
    Load all Hipparcos stars brighter than vmag_limit
    (VizieR catalogue I/239/hip_main).

    The first run downloads the data and saves a CSV next to the script;
    later runs reuse that file, so the star list is reproducible and can
    be cited in the paper.
    """
    columns = ["HIP", "RAICRS", "DEICRS", "pmRA", "pmDE", "Vmag"]
    cache_path = os.path.join(
        cache_dir,
        f"hipparcos_vmag_lt_{vmag_limit}.csv",
    )

    if not os.path.exists(cache_path):
        try:
            import numpy as np
            from astroquery.vizier import Vizier
        except ImportError as error:
            raise RuntimeError(
                "astroquery is required to download the catalogue: "
                "pip install astroquery"
            ) from error

        vizier = Vizier(
            columns=columns,
            column_filters={"Vmag": f"<{vmag_limit}"},
            row_limit=-1,
        )
        tables = vizier.get_catalogs("I/239/hip_main")
        table = tables[0]

        with open(cache_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)

            for row in table:
                values = [row[c] for c in columns]

                # Skip stars lacking position or proper motion
                if any(np.ma.is_masked(v) for v in values):
                    continue

                writer.writerow([float(v) for v in values])

    stars = []

    with open(cache_path, newline="") as f:
        for row in csv.DictReader(f):
            stars.append(
                Star(
                    name=f"HIP {int(float(row['HIP']))}",
                    ra_deg=float(row["RAICRS"]),
                    dec_deg=float(row["DEICRS"]),
                    pm_ra_cosdec_mas_yr=float(row["pmRA"]),
                    pm_dec_mas_yr=float(row["pmDE"]),
                    vmag=float(row["Vmag"]),
                    epoch_jyear=HIPPARCOS_EPOCH_JYEAR,
                )
            )

    print(
        f"Loaded {len(stars)} Hipparcos stars "
        f"with V < {vmag_limit} from {cache_path}"
    )

    return stars

# =====================================================================
# Angle utilities
# =====================================================================

def deg_to_rad(value):
    return math.radians(value)


def rad_to_deg(value):
    return math.degrees(value)


def normalize_degrees(value):
    return value % 360.0


def signed_angular_difference_deg(a, b):
    """
    Return a - b normalized to [-180, +180) degrees.
    """
    return (a - b + 180.0) % 360.0 - 180.0


# =====================================================================
# Julian Date and historical year conversion
# =====================================================================

def julian_day_from_astronomical_year(
    astronomical_year,
    month,
    day,
    hour=0.0,
):
    """
    Julian Date (Greenwich-based, UT) for a proleptic Julian-calendar
    date using astronomical year numbering.

    Examples:
        astronomical year 0     = 1 BCE
        astronomical year -2549 = 2550 BCE
        astronomical year -2548 = 2549 BCE
    """
    y = astronomical_year
    m = month
    d = day + hour / 24.0

    if m <= 2:
        y -= 1
        m += 12

    # Proleptic Julian calendar: no Gregorian correction term.
    jd = (
        math.floor(365.25 * (y + 4716))
        + math.floor(30.6001 * (m + 1))
        + d
        - 1524.5
    )

    return float(jd)


def julian_years_from_j2000(jd):
    return (jd - 2451545.0) / 365.25


def julian_centuries_from_j2000(jd):
    return (jd - 2451545.0) / 36525.0


# =====================================================================
# Proper motion and historical precession
# =====================================================================

def propagate_proper_motion(star, jd):
    """
    First-order proper-motion propagation from the star's own reference
    epoch (J2000 for manual entries, J1991.25 for Hipparcos) to jd.

    pm_ra_cosdec is mu_alpha*cos(delta), so the RA displacement is
    divided by cos(delta).
    """
    years = (
        julian_years_from_j2000(jd)
        - (star.epoch_jyear - 2000.0)
    )

    dec0_rad = deg_to_rad(star.dec_deg)
    cos_dec = math.cos(dec0_rad)

    if abs(cos_dec) < 1.0e-12:
        raise ValueError(
            "Declination is too close to a pole for this calculation."
        )

    delta_ra_deg = (
        star.pm_ra_cosdec_mas_yr
        * years
        / cos_dec
        / 3_600_000.0
    )

    delta_dec_deg = (
        star.pm_dec_mas_yr
        * years
        / 3_600_000.0
    )

    ra_deg = normalize_degrees(star.ra_deg + delta_ra_deg)
    dec_deg = star.dec_deg + delta_dec_deg

    return ra_deg, dec_deg


def precess_j2000_to_date(ra_deg, dec_deg, jd):
    """
    Compact IAU-style precession approximation.

    Input:  J2000-like equatorial RA/Dec in degrees.
    Output: approximate mean-of-date RA/Dec in degrees.

    Note: Hipparcos (ICRS) positions are treated as J2000 here after the
    proper-motion step has moved them from J1991.25 to the target date.
    The ICRS-to-J2000 frame offset (~20 mas) is negligible for this use.
    """
    t = julian_centuries_from_j2000(jd)

    zeta_arcsec = (
        2306.2181 * t
        + 0.30188 * t * t
        + 0.017998 * t * t * t
    )

    z_arcsec = (
        2306.2181 * t
        + 1.09468 * t * t
        + 0.018203 * t * t * t
    )

    theta_arcsec = (
        2004.3109 * t
        - 0.42665 * t * t
        - 0.041833 * t * t * t
    )

    zeta = deg_to_rad(zeta_arcsec / 3600.0)
    z = deg_to_rad(z_arcsec / 3600.0)
    theta = deg_to_rad(theta_arcsec / 3600.0)

    alpha = deg_to_rad(ra_deg)
    delta = deg_to_rad(dec_deg)

    a = math.cos(delta) * math.sin(alpha + zeta)

    b = (
        math.cos(theta) * math.cos(delta) * math.cos(alpha + zeta)
        - math.sin(theta) * math.sin(delta)
    )

    c = (
        math.sin(theta) * math.cos(delta) * math.cos(alpha + zeta)
        + math.cos(theta) * math.sin(delta)
    )

    ra_new = math.atan2(a, b) + z
    dec_new = math.asin(max(-1.0, min(1.0, c)))

    return (
        normalize_degrees(rad_to_deg(ra_new)),
        rad_to_deg(dec_new),
    )


def historical_star_position(star, jd):
    """
    Apply:
        1. first-order proper motion from the catalogue epoch
        2. precession from J2000 to the target date
    """
    ra_pm_deg, dec_pm_deg = propagate_proper_motion(star, jd)

    return precess_j2000_to_date(ra_pm_deg, dec_pm_deg, jd)


# =====================================================================
# Sidereal time and horizontal coordinates
# =====================================================================

def greenwich_mean_sidereal_time_deg(jd):
    """
    Greenwich Mean Sidereal Time in degrees.
    """
    t = julian_centuries_from_j2000(jd)

    gmst = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * t * t
        - (t * t * t) / 38_710_000.0
    )

    return normalize_degrees(gmst)


def local_sidereal_time_deg(jd):
    """
    Local Mean Sidereal Time.

    Longitude is positive east.
    """
    return normalize_degrees(
        greenwich_mean_sidereal_time_deg(jd)
        + GIZA_LONGITUDE_DEG_EAST
    )


def equatorial_to_altaz(ra_deg, dec_deg, jd):
    """
    Convert RA/Dec to geometric altitude and azimuth.

    Azimuth convention:
        0 degrees   = north
        90 degrees  = east
        180 degrees = south
        270 degrees = west
    """
    lst_deg = local_sidereal_time_deg(jd)

    hour_angle_deg = signed_angular_difference_deg(
        lst_deg,
        ra_deg,
    )

    phi = deg_to_rad(GIZA_LATITUDE_DEG)
    hour_angle = deg_to_rad(hour_angle_deg)
    dec = deg_to_rad(dec_deg)

    sin_altitude = (
        math.sin(phi) * math.sin(dec)
        + math.cos(phi) * math.cos(dec) * math.cos(hour_angle)
    )

    sin_altitude = max(-1.0, min(1.0, sin_altitude))

    altitude_deg = rad_to_deg(math.asin(sin_altitude))

    # Azimuth measured from north through east.
    # (Corrected: the denominator sign was reversed in the earlier version,
    # which put due-south meridian stars at azimuth 0 instead of 180.)
    azimuth_rad = math.atan2(
        -math.sin(hour_angle),
        (
            math.tan(dec) * math.cos(phi)
            - math.cos(hour_angle) * math.sin(phi)
        ),
    )

    azimuth_deg = normalize_degrees(rad_to_deg(azimuth_rad))

    return (
        altitude_deg,
        azimuth_deg,
        hour_angle_deg,
    )


# =====================================================================
# Local vector geometry
# =====================================================================

def horizontal_unit_vector(altitude_deg, azimuth_deg):
    """
    Convert altitude/azimuth to a local Cartesian unit vector.

    x = east, y = north, z = zenith
    """
    altitude = deg_to_rad(altitude_deg)
    azimuth = deg_to_rad(azimuth_deg)

    x_east = math.cos(altitude) * math.sin(azimuth)
    y_north = math.cos(altitude) * math.cos(azimuth)
    z_up = math.sin(altitude)

    return (x_east, y_north, z_up)


def angular_separation_deg(
    altitude_1_deg,
    azimuth_1_deg,
    altitude_2_deg,
    azimuth_2_deg,
):
    """
    Angular separation between two local horizon directions.
    """
    vector_1 = horizontal_unit_vector(altitude_1_deg, azimuth_1_deg)
    vector_2 = horizontal_unit_vector(altitude_2_deg, azimuth_2_deg)

    dot_product = sum(a * b for a, b in zip(vector_1, vector_2))
    dot_product = max(-1.0, min(1.0, dot_product))

    return rad_to_deg(math.acos(dot_product))


# =====================================================================
# Star evaluation
# =====================================================================

def evaluate_star(star, jd, shaft_altitude_deg):
    """
    Evaluate one star at one Julian Date.
    """
    ra_deg, dec_deg = historical_star_position(star, jd)

    altitude_deg, azimuth_deg, hour_angle_deg = equatorial_to_altaz(
        ra_deg,
        dec_deg,
        jd,
    )

    altitude_residual_deg = altitude_deg - shaft_altitude_deg

    azimuth_residual_deg = signed_angular_difference_deg(
        azimuth_deg,
        SHAFT_AZIMUTH_DEG,
    )

    separation_deg = angular_separation_deg(
        altitude_deg,
        azimuth_deg,
        shaft_altitude_deg,
        SHAFT_AZIMUTH_DEG,
    )

    return {
        "star": star.name,
        "vmag": star.vmag,
        "jd": jd,
        "ra_deg": ra_deg,
        "dec_deg": dec_deg,
        "altitude_deg": altitude_deg,
        "azimuth_deg": azimuth_deg,
        "hour_angle_deg": hour_angle_deg,
        "altitude_residual_deg": altitude_residual_deg,
        "azimuth_residual_deg": azimuth_residual_deg,
        "separation_deg": separation_deg,
    }


# =====================================================================
# Search functions
# =====================================================================

def search_window_bounds(center_jd):
    """
    Return the Julian Date bounds of the search window around local
    midnight (23:00-01:00 with the default configuration).
    """
    start_jd = center_jd + SEARCH_START_HOURS / 24.0
    end_jd = center_jd + SEARCH_END_HOURS / 24.0

    return start_jd, end_jd


def find_best_full_direction_match(star, center_jd, shaft_altitude_deg):
    """
    Search the window and minimize the full angular separation from the
    idealized shaft direction:
        altitude = shaft_altitude_deg
        azimuth  = 180 degrees
    """
    start_jd, end_jd = search_window_bounds(center_jd)
    step_days = SEARCH_STEP_MINUTES / 1440.0

    best = None
    jd = start_jd

    while jd <= end_jd + 1.0e-12:
        result = evaluate_star(star, jd, shaft_altitude_deg)

        if best is None or result["separation_deg"] < best["separation_deg"]:
            best = result

        jd += step_days

    return best


def find_closest_meridian_position(star, center_jd, shaft_altitude_deg):
    """
    Search the same window and minimize the absolute hour angle. This
    identifies the closest upper-meridian position in the window.
    """
    start_jd, end_jd = search_window_bounds(center_jd)
    step_days = SEARCH_STEP_MINUTES / 1440.0

    best = None
    best_score = None
    jd = start_jd

    while jd <= end_jd + 1.0e-12:
        result = evaluate_star(star, jd, shaft_altitude_deg)

        score = abs(result["hour_angle_deg"])

        if best is None or score < best_score:
            best = result
            best_score = score

        jd += step_days

    return best


# =====================================================================
# Formatting and reporting
# =====================================================================

def format_offset_from_midnight(jd, center_jd):
    """
    Return signed hours relative to local midnight at Giza.
    """
    hours = (jd - center_jd) * 24.0

    if hours < 0.0:
        return f"{abs(hours):.4f} h before midnight"

    if hours > 0.0:
        return f"{hours:.4f} h after midnight"

    return "exactly at midnight"


def format_vmag(vmag):
    if vmag is None:
        return ""

    return f" (V={vmag:.2f})"


def print_result(title, result, center_jd):
    print()
    print(title)
    print(
        f"  Time offset:          "
        f"{format_offset_from_midnight(result['jd'], center_jd)}"
    )
    print(f"  Julian Date (UT):     {result['jd']:.8f}")
    print(f"  Historical RA:        {result['ra_deg']:.8f} deg")
    print(f"  Historical Dec:       {result['dec_deg']:.8f} deg")
    print(f"  Altitude:             {result['altitude_deg']:.8f} deg")
    print(f"  Azimuth:              {result['azimuth_deg']:.8f} deg")
    print(f"  Hour angle:           {result['hour_angle_deg']:.8f} deg")
    print(f"  Altitude residual:    {result['altitude_residual_deg']:+.8f} deg")
    print(f"  Azimuth residual:     {result['azimuth_residual_deg']:+.8f} deg")
    print(f"  3D separation:        {result['separation_deg']:.8f} deg")


def print_candidates_within_threshold(
    results,
    center_jd,
    threshold_deg=OPEN_SEARCH_THRESHOLD_DEG,
):
    """
    Print ALL stars within the selected full-direction threshold.
    """
    print()
    print(
        f"Stars within {threshold_deg:.3f} degrees "
        "of the idealized shaft direction:"
    )

    found = False

    for rank, item in enumerate(results, start=1):
        result = item["midnight"]

        if result["separation_deg"] <= threshold_deg:
            found = True

            print(
                f"  {rank:03d}. "
                f"{result['star']}{format_vmag(result['vmag'])}: "
                f"{result['separation_deg']:.6f} deg, "
                f"{format_offset_from_midnight(result['jd'], center_jd)}"
            )

    if not found:
        print("  None")


# =====================================================================
# Case runner
# =====================================================================

def run_case(
    case_name,
    calendar_label,
    astronomical_year,
    month,
    day,
    shaft_altitude_deg,
    stars,
    expected_target=None,
    open_search=False,
):
    """
    Run one date/shaft case.

    The labeled date's 00:00 LOCAL MEAN SOLAR TIME at Giza is the center
    of the search window. The script then searches from 23:00 to 01:00
    around that local midnight.
    """
    # 00:00 UT (Greenwich midnight) of the labeled date
    midnight_ut_jd = julian_day_from_astronomical_year(
        astronomical_year,
        month,
        day,
        hour=0.0,
    )

    # Shift to local mean solar midnight at Giza. Giza is east of
    # Greenwich, so its midnight occurs earlier on the UT scale.
    center_jd = midnight_ut_jd - GIZA_LONGITUDE_DEG_EAST / 360.0

    print()
    print("=" * 80)
    print(case_name)
    print("=" * 80)
    print(f"Calendar label:              {calendar_label}")
    print(f"Internal astronomical year:  {astronomical_year}")
    print("Search interval:             23:00 to 01:00 local time at Giza")
    print(f"Target shaft altitude:       {shaft_altitude_deg:.4f} deg")
    print(f"Target shaft azimuth:        {SHAFT_AZIMUTH_DEG:.4f} deg")
    print(f"Stars searched:              {len(stars)}")

    if expected_target is None:
        print("Expected target:             none imposed")
    else:
        print(f"Expected target:             {expected_target}")

    if open_search:
        print("Search mode:                 open catalogue search")
    else:
        print("Search mode:                 predefined-target test")

    print()
    print(
        "The 180-degree azimuth is an idealized "
        "due-south assumption, not a measured shaft azimuth."
    )

    results = []

    for star in stars:
        midnight_match = find_best_full_direction_match(
            star,
            center_jd,
            shaft_altitude_deg,
        )

        meridian_match = find_closest_meridian_position(
            star,
            center_jd,
            shaft_altitude_deg,
        )

        results.append(
            {
                "star": star,
                "midnight": midnight_match,
                "meridian": meridian_match,
            }
        )

    # Rank by closest full-direction match.
    results.sort(key=lambda item: item["midnight"]["separation_deg"])

    print()
    print(
        f"RANKED FULL-DIRECTION RESULTS "
        f"(top {min(MAX_RANKED_PRINT, len(results))} of {len(results)})"
    )
    print("-" * 80)

    for rank, item in enumerate(results[:MAX_RANKED_PRINT], start=1):
        result = item["midnight"]

        print(
            f"{rank:02d}. "
            f"{result['star']}{format_vmag(result['vmag'])}: "
            f"separation={result['separation_deg']:.6f} deg, "
            f"alt_residual={result['altitude_residual_deg']:+.6f} deg, "
            f"az_residual={result['azimuth_residual_deg']:+.6f} deg, "
            f"time={format_offset_from_midnight(result['jd'], center_jd)}"
        )

    if open_search:
        print_candidates_within_threshold(
            results,
            center_jd,
            OPEN_SEARCH_THRESHOLD_DEG,
        )

    print()
    print(
        f"DETAILED RESULTS (top {min(MAX_DETAILED_PRINT, len(results))})"
    )
    print("-" * 80)

    for item in results[:MAX_DETAILED_PRINT]:
        print()
        print(item["star"].name + format_vmag(item["star"].vmag))

        print_result(
            "Best full-direction match in 23:00-01:00:",
            item["midnight"],
            center_jd,
        )

        print_result(
            "Closest meridian position in 23:00-01:00:",
            item["meridian"],
            center_jd,
        )


# =====================================================================
# Main program
# =====================================================================

def main():
    # Open-search catalogue (downloaded once, then cached as CSV)
    try:
        catalogue = load_hipparcos_stars(HIPPARCOS_VMAG_LIMIT)
    except Exception as error:
        print(f"WARNING: could not load the Hipparcos catalogue: {error}")
        print("Falling back to the small manual STARS list for open searches.")
        catalogue = STARS

    # ---------------------------------------------------------------
    # 1. 22 November 2550 BCE, King's Chamber, Orion's Belt test
    # ---------------------------------------------------------------

    run_case(
        case_name="King's Chamber south shaft - Orion's Belt test",
        calendar_label="22 November 2550 BCE",
        astronomical_year=-2549,
        month=11,
        day=22,
        shaft_altitude_deg=KINGS_SHAFT_ALTITUDE_DEG,
        stars=[
            STARS[0],  # Alnitak
            STARS[1],  # Alnilam
            STARS[2],  # Mintaka
        ],
        expected_target="Orion's Belt",
        open_search=False,
    )

    # ---------------------------------------------------------------
    # 2. 11 December 2550 BCE, Queen's Chamber, Sirius test
    # ---------------------------------------------------------------

    run_case(
        case_name="Queen's Chamber south shaft - Sirius test",
        calendar_label="11 December 2550 BCE",
        astronomical_year=-2549,
        month=12,
        day=11,
        shaft_altitude_deg=QUEENS_SHAFT_ALTITUDE_DEG,
        stars=[
            next(
                star
                for star in STARS
                if star.name.startswith("Sirius")
            )
        ],
        expected_target="Sirius",
        open_search=False,
    )

    # ---------------------------------------------------------------
    # 3. 2 March 2549 BCE, King's Chamber, open search
    # ---------------------------------------------------------------

    run_case(
        case_name="King's Chamber south shaft - open stellar search",
        calendar_label="2 March 2549 BCE",
        astronomical_year=-2548,
        month=3,
        day=2,
        shaft_altitude_deg=KINGS_SHAFT_ALTITUDE_DEG,
        stars=catalogue,
        expected_target=None,
        open_search=True,
    )

    # ---------------------------------------------------------------
    # 4. 11 February 2549 BCE, Queen's Chamber, open search
    # ---------------------------------------------------------------

    run_case(
        case_name="Queen's Chamber south shaft - open stellar search",
        calendar_label="11 February 2549 BCE",
        astronomical_year=-2548,
        month=2,
        day=11,
        shaft_altitude_deg=QUEENS_SHAFT_ALTITUDE_DEG,
        stars=catalogue,
        expected_target=None,
        open_search=True,
    )

    # ---------------------------------------------------------------
    # 5. 22 November 2550 BCE, King's Chamber, open search (extra)
    # ---------------------------------------------------------------

    run_case(
        case_name="King's Chamber south shaft - open stellar search (Nov)",
        calendar_label="22 November 2550 BCE",
        astronomical_year=-2549,
        month=11,
        day=22,
        shaft_altitude_deg=KINGS_SHAFT_ALTITUDE_DEG,
        stars=catalogue,
        expected_target=None,
        open_search=True,
    )

    # ---------------------------------------------------------------
    # 6. 11 December 2550 BCE, Queen's Chamber, open search (extra)
    # ---------------------------------------------------------------

    run_case(
        case_name="Queen's Chamber south shaft - open stellar search (Dec)",
        calendar_label="11 December 2550 BCE",
        astronomical_year=-2549,
        month=12,
        day=11,
        shaft_altitude_deg=QUEENS_SHAFT_ALTITUDE_DEG,
        stars=catalogue,
        expected_target=None,
        open_search=True,
    )

if __name__ == "__main__":
    main()
