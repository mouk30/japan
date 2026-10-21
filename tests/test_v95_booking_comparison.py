"""V95 offline regression: only actual GA4 rows create numbers. Never manufacture conversions."""
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
spec=importlib.util.spec_from_file_location("v95",ROOT/"scripts/v95_booking_comparison.py")
v95=importlib.util.module_from_spec(spec);spec.loader.exec_module(v95)

class BookingComparisonTests(unittest.TestCase):
    def rows(self, records):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"synthetic-not-real.csv"
            with p.open("w",newline="",encoding="utf-8") as f:
                writer=csv.DictWriter(f,fieldnames=["Event name","Event count","route","page_area","placement","operator","destination_step"])
                writer.writeheader()
                for row in records:writer.writerow(dict(zip(writer.fieldnames,row)))
            return v95.parse_rows(p)

    def test_six_distinct_page_comparisons_and_rank_only_sufficient_views(self):
        rows=self.rows([
            ["ferry_hub_view",1000,"all","ferry_hub","page","internal","hub_view"],
            ["ferry_hub_view",200,"all","booking_hub","page","internal","hub_view"],
            ["ferry_route_view",100,"osaka","route_guide","page","internal","guide_view"],
            ["ferry_route_view",12,"fukuoka","route_guide","page","internal","guide_view"],
            ["ferry_operator_click",25,"osaka","ferry_hub","hub_card","panstar","operator_search"],
            ["ferry_operator_click",18,"fukuoka","ferry_hub","hub_card","koreaferry","booking_search"],
            ["ferry_operator_click",10,"tsushima","booking_hub","hub_card","panstar","operator_search"],
            ["ferry_operator_click",12,"osaka","route_guide","guide_hero","panstar","operator_search"],
            ["ferry_operator_click",1,"fukuoka","route_guide","guide_hero","koreaferry","booking_search"],
            ["ferry_operator_click",9,"osaka","ferry_hub","route_banner","panstar","route_info"],
        ])
        report=v95.summarize(rows,"테스트 기간")
        self.assertEqual(report["status"],"real_ga4_export_compared")
        self.assertEqual(report["booking_entry_clicks_total"],66)
        self.assertEqual(report["all_official_link_clicks"],75)
        self.assertEqual(len(report["pages"]),6)
        self.assertEqual(report["routes"]["osaka"]["booking_entry_clicks"],37)
        self.assertEqual(report["routes"]["fukuoka"]["booking_entry_clicks"],19)
        h={p["key"]:p for p in report["pages"]}
        self.assertEqual(h["ferry_hub"]["booking_clicks_per_100_views"],4.3)
        self.assertEqual(h["route_osaka"]["booking_clicks_per_100_views"],12)
        self.assertEqual(h["route_fukuoka"]["data_quality"],"low_sample")
        self.assertIsNone(h["route_fukuoka"]["qualified_activity_rank"])
        self.assertEqual(h["route_tsushima"]["data_quality"],"no_pageview_denominator")
        self.assertIsNone(h["route_tsushima"]["booking_clicks_per_100_views"])

    def test_information_links_are_not_booking_entry_clicks(self):
        rows=self.rows([
            ["ferry_hub_view",100,"all","ferry_hub","page","internal","hub_view"],
            ["ferry_operator_click",10,"osaka","ferry_hub","route_banner","panstar","route_info"],
            ["ferry_operator_click",4,"osaka","ferry_hub","hub_card","panstar","operator_search"],
        ])
        report=v95.summarize(rows)
        self.assertEqual(report["booking_entry_clicks_total"],4)
        self.assertEqual(report["all_official_link_clicks"],14)
        self.assertEqual(report["pages"][0]["booking_clicks_per_100_views"],4)
        self.assertEqual(report["pages"][0]["official_info_clicks"],10)

    def test_no_view_denominator_yields_null_not_zero(self):
        rows=self.rows([
            ["ferry_operator_click",14,"tsushima","route_guide","guide_end","panstar","operator_search"]
        ])
        report=v95.summarize(rows)
        guide=next(p for p in report["pages"] if p["key"]=="route_tsushima")
        self.assertIsNone(guide["measured_pageviews"])
        self.assertIsNone(guide["booking_clicks_per_100_views"])
        self.assertEqual(guide["data_quality"],"no_pageview_denominator")
        self.assertIsNone(guide["qualified_activity_rank"])

    def test_low_performance_is_a_review_lead_not_an_automatic_site_change(self):
        rows=self.rows([
            ["ferry_hub_view",100,"all","ferry_hub","page","internal","hub_view"],
            ["ferry_hub_view",100,"all","booking_hub","page","internal","hub_view"],
            ["ferry_operator_click",25,"osaka","ferry_hub","hub_card","panstar","operator_search"],
            ["ferry_operator_click",3,"osaka","booking_hub","hub_card","panstar","operator_search"],
        ])
        report=v95.summarize(rows)
        self.assertEqual(report["pages"][1]["data_quality"],"review_candidate")
        self.assertTrue(report["pages"][1]["review_reasons"])

    def test_no_data_private_dashboard_displays_unknown_not_fake_zero(self):
        report={"version":"V95","status":"awaiting_real_ga4_export",
                "period_label":"실제 데이터 미연결","booking_entry_clicks_total":None,
                "all_official_link_clicks":None,"routes":None,"pages":None}
        html=v95.markup(report)
        self.assertIn("미확인",html)
        self.assertIn('noindex,nofollow',html)
        self.assertNotIn('예약 진입 클릭 합계 0',html)
        with tempfile.TemporaryDirectory() as tmp:
            v95.write(report,tmp)
            self.assertTrue((Path(tmp)/"dashboard.html").exists())
            self.assertFalse((Path(tmp)/"report.json").exists())
            self.assertIsNone(json.loads((Path(tmp)/"status.json").read_text("utf8"))["booking_entry_clicks_total"])

    def test_real_data_html_escapes_user_supplied_period(self):
        rows=self.rows([
            ["ferry_hub_view",120,"all","ferry_hub","page","internal","hub_view"],
            ["ferry_operator_click",1,"osaka","ferry_hub","hub_card","panstar","operator_search"],
        ])
        report=v95.summarize(rows,'<img src=x onerror=alert(1)>')
        html=v95.markup(report)
        self.assertNotIn('<img src=x onerror=alert(1)>',html)
        self.assertIn('&lt;img',html)

    def test_rank_ratio_can_exceed_100_without_falsely_claiming_booking_rate(self):
        rows=self.rows([
            ["ferry_hub_view",100,"all","ferry_hub","page","internal","hub_view"],
            ["ferry_operator_click",200,"osaka","ferry_hub","hub_card","panstar","operator_search"],
        ])
        report=v95.summarize(rows)
        self.assertEqual(report["pages"][0]["booking_clicks_per_100_views"],200.0)
        self.assertIsNone(report["unique_reservations"])

if __name__=="__main__": unittest.main()
