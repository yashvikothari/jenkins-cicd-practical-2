import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import app

class AppTests(unittest.TestCase):
    def test_health_status_is_ok(self):
        self.assertEqual(app.health_payload()["status"], "ok")

    def test_health_has_version(self):
        self.assertTrue(app.health_payload()["version"])

    def test_home_contains_version(self):
        self.assertIn(app.APP_VERSION, app.home_html())

    def test_home_reports_healthy(self):
        self.assertIn("APPLICATION HEALTHY", app.home_html())

if __name__ == "__main__":
    unittest.main()
