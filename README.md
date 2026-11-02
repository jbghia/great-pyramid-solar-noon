# Great Pyramid solar-noon correspondences

Research software for solar meridian-altitude dates at Giza and stellar comparisons on the resulting nighttime windows.

## Run

Use Python 3.10+ and keep the three root scripts together:

```sh
python -m pip install -r requirements.txt
python pyramid_solar_alignment.py --ephemeris data/de422.bsp
python stellar_alignment_search.py --ephemeris data/de422.bsp --catalogue data/hipparcos.csv --windows-json results/solar/stellar_windows.json
python queens_chamber_solar_robustness.py
```

Supply a local historical-coverage BSP and archived catalogue CSV. No data are downloaded or substituted. Required columns: HIP, RAICRS, DEICRS, pmRA, pmDE, Vmag. Optional epoch_jyear defaults to 1991.25; name is a label. ICRS positions are decimal degrees; proper motions are mas/year, with pmRA including cos(dec).

## Model

Skyfield evaluates apparent geocentric solar coordinates and apparent topocentric stellar directions without refraction. Solar parallax is excluded; stellar parallax and radial velocity are zero. The main stages share the kernel and fixed TT-UT1, 61,033 s by default. This is not a compact Meeus geometric approximation. The manuscript must describe the actual executed model.

Solar roots are mapped to the closest daily transit in time and then the following local-mean midnight. Stellar searches retain exact endpoints, sampled/refined minima, rankings and edge flags. The PyEphem sensitivity experiment instead retains its internal Delta T and interpolates daily topocentric transit altitudes. These are distinct quantities; see `docs/methods.md`.

## Verification and outputs

```sh
python -m unittest discover -s tests -p test_pipeline.py -v
```

Twelve pipeline tests passed locally, including actual SciPy minimization and synthetic sampling tests. Historical backends and independent ancient-epoch accuracy were not evaluated in that environment. Passing tests do not establish physical alignment or regenerate manuscript tables. Real runs save CSV results and JSON configuration, input hashes and installed versions under `results/`. Transcribed reference tables are not computed outputs.

For coupled inclination sensitivity, rerun solar anchors and then the stellar stage with the new windows JSON. An azimuth-only override does not change scalar solar-noon roots. CLI help documents options; `docs/reproduction_status.md` records validation scope.

## Citation and licensing

https://github.com/jbghia/great-pyramid-solar-noon

Cite an exact reviewed snapshot. No release or archival DOI is assigned. Author metadata and licensing require owner review. Numerical correspondences alone do not establish illumination, statistical preference or architectural intention.
