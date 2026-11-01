# Reproduction status

## Preservation

All three supplied scripts are in `original/`. Source text is preserved without scientific corrections; CRLF line endings are normalized to LF and a final newline is added. `data/source_manifest.json` distinguishes original uploaded byte hashes from normalized repository text hashes. Earlier descriptions of byte-for-byte preservation apply to the original ZIP bundle, not GitHub's normalized text files.

## Unresolved manuscript/code differences

1. The manuscript describes a compact Meeus-style solar model and a truncated VSOP87D/Laskar comparison; the supplied solar script uses Skyfield/DE422. Neither generating compact code nor comparison code was supplied.
2. The solar routines call `(EARTH + SUN).at(t).apparent()` instead of forming an Earth-observer-to-Sun observation. This is an unresolved review finding, not a corrected or executed ephemeris solution.
3. The solar self-test treats JD 2451545.0 as an equinox-like declination check; its epoch/expectation needs independent verification and correction.
4. The manuscript adopts Delta T = 61,033 s; the solar code defaults to a variable parabola. The stellar code uses one JD for astrometry and Earth rotation without an explicit TT/UT separation.
5. Predefined stellar tests use approximate manually entered J2000-like data, while the manuscript describes Hipparcos J1991.25 inputs.
6. The stellar script returns grid minima; the manuscript describes additional interior-minimum refinement.
7. Catalogue failure silently substitutes a small manual star list. That fallback is not a verified 93-star Hipparcos search.
8. The Queen's Chamber script advances a full day after each transit before requesting the next, potentially skipping transits. Its PyEphem date inputs and TT labels require consistent time-scale treatment. Results remain preliminary.
9. The original catalogue cache, ephemeris kernel, environment lockfile, original generated outputs, and figure-generation code were not supplied.

## Verified scope

Three normalized source-text hashes and syntax checks, plus nine selected offline geometry/calendar tests, passed locally. These are not independent astronomical validation. GitHub Actions execution must be checked separately.

Complete numerical reproduction of Tables 2-12 and Figures 1-4 has not been established. Transcribed manuscript values are explicitly separate from generated results. No physical alignment, historical intent, or statistical significance is newly established.

## Further work

Recover exact generating code or identify replacements as reconstructed; reconcile models and time scales; archive catalogue and environment inputs; remove silent fallback in a separately identified revised implementation; implement/document refinement; verify transit sampling; compare every regenerated table and figure; and perform independent long-term astronomical checks before a publication release.
