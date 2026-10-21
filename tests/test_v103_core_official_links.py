"""V103: audit official ferry source links without confusing bot defense with dead links."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v103",ROOT/"scripts/v103_core_official_links.py")
v103=importlib.util.module_from_spec(spec);spec.loader.exec_module(v103)

class V103Tests(unittest.TestCase):
    def test_all_14_source_pages_official_ctas_and_canonicals(self):
        inventory=v103.inventory()
        self.assertEqual(len(inventory["pages"]),14)
        self.assertEqual(inventory["errors"],[],str(inventory["errors"]))
        self.assertGreater(len(inventory["occurrences"]),12)

    def test_404_410_are_actionable(self):
        for code in (404,410):
            result=v103.evaluate_url("https://kampuferry.co.jp/reserve/",code)
            self.assertEqual(result["classification"],"needs_review")

    def test_403_429_500_and_502_cannot_be_declared_permanent_failures(self):
        for code in (403,429,500,502):
            result=v103.evaluate_url("https://www.koreaferry.kr/",code)
            self.assertEqual(result["classification"],"unverified")

    def test_redirect_to_non_operator_domain_requires_review(self):
        result=v103.evaluate_url("https://www.panstarcruise.com/product/osaka/info",
                                 200,"https://shopping.example.com/deals")
        self.assertEqual(result["reason"],"unexpected_final_domain")

    def test_cross_operator_redirect_requires_review(self):
        result=v103.evaluate_url("https://www.panstarcruise.com/product/osaka/info",
                                 200,"https://www.koreaferry.kr/")
        self.assertEqual(result["reason"],"cross_operator_or_port_authority_redirect")

    def test_www_alias_stays_valid_on_same_operator(self):
        result=v103.evaluate_url("https://www.kampuferry.co.jp/reserve/",
                                 200,"https://kampuferry.co.jp/reserve/")
        self.assertEqual(result["classification"],"reached_official_html")

    def test_specific_url_to_home_is_review_candidate_even_if_200(self):
        result=v103.evaluate_url("https://kampuferry.co.jp/yoyaku/en/reservation.html",
                                 200,"https://kampuferry.co.jp/")
        self.assertEqual(result["reason"],"deep_link_became_generic_homepage")

    def test_successful_200_is_only_http_access_not_booking_success(self):
        result=v103.evaluate_url("https://kampuferry.co.jp/reserve/",200)
        self.assertEqual(result["classification"],"reached_official_html")
        self.assertIn("without_claiming_correct_booking_content",result["reason"])

    def test_bad_http_and_unknown_content_are_unverified(self):
        for code in (302,401):
            self.assertEqual(v103.evaluate_url("https://kampuferry.co.jp/reserve/",code)["classification"],"unverified")
        self.assertEqual(v103.evaluate_url("https://kampuferry.co.jp/reserve/",200,content_type="application/pdf")["classification"],"unverified")

    def test_report_without_online_calls_is_explicit(self):
        report=v103.run(live=False)
        self.assertEqual(report["scope_pages"],14)
        self.assertEqual(report["online_probes"],[])
        self.assertEqual(report["unverified"],[])
        self.assertIn("HTTP 200",report["notes"][0])

    def test_refused_kampu_reservation_url_must_not_return(self):
        inv=v103.inventory()
        self.assertNotIn("https://www.kampuferry.co.jp/lang_kor/reserve/",inv["occurrences"])
        self.assertNotIn("https://www.pukwan.co.kr/",inv["occurrences"])

if __name__=="__main__":
    unittest.main()
