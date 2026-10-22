"""V112 10 existing cruise-port photo sources, date and SEO regression."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import v112_ten_port_photo_audit as audit
class V112Tests(unittest.TestCase):
    def test_ten_photo_rights_and_original_seo(self):
        result=audit.audit()
        self.assertTrue(result["passed"],result["errors"])
        self.assertEqual(result["checked"],10)
        self.assertEqual(result["photo_binary_replacements"],0)
    def test_history_context_and_attribution(self):
        records=json.loads((ROOT/audit.INV).read_text("utf8"))["items"]
        self.assertEqual(len({x["asset"] for x in records}),10)
        for item in records:
            self.assertGreaterEqual(item["year"],2000)
            self.assertLessEqual(item["year"],2026)
            self.assertTrue(item["source"].startswith("https://commons.wikimedia.org/wiki/File:"))
            self.assertRegex(item["git_blob_sha1"],r"^[a-f0-9]{40}$")
    def test_no_ferry_generic_fallback_on_actual_station_or_canal_photos(self):
        for slug in ("otaru","tokyo"):
            source=(ROOT/"site"/"things-to-do"/(slug+"-cruise-port-day-trip")/"index.html").read_text("utf8")
            target=next(x["asset"] for x in json.loads((ROOT/audit.INV).read_text("utf8"))["items"] if x["slug"]==slug)
            start=source.index('src="'+target+'"')
            self.assertNotIn("onerror=",source[start:start+500])
if __name__=="__main__":unittest.main()
