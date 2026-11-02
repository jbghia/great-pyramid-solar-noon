# Great Pyramid solar-noon correspondences

Research code and archived results for the paper *Solar-Noon Altitude Correspondences for the South-Directed Shafts of the Great Pyramid* (Jenny Baur, in preparation).

The code computes:

1. the instants in 2550–2549 BCE at which the Sun's airless meridian altitude at Giza equals the adopted inclinations of the southern shafts (King's Chamber 45.0000°, Queen's Chamber 39.6078°), with ±0.2° sensitivity windows;
2. the apparent solar noon closest to each root and the following local-mean-midnight window (23:00–01:00);
3. the angular separation of all 93 Hipparcos stars with V < 2.5 from the idealized due-south shaft direction in each window;
4. a PyEphem test of how the Queen's Chamber dates shift if the inclination is 40.0000° instead of 39.6078°.

## Repository layout

| Path | Contents |
|---|---|
| `pyramid_solar_alignment.py` | Solar roots, sensitivity boundaries, daily noons, stellar search windows |
| `stellar_alignment_search.py` | Open catalogue search and predefined targets (Orion's Belt, Sirius) |
| `queens_chamber_solar_robustness.py` | PyEphem inclination-sensitivity test |
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
```

Each stage writes CSV results and a `run_metadata.json` (script hash, input hashes, package versions, settings) into `results/solar/`, `results/stellar/` and `results/queen_sensitivity/`. Run `--help` on any script for all options.

## Model summary

- **Sun:** apparent geocentric declination from JPL DE422 via Skyfield (true equator and equinox of date); altitude h = 90° − |φ − δ|; no refraction or solar parallax. Roots are found by daily bracketing and bisection to 0.001 s.
- **Time:** fixed TT − UT1 = 61 033 s; proleptic Julian calendar; local mean solar time = UT1 + longitude/15°.
- **Noon and night:** of the apparent noons on three neighbouring UT1 days, the one closest in time to the root is selected; the search window is the following local mean midnight ± 1 h.
- **Stars:** Hipparcos ICRS positions (J1991.25) and proper motions, parallax and radial velocity set to zero; apparent topocentric, airless directions from Skyfield; 60 s grid plus SciPy bounded refinement (0.01 s). Minima at the exact window edge are flagged.
- **PyEphem test:** 141 consecutive daily transits, airless topocentric altitudes, PyEphem's internal ΔT, linear interpolation.

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

Please cite the archived release (see `CITATION.cff`) and state the version or commit you used. The code is released under the MIT licence (`LICENSE`). Hipparcos and JPL data remain subject to their providers' terms.
