"""V111 10 cruise-port photo provenance and SEO preservation regression."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"scripts"))
import v111_ten_port_photo_audit as photo

class V111PortPhotoQualityTests(unittest.TestCase):
    def test_existing_ten_article_photos_and_seo(self):
        result = photo.audit()
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(result["verified_pages"], 10)
        self.assertEqual(result["representative_images_replaced"], 4)
        self.assertEqual(result["og_images_corrected"], 7)

    def test_photo_identity_and_license_records(self):
        manifest = json.loads((ROOT/photo.MANIFEST).read_text("utf8"))
        self.assertEqual(len(manifest["items"]), 10)
        self.assertEqual(len(set(x["slug"] for x in manifest["items"])), 10)
        self.assertEqual(len(set(x["asset"] for x in manifest["items"])), 10)
        for entry in manifest["items"]:
            self.assertTrue(entry["source"].startswith("https://commons.wikimedia.org/wiki/File:"))
            self.assertRegex(entry["blob_sha"], r"^[a-f0-9]{40}$")

    def test_kochi_matsuyama_old_disclaimer_is_removed(self):
        for slug in ("kochi", "matsuyama"):
            html=(ROOT/"site"/"things-to-do"/(slug+"-cruise-port-day-trip")/"index.html").read_text("utf8")
            self.assertNotIn("현재는 공통 크루즈 참고 이미지입니다.", html)
            self.assertIn('class="v111-photo-credit"', html)

if __name__ == "__main__":
    unittest.main()
