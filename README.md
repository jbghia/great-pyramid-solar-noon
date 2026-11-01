# Great Pyramid solar-noon correspondences

Companion repository for *Solar-Noon Altitude Correspondences for the South-Directed Shafts of the Great Pyramid: A Reproducible Geometrical Baseline*.

## Status

Source-preservation and reproducibility-audit edition, not yet a verified reproduction of every manuscript table and figure. All three supplied research scripts are included under `original/`. No scientific corrections have been applied. Repository text uses LF line endings and a final newline; original byte hashes and normalized text hashes are recorded separately in `data/source_manifest.json`.

## Contents

- `original/`: supplied solar, stellar, and Queen's Chamber sensitivity scripts.
- `scripts/audit_sources.py`: offline source-text integrity and syntax checks.
- `tests/test_geometry.py`: nine offline checks of selected routines, not an ephemeris validation.
- `.github/workflows/tests.yml`: runs the offline checks on GitHub Actions.
- `data/manuscript_reported/`: selected manuscript values transcribed as references, not regenerated results.
- `docs/`: methods, reproduction gaps, table mapping, publication checklist, and local-check report.
- `requirements.txt`: optional dependencies inferred from imports, not the original pinned environment.
- `CITATION.cff`: preliminary citation metadata; author details and publication release remain to be confirmed.

## Run offline checks

From the repository root with Python 3.10 or newer:

```sh
python scripts/audit_sources.py
python -m unittest discover -s tests -v
```

Three source-text checks and nine tests passed locally. This does not establish independent long-term astronomical accuracy or numerical reproduction of the paper. GitHub Actions results must be checked separately.

## Research dependencies and scripts

```sh
python -m venv .venv
# Activate the environment for your operating system.
python -m pip install -r requirements.txt
```

Read `docs/reproduction_status.md` before interpreting output. The solar script loads `de422.bsp` at import time and has unresolved implementation/test issues. The stellar script may download catalogue data and silently fall back to a small manual list. The supplementary Queen's Chamber calculation has unresolved sampling and time-scale issues. These original scripts are preserved for inspection, not endorsed as a publication-ready pipeline.

The original catalogue snapshot, ephemeris kernel, original generated outputs, compact-model code, independent solar comparison code, and figure-generation scripts were not supplied. Dependencies are not a lockfile. No full network-dependent reproduction is claimed.

## Scientific scope

The comparisons use adopted inclinations and idealized due-south directions, not measured complete shaft sightlines. Solar-date anchors constrain the nighttime search but do not independently confirm stellar altitude matches. Numerical correspondences do not demonstrate illumination, architectural intention, or historical significance.

## Citation and license

Repository: https://github.com/jbghia/great-pyramid-solar-noon

Cite an exact reviewed commit or release. No publication release or DOI is assigned. Author metadata and a software license require owner confirmation; no license grant is implied by public visibility. Third-party data retain their own terms. The paper PDF is not redistributed. See `docs/publication_checklist.md` before updating the paper's data-availability statement.
