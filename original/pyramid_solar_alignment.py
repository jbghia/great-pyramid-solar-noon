#!/usr/bin/env python3
"""
Solar-noon altitude correspondences and angular-sensitivity windows
for the south-directed shafts of the Great Pyramid.

Ephemeris:
    JPL DE422 via Skyfield. DE422 covers astronomical years -3000 to
    +3000, including the late 26th century BCE interval examined here.

Calendar labels:
    Proleptic Julian calendar using astronomical year numbering.
    Astronomical year -2549 = 2550 BCE.
    Astronomical year -2548 = 2549 BCE.

Time scales:
    TT  Terrestrial Time: uniform dynamical time used for ephemeris
        positions.
    UT  Universal Time: rotation-based time used for the calendar day
        and clock time of local solar noon.

    TT = UT + Delta-T. For the 26th century BCE, Delta-T is roughly
    17 hours, with an uncertainty of at least about an hour.

Reported quantities:
    1. Root: instant when the Sun's apparent declination equals the
       declination required for a shaft inclination.
    2. Solar noon: instant the Sun crosses the Giza meridian on each
       neighbouring UT calendar day, and its altitude then.

Scope:
    Meridian-plane comparison only. No shaft azimuths or 3-D ray paths.
"""


import math

from skyfield.api import load



# ---------------------------------------------------------------------
# Adopted inputs
# ---------------------------------------------------------------------


EPHEMERIS_FILE = "de422.bsp"

PHI_GIZA = 29.9792
LAMBDA_GIZA_EAST = 31.1342


TARGETS = {
    "King's Chamber southern shaft": 45.0000,
    "Queen's Chamber southern shaft": 39.6078,
}


TOL_ALT = 0.2
ROOT_TOL = 1e-8

DELTA_T_OVERRIDE_SECONDS = None

NEIGHBOUR_DAYS = (-1, 0, 1)



# ---------------------------------------------------------------------
# Load ephemeris and time scale
# ---------------------------------------------------------------------


print(f"Loading ephemeris: {EPHEMERIS_FILE}")
eph = load(EPHEMERIS_FILE)
ts = load.timescale()

EARTH = eph["earth"]
SUN = eph["sun"]



# ---------------------------------------------------------------------
# Solar position
# ---------------------------------------------------------------------


def solar_declination_deg(jd_tt):
    """
    Apparent geocentric equatorial declination of the Sun, degrees.

    Skyfield applies the relevant light-time, aberration, precession,
    nutation, and frame transformations when `apparent()` and
    `radec(epoch='date')` are used.
    """
    t = ts.tt_jd(jd_tt)

    apparent = (EARTH + SUN).at(t).apparent()
    _, declination, _ = apparent.radec(epoch="date")

    return declination.degrees


def meridian_altitude_deg(jd_tt):
    """
    Geometric solar-centre altitude at upper culmination, degrees.

        h = 90 degrees - |phi - delta|
    """
    delta = solar_declination_deg(jd_tt)
    return 90.0 - abs(PHI_GIZA - delta)


def required_declination_deg(target_altitude):
    """
    Required solar declination for a target shaft inclination.
    """
    return target_altitude + PHI_GIZA - 90.0



# ---------------------------------------------------------------------
# Delta-T, equation of time, and solar noon
# ---------------------------------------------------------------------


def decimal_year_from_jd(jd):
    return 2000.0 + (jd - 2451545.0) / 365.25


def delta_t_seconds(jd):
    """
    Delta-T = TT - UT, seconds.

    Uses DELTA_T_OVERRIDE_SECONDS if set; otherwise the Morrison &
    Stephenson (2004) parabola:
        Delta-T = -20 + 32 u^2 seconds,
        u = (year - 1820) / 100.
    """
    if DELTA_T_OVERRIDE_SECONDS is not None:
        return DELTA_T_OVERRIDE_SECONDS

    u = (decimal_year_from_jd(jd) - 1820.0) / 100.0
    return -20.0 + 32.0 * u * u


def ut_to_tt(jd_ut):
    return jd_ut + delta_t_seconds(jd_ut) / 86400.0


def tt_to_ut(jd_tt):
    # Delta-T varies slowly; evaluating it at TT is sufficiently
    # accurate for this application.
    return jd_tt - delta_t_seconds(jd_tt) / 86400.0


def equation_of_time_minutes(jd_tt):
    """
    Equation of time in minutes: apparent minus mean solar time.

    Uses Skyfield's apparent solar right ascension and the mean Sun's
    right ascension.
    """
    t = ts.tt_jd(jd_tt)

    apparent = (EARTH + SUN).at(t).apparent()
    ra_sun, _, _ = apparent.radec(epoch="date")
    alpha_sun_deg = ra_sun.degrees

    # Mean longitude of the Sun, degrees.
    T = (jd_tt - 2451545.0) / 36525.0
    L0 = (
        280.46646
        + 36000.76983 * T
        + 0.0003032 * T * T
    ) % 360.0

    # Equation of the centre is not separately needed here because the
    # apparent right ascension already incorporates it.
    e_deg = (L0 - 0.0057183 - alpha_sun_deg + 180.0) % 360.0 - 180.0

    return 4.0 * e_deg


def solar_noon_jd_ut(jd_ut_midnight):
    """
    Julian Date (UT) of local apparent solar noon at Giza on the UT 
    calendar day beginning at jd_ut_midnight.

    Apparent noon occurs when the Sun crosses the Giza meridian:

        local apparent solar time = 12:00

    The equation of time depends on the instant, so iterate to convergence.
    """
    jd_ut = jd_ut_midnight + 0.5 - LAMBDA_GIZA_EAST / 360.0

    for _ in range(8):
        e_minutes = equation_of_time_minutes(ut_to_tt(jd_ut))
        jd_ut = (
            jd_ut_midnight
            + 0.5
            - LAMBDA_GIZA_EAST / 360.0
            - e_minutes / 1440.0
        )

    return jd_ut


def noon_altitude_deg(jd_ut_noon):
    return meridian_altitude_deg(ut_to_tt(jd_ut_noon))



# ---------------------------------------------------------------------
# Proleptic Julian calendar conversion
# ---------------------------------------------------------------------


def julian_calendar_to_jd(year, month, day=1.0):
    y = year
    m = month

    if m <= 2:
        y -= 1
        m += 12

    return (
        math.floor(365.25 * (y + 4716))
        + math.floor(30.6001 * (m + 1))
        + day
        - 1524.5
    )


def jd_to_julian_calendar(jd):
    x = jd + 0.5
    Z = math.floor(x)
    F = x - Z

    C = Z + 1524
    D = math.floor((C - 122.1) / 365.25)
    E = math.floor(365.25 * D)
    G = math.floor((C - E) / 30.6001)

    day = C - E - math.floor(30.6001 * G) + F
    month = G - 1 if G < 13.5 else G - 13
    year = D - 4716 if month > 2.5 else D - 4715

    return year, month, day


def jd_of_jan1_0(year):
    return julian_calendar_to_jd(year, 1, 1.0)



# ---------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------


MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def bce_ce_label(year):
    if year <= 0:
        return f"{1 - year} BCE"
    return f"{year} CE"


def format_date(jd):
    year, month, day = jd_to_julian_calendar(jd)
    return f"{int(day):02d} {MONTH_NAMES[month - 1]} {bce_ce_label(year)}"


def format_clock(fraction_of_day):
    total_seconds = int(round((fraction_of_day % 1.0) * 86400.0))

    if total_seconds >= 86400:
        total_seconds -= 86400

    hour = total_seconds // 3600
    minute = (total_seconds % 3600) // 60
    second = total_seconds % 60

    return f"{hour:02d}:{minute:02d}:{second:02d}"


def format_date_time(jd, scale="TT"):
    year, month, day = jd_to_julian_calendar(jd)
    day_integer = int(day)
    fraction = day - day_integer

    return (
        f"{day_integer:02d} {MONTH_NAMES[month - 1]} "
        f"{bce_ce_label(year)} "
        f"{format_clock(fraction)} {scale}"
    )



# ---------------------------------------------------------------------
# Root finding
# ---------------------------------------------------------------------


def search_bounds():
    """
    Search late astronomical year -2549 through early year -2548.
    """
    start = jd_of_jan1_0(-2549) + 300.0
    end = jd_of_jan1_0(-2548) + 75.0
    return start, end


def bisect_root(a, b, target_altitude):
    fa = meridian_altitude_deg(a) - target_altitude
    fb = meridian_altitude_deg(b) - target_altitude

    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if fa * fb > 0.0:
        raise ValueError("Root is not bracketed.")

    for _ in range(100):
        midpoint = 0.5 * (a + b)
        fm = meridian_altitude_deg(midpoint) - target_altitude

        if abs(fm) < ROOT_TOL or (b - a) < 1e-10:
            return midpoint

        if fa * fm <= 0.0:
            b = midpoint
            fb = fm
        else:
            a = midpoint
            fa = fm

    return 0.5 * (a + b)


def all_roots(target_altitude, start, end, step=1.0):
    roots = []

    a = start
    fa = meridian_altitude_deg(a) - target_altitude

    while a < end:
        b = min(a + step, end)
        fb = meridian_altitude_deg(b) - target_altitude

        if fa == 0.0 or fa * fb < 0.0:
            root = a if fa == 0.0 else bisect_root(a, b, target_altitude)

            if not roots or abs(root - roots[-1]) > 1e-7:
                roots.append(root)

        a = b
        fa = fb

    return roots


def paired_window_for_root(root, lower_roots, upper_roots):
    lower_near = min(lower_roots, key=lambda x: abs(x - root))
    upper_near = min(upper_roots, key=lambda x: abs(x - root))

    return min(lower_near, upper_near), max(lower_near, upper_near)



# ---------------------------------------------------------------------
# Solar-noon table
# ---------------------------------------------------------------------


def ut_day_start(jd_ut):
    return math.floor(jd_ut - 0.5) + 0.5


def noon_table_for_root(root_jd_tt, target_altitude):
    root_jd_ut = tt_to_ut(root_jd_tt)
    base_day = ut_day_start(root_jd_ut)

    rows = []

    for offset in NEIGHBOUR_DAYS:
        midnight = base_day + offset
        noon_ut = solar_noon_jd_ut(midnight)
        noon_tt = ut_to_tt(noon_ut)

        e_minutes = equation_of_time_minutes(noon_tt)
        altitude = noon_altitude_deg(noon_ut)

        local_mean_hours = 12.0 - e_minutes / 60.0

        rows.append(
            {
                "offset": offset,
                "noon_ut": noon_ut,
                "noon_tt": noon_tt,
                "eot_min": e_minutes,
                "local_mean_clock": format_clock(local_mean_hours / 24.0),
                "altitude": altitude,
                "residual": altitude - target_altitude,
            }
        )

    best_index = min(
        range(len(rows)),
        key=lambda i: abs(rows[i]["residual"]),
    )

    return rows, best_index



# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------


def run_self_tests():
    assert abs(julian_calendar_to_jd(2000, 1, 1.0) - 2451557.5) < 1e-9

    year, month, day = jd_to_julian_calendar(2451557.5)
    assert year == 2000
    assert month == 1
    assert abs(day - 1.0) < 1e-9

    assert abs(required_declination_deg(45.0000) - (-15.0208)) < 1e-9
    assert abs(required_declination_deg(39.6078) - (-20.4130)) < 1e-9

    # Modern-era equation-of-time sanity check.
    e_nov = equation_of_time_minutes(2451851.5)
    assert 15.5 < e_nov < 17.5, e_nov

    # Delta-T round trip.
    jd_test = 790400.0
    assert abs(tt_to_ut(ut_to_tt(jd_test)) - jd_test) < 1e-6

    # Solar declination sanity check near an equinox.
    delta = solar_declination_deg(2451545.0)
    assert -1.0 < delta < 1.0, delta



# ---------------------------------------------------------------------
# Main output
# ---------------------------------------------------------------------


def main():
    run_self_tests()

    start, end = search_bounds()

    print("Solar-noon altitude correspondences and sensitivity windows")
    print("Calendar labels: proleptic Julian calendar; astronomical year numbering")
    print(f"Ephemeris: JPL {EPHEMERIS_FILE} via Skyfield")
    print("Comparison: solar altitude at upper culmination versus shaft inclination")
    print("No shaft azimuth is assumed or evaluated.")
    print()
    print(f"Giza latitude:  {PHI_GIZA:.4f} deg N")
    print(f"Giza longitude: {LAMBDA_GIZA_EAST:.4f} deg E")
    print(f"Illustrative altitude sensitivity band: +/-{TOL_ALT:.3f} deg")
    print(f"Search interval: JD(TT) {start:.1f} to {end:.1f}")

    sample_jd = 0.5 * (start + end)
    delta_t = delta_t_seconds(sample_jd)

    print(
        f"Delta-T used (TT - UT) near these dates: "
        f"{delta_t:.0f} s ({delta_t / 3600.0:.2f} h)"
        + (
            "  [fixed override]"
            if DELTA_T_OVERRIDE_SECONDS is not None
            else "  [Morrison & Stephenson 2004 parabola]"
        )
    )
    print()

    for name, target in TARGETS.items():
        central_roots = all_roots(target, start, end)
        lower_roots = all_roots(target - TOL_ALT, start, end)
        upper_roots = all_roots(target + TOL_ALT, start, end)

        print(name)
        print(f"  Adopted inclination: {target:.4f} deg")
        print(
            "  Required declination: "
            f"{required_declination_deg(target):.4f} deg"
        )

        print("  Central roots:")
        for jd in central_roots:
            jd_ut = tt_to_ut(jd)

            print(
                f"    {format_date(jd)} (TT label) | "
                f"JD(TT) {jd:.6f} | "
                f"altitude {meridian_altitude_deg(jd):.6f} deg"
            )
            print(
                f"      same instant in UT: {format_date_time(jd_ut, 'UT')} | "
                f"JD(UT) {jd_ut:.6f}"
            )

        print("  Lower-altitude roots:")
        for jd in lower_roots:
            print(
                f"    {format_date(jd)} | "
                f"JD(TT) {jd:.6f} | "
                f"altitude {meridian_altitude_deg(jd):.6f} deg"
            )

        print("  Upper-altitude roots:")
        for jd in upper_roots:
            print(
                f"    {format_date(jd)} | "
                f"JD(TT) {jd:.6f} | "
                f"altitude {meridian_altitude_deg(jd):.6f} deg"
            )

        print("  Sensitivity windows:")
        for index, central_jd in enumerate(central_roots, start=1):
            window_start, window_end = paired_window_for_root(
                central_jd,
                lower_roots,
                upper_roots,
            )

            print(
                f"    Correspondence {index}: "
                f"{format_date(window_start)} to {format_date(window_end)}"
            )

        print()
        print("  EXACT SOLAR NOON on the calendar days around each root (UT days):")

        for index, central_jd in enumerate(central_roots, start=1):
            rows, best_index = noon_table_for_root(central_jd, target)

            print(f"    Correspondence {index}:")
            print(
                "      day (UT)            noon UT      "
                "local mean time   EoT (min)   JD(UT)           "
                "altitude (deg)   residual (deg)"
            )

            for i, row in enumerate(rows):
                marker = "  <-- closest" if i == best_index else ""
                inside = (
                    "  (within band)"
                    if abs(row["residual"]) <= TOL_ALT
                    else ""
                )

                print(
                    f"      {format_date(row['noon_ut']):<18}  "
                    f"{format_clock(row['noon_ut'] + 0.5):<10}  "
                    f"{row['local_mean_clock']:<15}   "
                    f"{row['eot_min']:+8.2f}    "
                    f"{row['noon_ut']:.6f}   "
                    f"{row['altitude']:12.4f}   "
                    f"{row['residual']:+12.4f}"
                    f"{marker}{inside}"
                )

        print()


if __name__ == "__main__":
    main()
