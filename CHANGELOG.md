# Changelog

## 1.1.0 – 2026-11-03

- Add `epoch_sensitivity.py`: scan of the target stars' meridian-altitude residuals for 2850–2150 BCE, for the adopted inclinations, Petrie's 45°13′ and 40.00°, with a catalogue baseline.
- Add archived outputs in `results/epoch_scan/` (checksums added to `SHA256SUMS`), the plotting script `scripts/plot_epoch_scan.py` and `requirements-plot.txt`.
- Add `docs/epoch_sensitivity.md` and offline tests, including a check that the scan reproduces the archived Table 8 residuals at 2550 BCE.
- Earlier scripts and archived results are unchanged.
- Archived on Zenodo: https://doi.org/10.5281/zenodo.23920012

## 1.0.0 – 2026-11-03

- Add archived results of the published run (`results/`) with checksums.
- Replace transcribed reference values with tables extracted from the archived results (`data/manuscript_tables/`).
- Add MIT licence, complete citation metadata and pinned package versions.
- Document input files (DE422, Hipparcos extract) with checksums.
- Rewrite README and reproduction record; document the earlier scripts in `original/`.
- Run all tests and the source audit in continuous integration.

## Unreleased (before 1.0.0)

- Solar meridian-altitude roots, daily transits and nighttime windows.
- Catalogue-based stellar search with endpoint-inclusive sampling and local refinement.
- Consecutive-transit inclination sensitivity, run metadata and input hashes.
- Offline pipeline tests and usage documentation.
