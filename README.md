# Great Pyramid solar-noon correspondences

[![DOI](https://zenodo.org/badge/1442216677.svg)](https://doi.org/10.5281/zenodo.23900531)

Research code and archived results for the paper *Solar-Noon Altitude Correspondences for the South-Directed Shafts of the Great Pyramid* (Jenny Baur, [ORCID 0009-0009-8855-211X](https://orcid.org/0009-0009-8855-211X), in preparation).

The code computes:

1. the instants in 2550–2549 BCE at which the Sun's airless meridian altitude at Giza equals the adopted inclinations of the southern shafts (King's Chamber 45.0000°, Queen's Chamber 39.6078°), with ±0.2° sensitivity windows;
2. the apparent solar noon closest to each root and the following local-mean-midnight window (23:00–01:00);
3. the angular separation of all 93 Hipparcos stars with V < 2.5 from the idealized due-south shaft direction in each window;
4. a PyEphem test of how the Queen's Chamber dates shift if the inclination is 40.0000° instead of 39.6078°;
5. an epoch-sensitivity scan (2850–2150 BCE) of the target stars' meridian-altitude residuals, with a simple catalogue baseline.

## Repository layout

| Path | Contents |
|---|---|
| `pyramid_solar_alignment.py` | Solar roots, sensitivity boundaries, daily noons, stellar search windows |
| `stellar_alignment_search.py` | Open catalogue search and predefined targets (Orion's Belt, Sirius) |
| `queens_chamber_solar_robustness.py` | PyEphem inclination-sensitivity test |
| `epoch_sensitivity.py` | Epoch scan of the stellar meridian-altitude residuals |
| `scripts/plot_epoch_scan.py` | Figure of the epoch scan (optional, needs matplotlib) |
| `results/` | Archived outputs of the run reported in the paper, with `SHA256SUMS` |
| `data/` | Input-file instructions and the paper's key tables as CSV |
| `docs/` | Method notes, paper-to-code mapping, reproduction record |
| `original/` | Earlier preserved script versions (not used for the published results) |
| `tests/` | Offline regression tests |

## Requirements

Python 3.12 or newer (required by SciPy 1.18) and the exact package versions in `requirements.txt`:

```sh
python -m pip install -r requirements.txt
```

Two input files are needed; neither is downloaded automatically (see `data/README.md`):

- the JPL DE422 kernel `de422.bsp` (SHA-256 `1c9725e0f7d05a5f881dfd8813641aa276a0f3923361e286dc421b59ea49f94e`);
- a CSV extract of the Hipparcos main catalogue (VizieR I/239) with V < 2.5.

## Running

```sh
python pyramid_solar_alignment.py --ephemeris data/de422.bsp
python stellar_alignment_search.py --ephemeris data/de422.bsp --catalogue data/hipparcos.csv --windows-json results/solar/stellar_windows.json
python queens_chamber_solar_robustness.py
python epoch_sensitivity.py --ephemeris data/de422.bsp --catalogue data/hipparcos.csv
```

For the optional figure: `python -m pip install -r requirements-plot.txt`, then `python scripts/plot_epoch_scan.py`.

Each stage writes CSV results and a `run_metadata.json` (script hash, input hashes, package versions, settings) into `results/solar/`, `results/stellar/`, `results/queen_sensitivity/` and `results/epoch_scan/`. Run `--help` on any script for all options.

## Model summary

- **Sun:** apparent geocentric declination from JPL DE422 via Skyfield (true equator and equinox of date); altitude h = 90° − |φ − δ|; no refraction or solar parallax. Roots are found by daily bracketing and bisection to 0.001 s.
- **Time:** fixed TT − UT1 = 61 033 s; proleptic Julian calendar; local mean solar time = UT1 + longitude/15°.
- **Noon and night:** of the apparent noons on three neighbouring UT1 days, the one closest in time to the root is selected; the search window is the following local mean midnight ± 1 h.
- **Stars:** Hipparcos ICRS positions (J1991.25) and proper motions, parallax and radial velocity set to zero; apparent topocentric, airless directions from Skyfield; 60 s grid plus SciPy bounded refinement (0.01 s). Minima at the exact window edge are flagged.
- **PyEphem test:** 141 consecutive daily transits, airless topocentric altitudes, PyEphem's internal ΔT, linear interpolation.
- **Epoch scan:** apparent declination of each star at local mean midnight of the same calendar night for every year 2850–2150 BCE; residual = meridian altitude − inclination, for 45.00°, 45.22° (Petrie), 39.6078° and 40.00°. See `docs/epoch_sensitivity.md`.

Details are in `docs/methods.md`. These are numerical correspondences under adopted inputs; they do not by themselves establish illumination, intention or statistical significance.

## Reproduction status

The archived results were produced with commit `2331431` and the package versions above. On 2 November 2026 the solar and PyEphem stages were re-run independently with a freshly downloaded DE422 kernel (matching checksum) and reproduced every output file exactly. The stellar stage depends on the archived catalogue file and was checked for internal consistency. See `docs/reproduction_status.md`.

## Tests

```sh
python -m unittest discover -s tests -v
python scripts/audit_sources.py
```

The tests check calendar conversions, root finding, window construction, sampling and minimization logic. They are software checks, not astronomical validation.

## Citation and licence

The code and results are archived on Zenodo. To cite the current version, which includes the epoch-sensitivity scan:

> Baur, J. (2026). *Great Pyramid solar-noon altitude correspondences* (Version 1.1.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23920012

Version 1.0.0, the code and results of the paper's principal analysis without the epoch scan, has the DOI [10.5281/zenodo.23900532](https://doi.org/10.5281/zenodo.23900532). The DOI [10.5281/zenodo.23900531](https://doi.org/10.5281/zenodo.23900531) always resolves to the latest version. Please cite the version you used; metadata are in `CITATION.cff`. The v1.0.0 release also includes the exact Hipparcos extract used for the archived run (`hipparcos_vmag_lt_2.5.csv`).

The code is released under the MIT licence (`LICENSE`). Hipparcos and JPL data remain subject to their providers' terms.
