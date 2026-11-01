# Reproduction status

## Available evidence

The author supplied a 20-page manuscript and three Python source files. The bundle preserves the source files byte-for-byte; SHA-256 values are in `data/source_manifest.json`. The manuscript itself is not redistributed. Passing syntax or selected unit tests does not validate a historical ephemeris or reproduce published results.

## Blocking discrepancies

1. **Solar model:** manuscript Sections 3.3-3.4 describe compact Meeus-style calculations and a truncated VSOP87D/Laskar comparison. The uploaded solar script uses Skyfield/DE422 and apparent coordinates. No compact-model or VSOP comparison script was supplied.
2. **Solar implementation:** `solar_declination_deg` and the equation-of-time routine call `(EARTH + SUN).at(t).apparent()` rather than forming an Earth-observer-to-Sun observation. This is an unresolved code-review finding, not a corrected or executed solution.
3. **Solar self-test:** a test requires the declination at JD 2451545.0 to be between -1 and +1 degree while labeling it an equinox check. The test epoch/expectation needs correction and independent verification.
4. **Delta T:** the manuscript specifies an adopted 61,033 s; the original solar script defaults to a variable parabola with no fixed override. The stellar script uses one JD for both astrometric epoch and Earth rotation without an explicit TT/UT split.
5. **Stellar data:** the manuscript describes Hipparcos J1991.25 inputs. Predefined tests in the script use manually entered approximate J2000-like positions; open searches use a downloaded cache when available.
6. **Search refinement:** the manuscript describes refining interior minima. The original script uses grid minima only. Reported sub-grid precision is not verified by this implementation.
7. **Catalogue fallback:** failure to obtain Hipparcos causes substitution of the small manual list. Such a run must not be represented as the manuscript's 93-star catalogue search.
8. **Queen's Chamber:** the supplementary script advances from a transit by a full day before requesting the next transit, potentially skipping transits. It also labels directly passed PyEphem date values as TT without an explicit consistent TT/UT conversion. Retain its outputs as preliminary.
9. **Missing artifacts:** no original catalogue snapshot, ephemeris kernel, environment lockfile, original generated result files, compact solar implementation, independent validation calculation, or figure-generation code was supplied.

## What this edition establishes

- Source syntax can be checked offline.
- Original source checksums can be checked offline.
- Selected declination/altitude, calendar, and vector-geometry routines can be unit tested.
- Selected manuscript values are preserved as transcribed references only.

## What it does not establish

Exact reproduction of Tables 2-12, Figures 1-4, catalogue completeness, physical shaft alignment, historical intent, or long-term astrometric accuracy. No scientific correction is silently substituted for an original calculation.

## Required next implementation work

Recover the exact generating scripts if available; otherwise label any replacement as reconstructed. Reconcile the solar models and coordinate definitions; use explicit TT for astrometry and UT for Earth rotation; remove silent catalogue fallback; archive catalogue inputs and checksums; implement/document refinement; verify sampling; run independent checks; compare every regenerated table and figure with the manuscript.
