"""Deterministic V90 safety tests; 403 != broken, redirect-to-home and unrelated domain are suspect."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("v90", ROOT/"scripts/v90_booking_destination_health.py")
v90=importlib.util.module_from_spec(spec);spec.loader.exec_module(v90)
cfg=json.loads((ROOT/"scripts/v90_booking_link_targets.json").read_text("utf8"))

class Response:
    def __init__(self,code,url,text="<html><title>Kampu Ferry Online Reservation</title><p>Online Reservation and passenger booking</p></html>",ctype="text/html",history=None):
        self.status_code=code;self.url=url;self.text=text
        self.headers={"content-type":ctype};self.history=history or []

class V90Tests(unittest.TestCase):
    def test_all_six_existing_page_anchors_point_to_expected_routes(self):
        r=v90.examine_local(cfg)
        self.assertEqual(r["errors"],[],str(r["errors"]))
        self.assertEqual(len(r["routes"]),4)

    def test_404_is_suspected_broken(self):
        x=v90.evaluate_response("https://www.kampuferry.co.jp/yoyaku/en/",Response(404,"https://www.kampuferry.co.jp/yoyaku/en/"),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(x["classification"],"suspected_broken")

    def test_403_429_do_not_mean_broken(self):
        for code in (401,403,429,503):
            x=v90.evaluate_response("https://www.kampuferry.co.jp/yoyaku/en/",Response(code,"https://www.kampuferry.co.jp/yoyaku/en/"),cfg,"kampuferry","reservation_instructions")
            self.assertEqual(x["classification"],"unverified")

    def test_wrong_domain_or_deep_link_to_home(self):
        src="https://www.kampuferry.co.jp/lang_kor/reserve/"
        bad=v90.evaluate_response(src,Response(200,"https://malicious.example/reserve/"),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(bad["reason"],"redirected_to_unexpected_domain")
        wrong=v90.evaluate_response(src,Response(200,"https://www.kampuferry.co.jp/"),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(wrong["reason"],"deep_link_redirected_to_operator_home")

    def test_same_domain_unrelated_page_requires_investigation(self):
        src="https://www.kampuferry.co.jp/lang_kor/reserve/"
        wrong=v90.evaluate_response(src,Response(200,src,"<html><title>Shop</title><body>limited period sale</body></html>"),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(wrong["classification"],"unverified")

    def test_valid_landing_is_not_inventory_claim(self):
        url="https://www.kampuferry.co.jp/yoyaku/en/"
        v=v90.evaluate_response(url,Response(200,url),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(v["classification"],"operator_landing_verified")

    def test_non_html_download_is_not_valid_landing(self):
        url="https://www.kampuferry.co.jp/yoyaku/en/"
        v=v90.evaluate_response(url,Response(200,url,"hello",ctype="application/pdf"),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(v["reason"],"non_html_destination")

if __name__=="__main__":unittest.main()
