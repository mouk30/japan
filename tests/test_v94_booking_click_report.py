import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v94",ROOT/"scripts/v94_booking_click_report.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class RealExportAnalysisTests(unittest.TestCase):
    def make_csv(self,headers,rows):
        tmp=tempfile.TemporaryDirectory()
        p=Path(tmp.name)/"synthetic-fixture.csv"
        with p.open("w",encoding="utf-8",newline="") as fh:
            w=csv.writer(fh)
            w.writerow(headers)
            w.writerows(rows)
        self.addCleanup(tmp.cleanup)
        return p

    def test_clicks_by_route_and_hub_denominator(self):
        path=self.make_csv(
            ["Event name","Event count","route","page_area","placement","operator","destination_step"],
            [["ferry_operator_click",3,"osaka","ferry_hub","hub_card","panstar","operator_search"],
             ["ferry_operator_click",2,"fukuoka","booking_hub","hub_card","koreaferry","booking_search"],
             ["ferry_operator_click",1,"osaka","route_guide","guide_hero","panstar","operator_search"],
             ["ferry_hub_view",20,"all","ferry_hub","page","internal","hub_view"],
             ["ferry_hub_view",10,"all","booking_hub","page","internal","hub_view"],
             ["ferry_route_view",5,"osaka","route_guide","page","internal","guide_view"]])
        result=mod.build_report(mod.parse_rows(path),"synthetic-fixture.csv")
        self.assertEqual(result["operator_clicks_total"],6)
        self.assertEqual(result["operator_clicks_by_route"]["osaka"],4)
        self.assertEqual(result["operator_clicks_by_route"]["fukuoka"],2)
        self.assertEqual(result["hub_activity"]["ferry_hub"]["clicks_per_100_pageviews"],15.0)
        self.assertEqual(result["guide_activity"]["osaka"]["clicks_per_100_pageviews"],20.0)
        self.assertEqual(result["guide_activity"]["tsushima"]["clicks_per_100_pageviews"],None)
        self.assertIn("NOT bookings",result["metric"])

    def test_count_can_exceed_100_clicks_per_100_views_without_false_conversion(self):
        path=self.make_csv(
            ["event_name","event_count","route","page_area"],
            [["ferry_operator_click",10,"osaka","ferry_hub"],["ferry_hub_view",2,"all","ferry_hub"]])
        result=mod.build_report(mod.parse_rows(path),"synthetic.csv")
        self.assertEqual(result["hub_activity"]["ferry_hub"]["clicks_per_100_pageviews"],500.0)
        self.assertIsNone(result["hub_activity"]["booking_hub"]["observed_page_views"])

    def test_missing_export_columns_fails_clearly(self):
        p=self.make_csv(["Event name","Event count"],[["ferry_operator_click","10"]])
        with self.assertRaisesRegex(ValueError,"route and page_area"):
            mod.parse_rows(p)

    def test_empty_export_does_not_claim_zero_clicks(self):
        p=self.make_csv(["Event name","Event count","route","page_area"],[["page_view","250"]])
        with self.assertRaisesRegex(ValueError,"No tracked ferry events"):
            mod.parse_rows(p)

    def test_korean_ga4_column_headers_are_supported(self):
        p=self.make_csv(["이벤트 이름","이벤트 수","항로","페이지 영역"],
                        [["ferry_operator_click","4","tsushima","ferry_hub"]])
        r=mod.build_report(mod.parse_rows(p),"synthetic.csv")
        self.assertEqual(r["operator_clicks_by_route"]["tsushima"],4)

    def test_invalid_counts_cannot_be_reported(self):
        p=self.make_csv(["Event name","Event count","route","page_area"],
                        [["ferry_operator_click","not known","osaka","ferry_hub"]])
        with self.assertRaisesRegex(ValueError,"invalid event_count"):
            mod.parse_rows(p)

if __name__=="__main__":
    unittest.main()
