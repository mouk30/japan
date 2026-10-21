"""Offline regression fixtures for the V88 source interpretation and no-auto-edit policy."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/v88_official_watch.py"
spec = importlib.util.spec_from_file_location("v88_module", MODULE_PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class V88MonitorTests(unittest.TestCase):
    def test_panstar_only_new_relevant_announcements(self):
        doc = BeautifulSoup("""
        <main>
         <a href="/support/notice/307">10월 20일~21일 결항 안내</a>
         <a href="/support/notice/309">회원 가입 이벤트</a>
         <a href="/support/notice/310">대마도 항로 유류할증료 변경 안내</a>
        </main>""", "html.parser")
        found = m.notice_index(doc, "panstar")
        self.assertEqual(sorted(found), [307,309,310])
        self.assertTrue(any(word in found[310]["title"] for word in m.NOTICE_WORDS))
        self.assertFalse(any(word in found[309]["title"] for word in m.NOTICE_WORDS))

    def test_korea_notices_are_scoped_to_ferry_board(self):
        doc = BeautifulSoup("""
         <a href="board.php?bo_table=ferry_notice&wr_id=41">2027년 TAX 변경</a>
         <a href="board.php?bo_table=other&wr_id=42">일반 상품 광고</a>""", "html.parser")
        found = m.notice_index(doc, "koreaferry")
        self.assertEqual(list(found), [41])

    def test_kampu_fuel_row_does_not_match_cabin_fares(self):
        doc = BeautifulSoup("""
        <table><tr><td>2등실</td><td>12,000엔</td><td>120,000원</td></tr>
         <tr><th>유류할증료</th><td>만1세 이상 1,900엔</td><td>19,000원</td></tr>
         <tr><td>국제관광여객세</td><td>3,000엔</td></tr></table>""", "html.parser")
        self.assertEqual(m.fuel_fee_row(doc)["busan_krw"],19000)
        self.assertEqual(m.fuel_fee_row(doc)["shimonoseki_jpy"],1900)
        self.assertEqual(m.fuel_fee_row(BeautifulSoup("<table><tr><td>12,000엔</td></tr></table>", "html.parser")),None)

    def test_fingerprints_not_affected_by_key_order(self):
        self.assertEqual(m.official_signature({"fare":19000,"status":"review"}),
                         m.official_signature({"status":"review","fare":19000}))

    def test_semantic_notice_hash_ignores_view_count_but_detects_image_change(self):
        first = BeautifulSoup('<div>조회 120회</div><div id="bo_v_con">TAX 공지 <img src="/img/q4.png"></div>', "html.parser")
        second = BeautifulSoup('<div>조회 999회</div><div id="bo_v_con">TAX 공지 <img src="/img/q4.png"></div>', "html.parser")
        changed = BeautifulSoup('<div>조회 999회</div><div id="bo_v_con">TAX 공지 <img src="/img/q1.png"></div>', "html.parser")
        self.assertEqual(m.semantic_document(first, "koreaferry"), m.semantic_document(second, "koreaferry"))
        self.assertNotEqual(m.semantic_document(BeautifulSoup('<div id="bo_v_con">TAX 공지 <img src="/img/q4.png"></div>', "html.parser"), "koreaferry"),
                            m.semantic_document(changed, "koreaferry"))

    def test_same_url_fuel_image_byte_change_is_observable(self):
        import hashlib
        class Response:
            status_code = 200
            url = "https://koreaferry.kr/data/tax.png"
            headers = {"Content-Type": "image/png"}
            def __init__(self, content):
                self.content = content
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def iter_content(self, chunk_size=65536):
                yield self.content
        class Session:
            def __init__(self, payload):
                self.payload = payload
            def get(self, url, **kwargs):
                return Response(self.payload)
        doc = BeautifulSoup('<article id="bo_v_con"><img src="/data/tax.png"><img src="https://evil.example/a.png"></article>', "html.parser")
        first = m.korea_ferry_tax_images(Session(b"image-binary-v1"), doc, "https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice&wr_id=39")
        second = m.korea_ferry_tax_images(Session(b"image-binary-v2"), doc, "https://koreaferry.kr/eng/bbs/board.php?bo_table=ferry_notice&wr_id=39")
        url = "https://koreaferry.kr/data/tax.png"
        self.assertEqual(list(first), [url])
        self.assertEqual(first[url]["status"], "ok")
        self.assertNotEqual(first[url]["sha256"], second[url]["sha256"])
        self.assertEqual(first[url]["sha256"], hashlib.sha256(b"image-binary-v1").hexdigest())

    def test_unverified_source_not_taken_as_price(self):
        self.assertIsNone(m.fuel_fee_row(None))
        self.assertEqual(m.notice_index(None,"panstar"),{})

if __name__=="__main__":
    unittest.main()
