# Publication checklist

- [x] Scripts, inputs and package versions identified; hashes recorded in `results/*/run_metadata.json`
- [x] Archived outputs committed in `results/` with `SHA256SUMS`
- [x] Solar and PyEphem stages independently re-executed with identical results
- [x] Paper tables and figures generated from `results/` (see `paper_repository_mapping.md`)
- [x] Licence (MIT) and citation metadata (`CITATION.cff`)
- [ ] Enable the repository in Zenodo, then publish release v1.0.0 to obtain a DOI
- [ ] Add the DOI to the README, `CITATION.cff` and the paper's Data availability section
- [ ] Optional: archive the Hipparcos extract with the release so the stellar stage can be re-run byte-for-byte
