"""V113 ten AI-to-real photographed tourist images, license credits and original SEO."""
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import v113_photo_quality_audit as audit
class V113Quality(unittest.TestCase):
    def test_webp_photographs_sources_original_seo(self):
        result=audit.scan()
        self.assertTrue(result["passed"],result["errors"])
        self.assertEqual(result["checked"],10)
        self.assertEqual(result["ai_hero_images_replaced"],10)
    def test_ai_replacements_are_unique_and_explicitly_documented(self):
        photos=json.loads((ROOT/"audit-reports/v113/photo-import-plan.json").read_text("utf8"))["items"]
        self.assertEqual(len({x["slug"] for x in photos}),10)
        self.assertEqual(len({x["output"] for x in photos}),10)
        for item in photos:
            self.assertTrue(item["commons_url"].startswith("https://commons.wikimedia.org/wiki/File:"))
            self.assertTrue(item["output"].endswith(".webp"))
    def test_shiraoi_is_a_traditional_house_not_a_hearth(self):
        result=json.loads((ROOT/"audit-reports/v113/import-result.json").read_text("utf8"))
        item=next(x for x in result["items"] if x["slug"]=="shiraoi")
        self.assertIn("14.jpg",item["source"])
        html=(ROOT/"site/things-to-do/shiraoi-cruise-port-day-trip/index.html").read_text("utf8")
        self.assertIn("전통 아이누 가옥(치세)",html)
if __name__=="__main__":unittest.main()
