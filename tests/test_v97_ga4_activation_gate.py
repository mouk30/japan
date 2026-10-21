"""V97 Production tag-readiness checks — no real Measurement ID or GA4 requests."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import v97_ga4_activation_gate as m

def html_page(path, test_id=None, css=True, src=True):
    html = '<!doctype html><html><head><link rel="canonical" href="'+m.BASE+path+'">'
    if css:
        html += '<link rel="stylesheet" href="/nf-v93-booking-clicks.css?v=test">'
    html += '</head><body>'
    if test_id is not None:
        uri = '/nf-v93-booking-clicks.js?v=test' if src else '/wrong.js'
        html += '<script defer data-nf-ga4="'+test_id+'" src="'+uri+'"></script>'
    return html + '</body></html>'

class ActivationGateTests(unittest.TestCase):
    def fake_pages(self, ga4=None, missing_css=False, broken_asset=False, second_id=None):
        def fake(url):
            path = url[len(m.BASE):]
            if path in m.PAGES:
                idx = m.PAGES.index(path)
                identifier = second_id if second_id and idx==1 else ga4
                body = html_page(path, identifier, not missing_css)
                return {"ok":True,"body":body,"status":200,"final_host":"www.nipponferry.com"}
            if path.startswith("/nf-v93-booking-clicks.js"):
                body = "ferry_operator_click and analytics_storage" if not broken_asset else "old irrelevant script"
                return {"ok":True,"body":body,"status":200,"final_host":"www.nipponferry.com"}
            if path.startswith("/nf-v93-booking-clicks.css"):
                return {"ok":True,"body":".nf93-consent{}","status":200,"final_host":"www.nipponferry.com"}
            return {"ok":False,"status":404}
        return fake

    def test_missing_ga4_shows_not_connected_and_no_fake_counts(self):
        x = m.production_report(self.fake_pages())
        self.assertEqual(x["status"],"not_connected")
        self.assertIsNone(x["actual_event_counts"])
        self.assertFalse(any(p["configured"] for p in x["pages"]))

    def test_configured_and_healthy_requires_all_four_pages(self):
        x = m.production_report(self.fake_pages(ga4="G-TEST123456"))
        self.assertEqual(x["status"],"installed_ready_for_owner_realtime_test")
        self.assertEqual(len(x["assets"]),2)
        self.assertTrue(all(a["ok"] for a in x["assets"]))
        self.assertNotIn("G-TEST123456", str(x))

    def test_different_stream_across_pages_must_alert(self):
        x = m.production_report(self.fake_pages(ga4="G-TEST123456",second_id="G-CHANGED4567"))
        self.assertEqual(x["status"],"inconsistent_partial_deployment")

    def test_missing_consent_css_must_alert(self):
        x = m.production_report(self.fake_pages(ga4="G-TEST123456",missing_css=True))
        self.assertEqual(x["status"],"inconsistent_partial_deployment")

    def test_missing_js_functionality_is_not_called_activated(self):
        x = m.production_report(self.fake_pages(ga4="G-TEST123456",broken_asset=True))
        self.assertEqual(x["status"],"installed_but_missing_or_wrong_asset")

    def test_public_invalid_ga4_tag_cannot_count_as_active(self):
        x = m.inspect_html(html_page("/",test_id="NOT-A-GA4-ID"), "/")
        self.assertFalse(x["configured"])

    def test_canonical_must_be_preserved(self):
        x = m.inspect_html(html_page("/ferry/",test_id="G-TEST123456"), "/ferry/")
        self.assertTrue(x["canonical_unchanged"])
        self.assertTrue(x["has_defer"])

if __name__ == "__main__":
    unittest.main()
