# Epoch sensitivity

`epoch_sensitivity.py` tests how the stellar correspondences of the principal analysis depend on the adopted construction epoch (2550 BCE).

## Method

For every year from 2850 BCE to 2150 BCE (astronomical years −2849 to −2149, step 1 year), the apparent declination of each of the 93 Hipparcos stars with V < 2.5 is computed at 00:00 local mean solar time on the same proleptic Julian calendar night as in the principal analysis: 22 November for the King's Chamber and 11 December for the Queen's Chamber. The declination is converted into an airless meridian altitude, h = 90° − |φ − δ|, and compared with the shaft inclination.

The residual h − α equals the angular separation from an idealized due-south shaft direction at the star's meridian transit. As shown in Section 3.10 of the paper, the altitude match at transit depends only on declination, so the solar roots and the night-time search do not need to be recomputed. Ephemeris (DE422), catalogue, astrometry (Skyfield apparent place of date, proper motion, parallax and radial velocity zero, no refraction), location and fixed TT − UT1 are the same as in the principal scripts.

Four inclination cases are evaluated:

| Case | Shaft | Inclination | Source |
|---|---|---|---|
| `Kings_adopted` | King's Chamber | 45.0000° | adopted value of the paper |
| `Kings_Petrie` | King's Chamber | 45.2167° | Petrie (1883), 45°13′ |
| `Queens_adopted` | Queen's Chamber | 39.6078° | adopted value of the paper |
| `Queens_40` | Queen's Chamber | 40.0000° | alternative value of the paper (Section 3.5) |

Targets are the three Orion Belt stars for the King's Chamber and Sirius for the Queen's Chamber. The year of best match is the zero crossing of the residual, interpolated linearly between consecutive years. The rate of change is a least-squares fit over 2600–2500 BCE; single-year differences jitter with the four-year Julian leap cycle because annual aberration is evaluated on a fixed calendar date.

As a simple baseline, `catalogue_baseline_by_year.csv` lists for each year and case the closest of all catalogue stars culminating south of the zenith and the number of stars within 0.1° and 0.2°. This baseline ignores right ascension, i.e. it does not require the star to transit near midnight on the selected night.

## Results (archived run)

At 2550 BCE the residuals reproduce the archived minima of Table 8 (Alnilam +0.0251°, Alnitak −0.2732°, Mintaka +0.5049°, Sirius −0.5540°) to better than 0.00001°.

| Case | Star | Residual at 2550 BCE | Change per century | Year of best match |
|---|---|---|---|---|
| King's 45.00° | Mintaka | +0.505° | +0.50° | 2650 BCE |
| King's 45.00° | Alnilam | +0.025° | +0.50° | 2555 BCE |
| King's 45.00° | Alnitak | −0.273° | +0.49° | 2494 BCE |
| King's 45.22° | Mintaka | +0.288° | +0.50° | 2607 BCE |
| King's 45.22° | Alnilam | −0.192° | +0.50° | 2511 BCE |
| King's 45.22° | Alnitak | −0.490° | +0.49° | 2449 BCE |
| Queen's 39.6078° | Sirius | −0.554° | +0.32° | 2370 BCE |
| Queen's 40.00° | Sirius | −0.946° | +0.32° | 2237 BCE |

Main points:

- The Orion Belt residuals change by about 0.5° per century, Sirius by about 0.3° per century. A shift of the adopted epoch by 50 years therefore changes the Alnilam separation from 0.025° to about 0.25°.
- With the adopted inclinations, the best Alnilam year (2555 BCE) and the best Sirius year (2370 BCE) differ by about 185 years. No single epoch gives close matches for both shafts.
- With Petrie's 45°13′, Alnitak becomes the best-matching Belt star around 2450 BCE and Alnilam around 2510 BCE.
- Baseline: over the 701 years scanned, some catalogue star lies within 0.1° of the King's Chamber meridian altitude (45.00°) in 137 years and within 0.2° in 236 years. For the Queen's Chamber (39.6078°) the numbers are 150 and 310 years.

These are geometric results under the stated model. They do not establish intention, illumination or historical significance, and the epoch range is a scan range, not a proposed dating.

## Running

```sh
python epoch_sensitivity.py --ephemeris data/de422.bsp --catalogue data/hipparcos.csv
python -m pip install -r requirements-plot.txt   # optional, for the figure
python scripts/plot_epoch_scan.py
```

Outputs in `results/epoch_scan/`:

| File | Contents |
|---|---|
| `target_residuals_by_year.csv` | Declination, meridian altitude and residual of each target star, per case and year |
| `best_epochs.csv` | Year of best match, residual at 2550 BCE and rate of change per target and case |
| `catalogue_baseline_by_year.csv` | Closest southern-culminating catalogue star and counts within 0.1° and 0.2°, per case and year |
| `run_metadata.json` | Script and input hashes, package versions, settings |
| `epoch_scan.png` | Residual against year for all targets and cases |
