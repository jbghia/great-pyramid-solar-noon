"""Offline pipeline regression tests; not astronomical validation."""
import importlib.util
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from pyramid_solar_alignment import DAY, calendar_jd, julian_label, next_midnight, bisect, roots
from stellar_alignment_search import catalogue, grid_times, minimize, separation
from queens_chamber_solar_robustness import sample_transits, crossings

HAS_SCIPY = importlib.util.find_spec('scipy') is not None


class PipelineTests(unittest.TestCase):
    def test_calendar(self):
        self.assertEqual(calendar_jd(2000,1,1),2451557.5)
        self.assertEqual(julian_label(calendar_jd(0,1,1),'TT'),'01-01-1 BCE 00:00:00 TT')
        self.assertIn('22-11-2550 BCE',julian_label(calendar_jd(-2549,11,22),'UT1'))

    def test_midnight(self):
        noon = calendar_jd(-2549,11,21)+10/24
        self.assertAlmostEqual(next_midnight(noon,31.1342),calendar_jd(-2549,11,22)-31.1342/360,places=9)

    def test_roots(self):
        self.assertLess(abs(bisect(lambda t:t-790400.12345,790400,790401)-790400.12345)*DAY,0.002)
        self.assertEqual(roots(lambda t:t-3,0,3),[3])

    def test_exact_endpoint_grid(self):
        times = grid_times(7200.0004,60)
        self.assertEqual(times[0],0)
        self.assertEqual(times[-1],7200.0004)

    def test_small_separation(self):
        self.assertAlmostEqual(separation(45,180,45.000001,180),0.000001,places=10)

    @unittest.skipUnless(HAS_SCIPY,'SciPy not installed')
    def test_refinement_near_boundary(self):
        row = minimize(lambda t:{'separation_deg':(t-5)**2+0.02},120,60,0.001)
        self.assertAlmostEqual(row['seconds_from_start'],5,places=3)
        self.assertFalse(row['boundary'])

    @unittest.skipUnless(HAS_SCIPY,'SciPy not installed')
    def test_endpoint_minimum(self):
        row = minimize(lambda t:{'separation_deg':t+1},120)
        self.assertEqual(row['seconds_from_start'],0)
        self.assertTrue(row['boundary'])

    def test_no_skipped_transits(self):
        origin, period = 790400.0,0.9997
        def event(cursor):
            k = math.floor((cursor-origin)/period)+1
            return {'jd_ut':origin+k*period,'altitude_deg':40}
        rows = sample_transits(event,origin-0.5,origin+10)
        self.assertEqual(len(rows),11)
        self.assertTrue(all(abs(b['jd_ut']-a['jd_ut']-period)<1e-8 for a,b in zip(rows,rows[1:])))

    def test_bad_transit_spacing(self):
        with self.assertRaises(RuntimeError):
            sample_transits(lambda t:{'jd_ut':t+2,'altitude_deg':40},790400,790410)

    def test_crossings(self):
        rows = [{'jd_ut':i,'altitude_deg':h} for i,h in enumerate([42,40,38,40,42])]
        self.assertEqual(crossings(rows,39),[1.5,2.5])

    def test_catalogue_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'stars.csv'
            path.write_text('HIP,RAICRS,DEICRS,pmRA,pmDE,Vmag\n1,84,-1,1,2,2.49\n2,80,0,0,0,2.5\n')
            selected,excluded = catalogue(path)
            self.assertEqual((len(selected),excluded),(1,1))
            self.assertEqual(selected[0]['epoch_jyear'],1991.25)
            with self.assertRaises(ValueError):
                catalogue(path,expected=93)
            path.write_text('HIP,RAICRS,DEICRS,pmRA,pmDE,Vmag\n1,84,-1,nan,2,2\n')
            with self.assertRaises(ValueError):
                catalogue(path)

    def test_help_without_astronomy_import(self):
        project = Path(__file__).resolve().parents[1]
        for name in ['pyramid_solar_alignment.py','stellar_alignment_search.py','queens_chamber_solar_robustness.py']:
            done = subprocess.run([sys.executable,str(project/name),'--help'],capture_output=True,text=True)
            self.assertEqual(done.returncode,0,done.stderr)


if __name__ == '__main__':
    unittest.main()
