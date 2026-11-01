# Great Pyramid solar-noon correspondences

Companion research repository for *Solar-Noon Altitude Correspondences for the South-Directed Shafts of the Great Pyramid: A Reproducible Geometrical Baseline*.

## Status

Source-preservation and reproducibility-audit edition. This is NOT yet a verified reproduction of all manuscript tables and figures. Original uploaded scripts are preserved under `original/` in the accompanying repository bundle; source upload to GitHub is a separate publishing step. See `docs/reproduction_status.md` for the differences between the supplied code and manuscript.

The study compares adopted shaft inclinations with solar meridian altitudes and uses the resulting dates to select nighttime stellar searches. A solar-date anchor is a right-ascension filter, not independent confirmation of a stellar altitude match. Assumed azimuth 180 degrees is not a measured physical shaft direction. Numerical correspondences do not demonstrate illumination, architectural intention, or historical significance.

## Contents

- `original/`: the three supplied Python scripts, preserved byte-for-byte in the bundle.
- `data/manuscript_reported/`: selected transcribed reference values, NOT regenerated calculations.
- `docs/`: methods, known issues, provenance, table mapping, and publication checklist.
- `scripts/audit_sources.py`: offline syntax and checksum audit.
- `tests/`: offline tests of selected geometric/calendar routines; not an ephemeris validation.
- `CITATION.cff`: repository citation metadata without an invented DOI or author name.

## Local checks

Requires Python 3.10 or newer for the documented workflow. From the repository root:

```sh
python scripts/audit_sources.py
python -m unittest discover -s tests -v
```

These checks do not need external catalogues or ephemerides. They require the three files in `original/`.

## Original research scripts

Create an isolated environment and install optional research dependencies:

```sh
python -m venv .venv
# POSIX: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The original scripts are archived for inspection, not recommended as a publication-ready pipeline. The solar script loads `de422.bsp` at import time and has unresolved implementation/test issues. The stellar script can download a Hipparcos catalogue and silently fall back to a manual star list. The Queen's Chamber script has unresolved time-scale and sampling issues. Read the audit before executing or interpreting output.

Dependencies are not a lockfile and do not reconstruct the original execution environment. The ephemeris, original Hipparcos cache, original generated tables, and figure-generation scripts were not supplied. No network-dependent numerical run has been verified for this edition.

## Citation and publication

Repository: https://github.com/jbghia/great-pyramid-solar-noon

Cite an exact reviewed commit or release, rather than implying the current default branch is immutable. No release or DOI has been created by this documentation. Confirm the paper author metadata and software/data licensing before the publication release. See `docs/publication_checklist.md`.

## License

No software license has been selected by the owner. Public visibility alone is not a license grant. Third-party catalogues and ephemerides retain their own terms. The paper PDF is not redistributed here.
