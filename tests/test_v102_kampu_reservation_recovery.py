"""V102 static + live verification without requiring customer network success."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import v102_kampu_reservation_recovery as q

class KampuTests(unittest.TestCase):
    def test_all_existing_site_and_registry_urls_migrated(self):
        self.assertEqual(q.verify_sources(),[])

    def test_public_old_site_is_not_mistaken_for_fully_deployed(self):
        v=q.inspect_deployed_html('<a href="'+q.OLD+'">예약</a>',q.NEW,"https://site.example")
        self.assertEqual(v["status"],"old_link_still_published")

    def test_new_official_link_is_identified(self):
        doc='<a href="'+q.NEW+'">Japanese official reservations</a>'
        self.assertEqual(q.inspect_deployed_html(doc,q.NEW,"test")["status"],"corrected_link_visible")

    def test_missing_target_detected_as_deployment_incomplete(self):
        self.assertEqual(q.inspect_deployed_html("<html></html>",q.NEW,"test")["status"],"replacement_not_visible")

    def test_actual_live_status_distinguishes_partial_vs_complete(self):
        def old_fetch(url):
            return '<a href="'+(q.OLD if "/ferry/" in url else q.NEW)+'">official</a>'
        state=q.live_check(fetch=old_fetch)
        self.assertEqual(state["status"],"production_old_link_pending_deployment")
        ready=q.live_check(fetch=lambda _: '<a href="'+q.NEW+'">official</a>')
        self.assertEqual(ready["status"],"production_updated")

    def test_fetch_errors_are_not_called_broken_or_verified(self):
        from urllib.error import URLError
        def blocked(_):raise URLError("network blocked")
        status=q.live_check(fetch=blocked)
        self.assertEqual(status["status"],"production_incomplete_or_unverifiable")
        self.assertTrue(all(x["status"]=="fetch_unavailable" for x in status["pages"]))

if __name__=="__main__":unittest.main()
