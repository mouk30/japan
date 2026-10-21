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

    def test_v101_previous_refused_korean_link_is_no_longer_used(self):
        old = "https://www.kampuferry.co.jp/lang_kor/reserve/"
        self.assertNotEqual(cfg["routes"]["shimonoseki"]["primary"],old)
        self.assertEqual(cfg["routes"]["shimonoseki"]["primary"],"https://kampuferry.co.jp/reserve/")
        self.assertEqual(cfg["routes"]["shimonoseki"]["secondary"],"https://kampuferry.co.jp/yoyaku/en/reservation.html")
        for path in [
          "site/guide/busan-shimonoseki-ferry/index.html",
          "site/guide/busan-shimonoseki-ferry-price/index.html",
          "site/guide/busan-shimonoseki-timetable/index.html",
          "site/ferry/index.html",
          "site/booking/japan-cruise/index.html",
        ]:
            self.assertNotIn(old,(ROOT/path).read_text("utf8"),path)

    def test_v101_japanese_official_booking_content_is_acceptable(self):
        url=cfg["routes"]["shimonoseki"]["primary"]
        page="<html><title>関釜フェリー</title><body>フェリーのご予約 ご予約方法 インターネット予約</body></html>"
        checked=v90.evaluate_response(url,Response(200,url,text=page),
                     cfg,"kampuferry","reservation_instructions")
        self.assertEqual(checked["classification"],"operator_landing_verified")

    def test_404_is_suspected_broken(self):
        x=v90.evaluate_response("https://kampuferry.co.jp/yoyaku/en/reservation.html",Response(404,"https://kampuferry.co.jp/yoyaku/en/reservation.html"),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(x["classification"],"suspected_broken")

    def test_403_429_do_not_mean_broken(self):
        for code in (401,403,429,503):
            x=v90.evaluate_response("https://kampuferry.co.jp/yoyaku/en/reservation.html",Response(code,"https://kampuferry.co.jp/yoyaku/en/reservation.html"),cfg,"kampuferry","reservation_instructions")
            self.assertEqual(x["classification"],"unverified")

    def test_wrong_domain_or_deep_link_to_home(self):
        src="https://kampuferry.co.jp/reserve/"
        bad=v90.evaluate_response(src,Response(200,"https://malicious.example/reserve/"),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(bad["reason"],"redirected_to_unexpected_domain")
        wrong=v90.evaluate_response(src,Response(200,"https://www.kampuferry.co.jp/"),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(wrong["reason"],"deep_link_redirected_to_operator_home")

    def test_200_route_redirect_to_other_operator_path_needs_review(self):
        url="https://www.panstarcruise.com/product/osaka/info"
        moved=v90.evaluate_response(url,Response(200,"https://www.panstarcruise.com/product/daemado/info",
                             text="<html><title>Panstar Cruise</title><body>Tsushima Express</body></html>"),cfg,
                             "panstar","route_info")
        self.assertEqual(moved["classification"],"needs_review")
        self.assertEqual(moved["reason"],"specific_booking_or_route_path_changed")

    def test_200_correct_path_without_route_content_is_unverified(self):
        url="https://www.panstarcruise.com/product/osaka/info"
        changed=v90.evaluate_response(url,Response(200,url,text="<html><title>Panstar Cruise</title><body>General products</body></html>"),cfg,
                             "panstar","route_info")
        self.assertEqual(changed["classification"],"unverified")
        self.assertEqual(changed["reason"],"route_specific_content_not_visible")

    def test_long_unrelated_200_body_is_actionable_wrong_screen(self):
        url="https://www.panstarcruise.com/product/osaka/info"
        page="<html><title>Other products</title><body>" + ("completely unrelated entertainment shopping " * 15) + "</body></html>"
        value=v90.evaluate_response(url,Response(200,url,text=page),cfg,"panstar","route_info")
        self.assertEqual(value["classification"],"needs_review")
        self.assertEqual(value["reason"],"substantial_unexpected_operator_content")

    def test_long_correct_operator_wrong_route_is_actionable(self):
        url="https://www.panstarcruise.com/product/osaka/info"
        page="<html><title>Panstar Cruise</title><body>" + ("Tsushima Ferry departure information " * 13) + "</body></html>"
        value=v90.evaluate_response(url,Response(200,url,text=page),cfg,"panstar","route_info")
        self.assertEqual(value["classification"],"needs_review")
        self.assertEqual(value["reason"],"wrong_route_or_unrelated_official_content")

    def test_same_domain_unrelated_page_requires_investigation(self):
        src="https://kampuferry.co.jp/reserve/"
        wrong=v90.evaluate_response(src,Response(200,src,"<html><title>Shop</title><body>limited period sale</body></html>"),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(wrong["classification"],"unverified")

    def test_valid_landing_is_not_inventory_claim(self):
        url="https://kampuferry.co.jp/yoyaku/en/reservation.html"
        v=v90.evaluate_response(url,Response(200,url),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(v["classification"],"operator_landing_verified")

    def test_new_camellia_blank_response_is_not_verified_booking(self):
        url=cfg["routes"]["fukuoka"]["primary"]
        empty=v90.evaluate_response(url,Response(200,url,text="<html><title></title><body></body></html>"),
                                      cfg,"koreaferry","booking_calendar_search")
        self.assertEqual(empty["classification"],"unverified")

    def test_new_camellia_real_calendar_content_is_verified(self):
        url=cfg["routes"]["fukuoka"]["primary"]
        calendar=v90.evaluate_response(url,Response(200,url,
                     text="<html><title>뉴카멜리아 온라인예약</title><body>STEP.1공실조회 최저가 달력 총 인원 검색</body></html>"),
                     cfg,"koreaferry","booking_calendar_search")
        self.assertEqual(calendar["classification"],"operator_landing_verified")

    def test_new_camellia_wrong_page_title_only_is_unverified(self):
        url=cfg["routes"]["fukuoka"]["primary"]
        wrong=v90.evaluate_response(url,Response(200,url,
                   text="<html><title>뉴카멜리아 공지사항</title><body>고려훼리 예약 안내</body></html>"),
                   cfg,"koreaferry","booking_calendar_search")
        self.assertEqual(wrong["reason"],"actual_booking_calendar_not_visible")

    def test_non_html_download_is_not_valid_landing(self):
        url="https://kampuferry.co.jp/yoyaku/en/reservation.html"
        v=v90.evaluate_response(url,Response(200,url,"hello",ctype="application/pdf"),cfg,"kampuferry","reservation_instructions")
        self.assertEqual(v["reason"],"non_html_destination")

if __name__=="__main__":unittest.main()
