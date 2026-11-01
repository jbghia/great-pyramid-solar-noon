"""Offline routine checks, not a historical ephemeris validation."""
import ast
import importlib.util
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("preserved_stellar", ROOT / "original/stellar_alignment_search.py")
S = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = S
spec.loader.exec_module(S)


class GeometryTests(unittest.TestCase):
    def test_declinations(self):
        self.assertAlmostEqual(45 + 29.9792 - 90, -15.0208)
        self.assertAlmostEqual(39.6078 + 29.9792 - 90, -20.4130)

    def test_calendar_anchor(self):
        self.assertEqual(S.julian_day_from_astronomical_year(2000, 1, 1), 2451557.5)

    def test_ancient_label(self):
        self.assertEqual(S.julian_day_from_astronomical_year(-2549, 11, 22), 790360.5)

    def test_zero_separation(self):
        self.assertAlmostEqual(S.angular_separation_deg(45, 180, 45, 180), 0, places=5)

    def test_altitude_separation(self):
        self.assertAlmostEqual(S.angular_separation_deg(45, 180, 44, 180), 1, places=8)

    def test_wrap(self):
        self.assertEqual(S.signed_angular_difference_deg(1, 359), 2)

    def test_south_meridian(self):
        jd = 790360.5
        alt, az, ha = S.equatorial_to_altaz(S.local_sidereal_time_deg(jd), -15.0208, jd)
        self.assertAlmostEqual(alt, 45, places=7)
        self.assertAlmostEqual(az, 180, places=7)
        self.assertAlmostEqual(ha, 0, places=7)

    def test_window(self):
        a, b = S.search_window_bounds(790360.5)
        self.assertAlmostEqual((b-a)*24, 2, places=7)

    def test_isolated_solar_calendar(self):
        path = ROOT / "original/pyramid_solar_alignment.py"
        tree = ast.parse(path.read_text())
        names = {"required_declination_deg", "julian_calendar_to_jd", "jd_to_julian_calendar"}
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
        env = {"math": math, "PHI_GIZA": 29.9792}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), env)
        self.assertAlmostEqual(env["required_declination_deg"](45), -15.0208)
        for year in [-2549, -2548, 0, 2000]:
            jd = env["julian_calendar_to_jd"](year, 3, 1.0)
            self.assertEqual(env["jd_to_julian_calendar"](jd), (year, 3, 1.0))


if __name__ == "__main__":
    unittest.main()
