# Archived results

The `solar/`, `stellar/` and `queen_sensitivity/` folders hold the outputs of the run reported in the paper, produced with commit `2331431e3f9a8208a3f7142ab72287b8ed4d282b`, Skyfield 1.55, SciPy 1.18.1, PyEphem 4.2.1 and DE422. Files are stored byte-for-byte as written (Windows line endings); `.gitattributes` prevents conversion so that the checksums in `SHA256SUMS` and in the metadata stay valid.

`epoch_scan/` was added in version 1.1.0 (same DE422 kernel and Hipparcos extract; script hash in its `run_metadata.json`). It does not change any earlier file.

| Folder | Script | Files |
|---|---|---|
| `solar/` | `pyramid_solar_alignment.py` | `solar_roots.csv`, `sensitivity_boundaries.csv`, `daily_solar_noons.csv`, `stellar_windows.json`, `run_metadata.json` |
| `stellar/` | `stellar_alignment_search.py` | `ranked_stellar_results.csv`, `historical_targets.csv`, `run_metadata.json` |
| `queen_sensitivity/` | `queens_chamber_solar_robustness.py` | `daily_transits.csv`, `inclination_crossings.csv`, `inclination_shifts.csv`, `run_metadata.json` |
| `epoch_scan/` | `epoch_sensitivity.py`, `scripts/plot_epoch_scan.py` | `target_residuals_by_year.csv`, `best_epochs.csv`, `catalogue_baseline_by_year.csv`, `run_metadata.json`, `epoch_scan.png` |

Verify the files with:

```sh
cd results && sha256sum -c SHA256SUMS
```

Re-running a script writes to the same folder and overwrites these files; use `--output-dir` to write elsewhere when comparing.
