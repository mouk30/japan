"""V114: ten actual tourist-site photographs, rights, hash and SEO regression tests."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import v114_photo_quality_audit as v114
class V114(unittest.TestCase):
    def test_original_seo_and_ten_real_photos(self):
        r=v114.audit()
        self.assertTrue(r["passed"],r["errors"])
        self.assertEqual(r["checked"],10)
    def test_illustration_sources_removed(self):
        p=json.loads((ROOT/v114.PLAN).read_text("utf8"))["selected"]
        b={v["slug"]:v for v in json.loads((ROOT/v114.SEO).read_text("utf8"))["pages"]}
        self.assertEqual(len(set(x["output"] for x in p)),10)
        for x in p:
            s=(ROOT/"site/things-to-do"/(x["slug"]+"-cruise-port-day-trip")/"index.html").read_text("utf8")
            self.assertNotIn('src="'+b[x["slug"]]["hero"]+'"',s)
            self.assertIn(x["source"],s)
            self.assertIn('class="v114-photo-credit"',s)
    def test_historical_not_current(self):
        p=json.loads((ROOT/v114.PLAN).read_text("utf8"))["selected"]
        for x in p:
            self.assertTrue(x["taken"].startswith(("200","201","202")))
            self.assertTrue(x["source"].startswith("https://commons.wikimedia.org/wiki/File:"))
if __name__=="__main__":unittest.main()
