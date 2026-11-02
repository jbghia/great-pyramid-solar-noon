# Archived results

Outputs of the run reported in the paper, produced with commit `2331431e3f9a8208a3f7142ab72287b8ed4d282b`, Skyfield 1.55, SciPy 1.18.1, PyEphem 4.2.1 and DE422. Files are stored byte-for-byte as written (Windows line endings); `.gitattributes` prevents conversion so that the checksums in `SHA256SUMS` and in the metadata stay valid.

| Folder | Script | Files |
|---|---|---|
| `solar/` | `pyramid_solar_alignment.py` | `solar_roots.csv`, `sensitivity_boundaries.csv`, `daily_solar_noons.csv`, `stellar_windows.json`, `run_metadata.json` |
| `stellar/` | `stellar_alignment_search.py` | `ranked_stellar_results.csv`, `historical_targets.csv`, `run_metadata.json` |
| `queen_sensitivity/` | `queens_chamber_solar_robustness.py` | `daily_transits.csv`, `inclination_crossings.csv`, `inclination_shifts.csv`, `run_metadata.json` |

Verify the files with:

```sh
cd results && sha256sum -c SHA256SUMS
```

Re-running a script writes to the same folder and overwrites these files; use `--output-dir` to write elsewhere when comparing.
