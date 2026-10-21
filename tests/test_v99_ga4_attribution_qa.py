"""V99: validate actual-source event taxonomy with artificial unit-test fixtures only."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from v99_ga4_attribution_qa import analyze,markdown

def e(name="ferry_operator_click",count=12,route="osaka",area="ferry_hub",
      placement="hub_card",provider="panstar",step="operator_search"):
    return {"event":name,"count":count,"route":route,"page_area":area,
            "placement":placement,"operator":provider,"destination_step":step}

class AttributionQualityTests(unittest.TestCase):
    def test_four_routes_correct_operators(self):
        rows=[e(count=10,route="osaka"),
              e(count=10,route="tsushima"),
              e(count=10,route="fukuoka",provider="koreaferry",step="booking_search"),
              e(count=10,route="shimonoseki",provider="kampuferry",step="booking_instructions")]
        result=analyze(rows)
        self.assertEqual(result["status"],"clean_attribution")
        self.assertEqual(result["operator_clicks"],40)
        self.assertEqual(result["problem_events"],0)

    def test_wrong_provider_triggers_manual_inspection(self):
        result=analyze([e(count=35,route="tsushima",provider="koreaferry")])
        self.assertEqual(result["status"],"requires_manual_measurement_review")
        self.assertEqual(result["problem_events"],35)
        self.assertEqual(result["issues"][0]["reason"],"route_operator_mismatch")

    def test_page_source_unknown_detected(self):
        result=analyze([e(count=22,area="(not set)")])
        self.assertEqual(result["missing_metadata_events"],22)
        self.assertEqual(result["issues"][0]["reason"],"page_area_unknown")

    def test_information_only_not_claimed_as_reservation(self):
        result=analyze([e(name="ferry_info_open",count=20)])
        self.assertIsNone(result["operator_clicks"])
        self.assertEqual(result["status"],"no_verifiable_outbound_click_data")

    def test_low_sample_is_not_called_proven(self):
        result=analyze([e(count=3)])
        self.assertEqual(result["status"],"small_sample_unreliable")
        self.assertIn("small",result["status"])

    def test_kampu_booking_instructions_not_checkout(self):
        result=analyze([e(count=30,route="shimonoseki",provider="kampuferry",step="booking_search")])
        self.assertEqual(result["issues"][0]["reason"],"shimonoseki_instructions_mislabeled_checkout")

    def test_bad_fukuoka_main_cta_classification(self):
        result=analyze([e(count=30,route="fukuoka",provider="koreaferry",step="operator_home")])
        self.assertTrue(any(z["reason"]=="fukuoka_main_cta_not_booking_calendar" for z in result["issues"]))

    def test_real_report_clearly_says_not_purchases(self):
        result=analyze([e(count=35)])
        self.assertIn("발권/구매가 아닌",markdown(result))

if __name__=="__main__":unittest.main()
