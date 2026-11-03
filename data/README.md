# Input data and paper tables

## Input files (not included)

Place both files in `data/` (they are ignored by git).

### JPL DE422 ephemeris

- Download: <https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de422.bsp> (about 623 MB)
- SHA-256: `1c9725e0f7d05a5f881dfd8813641aa276a0f3923361e286dc421b59ea49f94e`
- Coverage: 3001 BCE December 7 to 3000 CE January 30 (<https://ssd.jpl.nasa.gov/planets/eph_export.html>)

### Hipparcos catalogue extract

- Source: Hipparcos main catalogue, ESA (1997), VizieR catalogue `I/239/hip_main` (<https://cdsarc.cds.unistra.fr/viz-bin/cat/I/239>)
- Selection: all entries with `Vmag < 2.5` (93 stars, none excluded)
- Required columns: `HIP, RAICRS, DEICRS, pmRA, pmDE, Vmag`; optional `name`, `epoch_jyear` (default 1991.25)
- Units: ICRS positions in decimal degrees; proper motions in mas/yr, `pmRA` includes cos δ
- SHA-256 of the file used for the archived run: `264d86dc833daef792cf5107c4894c94f8984046607d7904be4764aa78b20f88`

The exact file used for the archived run is attached to the [v1.0.0 release](https://github.com/jbghia/great-pyramid-solar-noon/releases/tag/v1.0.0) as `hipparcos_vmag_lt_2.5.csv` (checksum verified). A freshly re-downloaded extract can differ byte-for-byte (formatting, column order) while containing the same values, so its checksum may not match. The list of selected HIP numbers is recorded in `results/stellar/run_metadata.json`.

## Paper tables

`manuscript_tables/` contains the paper's central root table (Table 2) and the predefined-target table (Table 8) as CSV, extracted from the archived outputs in `results/`. They are convenience copies; `results/` is authoritative.
