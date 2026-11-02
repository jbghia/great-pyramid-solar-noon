# Reproduction and validation status

Twelve pipeline tests passed locally: roots, calendar/midnight conventions, exact endpoints, small-angle geometry, catalogue validation, synthetic consecutive transits, interpolation, continuous minimization, and CLI help. These are internal software checks, not astronomical validation.

Historical Skyfield/PyEphem backends and archived inputs were unavailable in that environment. No independent ancient-epoch coordinate/transit comparison, full catalogue ranking check, survey validation, or manuscript-table regeneration is claimed.

Before publication: archive actual inputs and versions; execute the workflow; test numerical convergence; independently check historical transformations; assess Delta T, space-motion and survey assumptions; run coupled sensitivity; regenerate tables and figures from the stated model. A compact Meeus model and the Skyfield implementation are not interchangeable. `data/manuscript_reported/` holds transcriptions, not proof of reproduction. Assign archival identifiers only to an actual reviewed archive.
