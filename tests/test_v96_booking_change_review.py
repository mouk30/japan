"""V96 manual review leads from two actual GA4 exports, with synthetic test fixtures only."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from v96_booking_change_review import compare

def row(name,num,route,area,step="other",placement="hub_card"):
    return {"event":name,"count":num,"route":route,"page_area":area,"destination_step":step,"placement":placement,"operator":"panstar"}

class V96Tests(unittest.TestCase):
    def test_largest_real_click_activity_drop_requires_manual_review(self):
        before=[row("ferry_hub_view",200,"all","ferry_hub"),row("ferry_operator_click",40,"osaka","ferry_hub","operator_search")]
        now=[row("ferry_hub_view",200,"all","ferry_hub"),row("ferry_operator_click",10,"osaka","ferry_hub","operator_search")]
        report=compare(before,now,7,7,100)
        first=next(p for p in report["pages"] if p["page"]=="ferry_hub")
        self.assertEqual(first["decision"],"editorial_review_candidate")
        self.assertEqual(first["prior_clicks_per_100_views"],20)
        self.assertEqual(first["recent_clicks_per_100_views"],5)
        self.assertEqual(report["review_candidate_count"],1)
        self.assertIn("변경 금지",first["review_step"])

    def test_low_sample_is_not_labeled_underperforming(self):
        before=[row("ferry_hub_view",10,"all","ferry_hub"),row("ferry_operator_click",8,"osaka","ferry_hub","operator_search")]
        now=[row("ferry_hub_view",9,"all","ferry_hub"),row("ferry_operator_click",1,"osaka","ferry_hub","operator_search")]
        report=compare(before,now,7,7,100)
        sample=next(p for p in report["pages"] if p["page"]=="ferry_hub")
        self.assertEqual(sample["decision"],"hold_insufficient_comparable_views")
        self.assertIsNone(sample["relative_change_percent"])

    def test_equal_period_length_is_mandatory(self):
        with self.assertRaisesRegex(ValueError,"equal lengths"):
            compare([row("ferry_hub_view",100,"all","ferry_hub")],
                    [row("ferry_hub_view",100,"all","ferry_hub")],7,14,100)

    def test_unobserved_pages_have_unknown_denominators(self):
        before=[row("ferry_hub_view",100,"all","ferry_hub")]
        now=[row("ferry_hub_view",100,"all","ferry_hub")]
        result=compare(before,now,7,7,100)
        route=next(p for p in result["pages"] if p["page"]=="route_tsushima")
        self.assertIsNone(route["prior_views"])
        self.assertIsNone(route["recent_views"])
        self.assertIsNone(route["change_points_per_100_views"])

    def test_clicks_only_do_not_mean_sales(self):
        before=[row("ferry_hub_view",100,"all","ferry_hub"),row("ferry_operator_click",10,"osaka","ferry_hub","booking_instructions")]
        now=[row("ferry_hub_view",100,"all","ferry_hub"),row("ferry_operator_click",11,"osaka","ferry_hub","booking_instructions")]
        result=compare(before,now,7,7)
        self.assertEqual(result["review_candidate_count"],0)
        self.assertTrue(any("NOT ticket sales" in line for line in result["limits"]))

if __name__=="__main__":
    unittest.main()
