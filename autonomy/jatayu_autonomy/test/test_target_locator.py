"""
Unit test for target georeferencing projection mathematics.
"""

import unittest
from jatayu_autonomy.target_locator import project_pixel_to_gps, TargetLocator


class TestTargetLocator(unittest.TestCase):
    def setUp(self):
        self.locator = TargetLocator()

    def test_center_pixel_projection(self):
        # Drone at 26.25104, 78.17124, 30m AGL, heading North (0 deg)
        lat, lon, unc = project_pixel_to_gps(
            u=640,
            v=360,
            drone_lat=26.25104,
            drone_lon=78.17124,
            drone_alt_m=30.0,
            drone_yaw_deg=0.0
        )
        # Should project slightly forward of the drone position due to 45 deg camera mount
        self.assertGreater(lat, 26.25104)
        self.assertAlmostEqual(lon, 78.17124, places=4)
        self.assertGreater(unc, 1.0)

    def test_process_detection(self):
        res = self.locator.process_detection(
            bbox=[400, 200, 600, 500],
            conf=0.95,
            pose="lying_down",
            target_id="TGT-TEST"
        )
        self.assertEqual(res["target_id"], "TGT-TEST")
        self.assertEqual(res["severity"], 9)
        self.assertAlmostEqual(res["confidence"], 0.95)


if __name__ == "__main__":
    unittest.main()
