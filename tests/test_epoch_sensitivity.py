"""Offline tests for the epoch-sensitivity helpers; not astronomical validation."""
import csv
import unittest
from pathlib import Path
from pyramid_solar_alignment import calendar_jd
from epoch_sensitivity import CASES, PETRIE_KINGS, bce, best_epoch, meridian_altitude, midnight_ut1, slope_per_century


class EpochSensitivityTests(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(bce(-2549), '2550 BCE')
        self.assertEqual(bce(0), '1 BCE')
        self.assertEqual(bce(1), '1 CE')

    def test_midnight_matches_principal_windows(self):
        # Centre of the 22 Nov 2550 BCE window in results/solar/stellar_windows.json
        self.assertAlmostEqual(midnight_ut1(-2549, 11, 22, 31.1342), 790360.4135161111, places=9)
        self.assertAlmostEqual(midnight_ut1(-2549, 12, 11, 31.1342), 790379.4135161111, places=9)

    def test_meridian_altitude(self):
        self.assertAlmostEqual(meridian_altitude(-15.0208, 29.9792), 45.0, places=10)
        self.assertAlmostEqual(meridian_altitude(-14.99571, 29.9792) - 45.0, 0.02509, places=5)

    def test_best_epoch_interpolation(self):
        years = [-2600, -2599, -2598]
        self.assertEqual(best_epoch(years, [-0.006, -0.001, 0.004]), ([-2598.8], 'zero crossing'))
        epochs, method = best_epoch(years, [0.3, 0.2, 0.1])
        self.assertEqual((epochs, method[:7]), ([-2598.0], 'minimum'))

    def test_slope_fit(self):
        years = list(range(-2600, -2499))
        res = [0.005 * (y + 2549) + (0.001 if y % 4 == 0 else 0) for y in years]
        self.assertAlmostEqual(slope_per_century(years, res, -2549), 0.5, places=2)

    def test_cases(self):
        self.assertAlmostEqual(PETRIE_KINGS, 45.216667, places=6)
        self.assertEqual({c[1] for c in CASES}, {'Kings', 'Queens'})

    def test_archived_scan_matches_principal_targets(self):
        # At 2550 BCE the meridian residuals must equal the archived Table 8 minima.
        root = Path(__file__).resolve().parents[1] / 'results'
        targets = {(r['chamber'], int(r['HIP'])): float(r['separation_deg'])
                   for r in csv.DictReader((root / 'stellar/historical_targets.csv').open(newline=''))
                   if r['window_label'].startswith(('22-11', '11-12'))}
        rows = [r for r in csv.DictReader((root / 'epoch_scan/best_epochs.csv').open(newline=''))
                if r['case_id'].endswith('_adopted')]
        self.assertEqual(len(rows), 4)
        for r in rows:
            self.assertAlmostEqual(abs(float(r['residual_at_reference_deg'])),
                                   targets[r['chamber'], int(r['HIP'])], places=4)


if __name__ == '__main__':
    unittest.main()
