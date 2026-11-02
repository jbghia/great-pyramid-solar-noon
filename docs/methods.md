# Methods

Adopted inputs: latitude 29.9792 degrees N, longitude 31.1342 degrees E, elevations 45.0000 and 39.6078 degrees; not new measurements or uncertainty estimates. Azimuth is north through east, default 180 degrees.

Solar coordinates are Skyfield apparent geocentric true-equator/equinox-of-date. Compare 90 - abs(latitude - declination), without refraction or solar parallax. Bracket daily and bisect continuous TT roots to a numerical 0.001 s tolerance, not physical accuracy. Solve daily apparent hour angle with GAST/UT1 and a consistently configured fixed TT-UT1 offset. Select the nearest transit IN TIME and its following local-mean midnight; export the exact +/-1-hour UT1 bounds. Dates are proleptic Julian, not UTC or Egyptian civil dates.

Use one archived stellar catalogue with explicit epochs/proper motions. Skyfield stellar directions are apparent topocentric, no refraction, with parallax and radial velocity zero. Sample exact endpoints and refine local and boundary-adjacent brackets in elapsed seconds; local unimodality is assumed. Retain both sampled and refined separations and edge flags. Kernel hashes must agree across stages.

PyEphem dates are UT and its internal Delta T is reported. Resume one second after each transit; reject nonconsecutive spacing. Interpolate daily topocentric altitudes. These crossings are not equivalent to continuous geocentric roots. Changing inclination requires rerunning both main stages; azimuth alone does not change scalar noon roots. Physical illumination needs additional geometry and obstruction analysis.
