# Reproduction record

## Archived run

The files in `results/` were produced with the scripts at commit `2331431e3f9a8208a3f7142ab72287b8ed4d282b`. The script SHA-256 values recorded in each `run_metadata.json` match those files:

| Script | SHA-256 |
|---|---|
| `pyramid_solar_alignment.py` | `8ac3ff93a47db9ad4f1ae646483d306bc68c1b48fff9bd376fd397dad53386db` |
| `stellar_alignment_search.py` | `6e391de3eb691bb87061b5ecf16675693eef7177283ab9659b005a51dc23bcb0` |
| `queens_chamber_solar_robustness.py` | `4358c685f6eeb65b31ba1c8523caa73ccb5b8ebfb5a57235fec11ec2f632d98a` |

Inputs: DE422 (`1c9725e0…a49f94e`), Hipparcos extract (`264d86dc…b20f88`, 93 stars).

## Independent re-execution (2 November 2026)

On a separate Linux machine, with DE422 downloaded from JPL (checksum matching), Skyfield 1.55, SciPy 1.18.1 and PyEphem 4.2.1:

- **Solar stage:** `solar_roots.csv`, `sensitivity_boundaries.csv`, `daily_solar_noons.csv` and the content of `stellar_windows.json` were reproduced exactly (maximum numerical difference 0).
- **PyEphem stage:** `daily_transits.csv`, `inclination_crossings.csv` and `inclination_shifts.csv` were reproduced exactly.
- **Stellar stage:** not re-executed, because the catalogue could not be retrieved in that environment. The outputs were checked for internal consistency: 93 stars in each of the four cases, the same HIP set in every case, ranks ordered by separation, and edge flags consistent with the window bounds.

## Cross-check of the solar model

For the Queen's Chamber inclination (39.6078°), the PyEphem crossings fall 0.010 d earlier and 0.031 d later than the Skyfield roots. Because the two calculations use different solar theories, ΔT values and quantities (interpolated daily topocentric transits vs. continuous geocentric roots), this is a consistency check, not an independent validation.

## Known limitations

- Fixed ΔT (61 033 s); its historical uncertainty at this epoch (tens of minutes or more) is not propagated.
- Skyfield's IAU 2006 precession is not designed for −2548; the difference from the long-term model of Vondrák et al. (2011) is about 10″ for the target stars.
- Stellar parallax, radial velocity and refraction are neglected (about 1′ for Sirius, negligible for the others).
- The shaft azimuth is idealized as 180°; the inclinations are adopted values, not new measurements.
