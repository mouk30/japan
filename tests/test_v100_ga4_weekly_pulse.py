"""V100: end-to-end private read-only GA4 weekly pulse regression. Synthetic values ONLY."""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import v100_ga4_weekly_pulse as pulse

def row(name,count,route="osaka",area="ferry_hub",placement="hub_card",operator="panstar",step="operator_search"):
    return {"Event name":name,"Event count":count,"route":route,"page_area":area,
            "placement":placement,"operator":operator,"destination_step":step}

def recent_data(clicks=30,views=120,wrong=False):
    op = "koreaferry" if wrong else "panstar"
    return [row("ferry_hub_view",views,route="all",placement="page",operator="internal",step="hub_view"),
            row("ferry_operator_click",clicks,operator=op)]

class V100Tests(unittest.TestCase):
    def temp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root=Path(tmp.name)
        credential=root/"private.service-account.json"
        credential.write_text('{"dummy":"NO REAL KEY"}',"utf8")
        return root,credential

    def fake(self,recent=None,previous=None):
        calls=[]
        def fetch(property_id,token,start,end):
            self.assertEqual(property_id,"1234567")
            self.assertEqual(token,"synthetic-token-only")
            calls.append((start,end))
            if start == "2026-10-15":
                return recent if recent is not None else []
            if start == "2026-10-08":
                return previous if previous is not None else []
            raise AssertionError("Unexpected date window "+start)
        return fetch,calls

    def test_two_nonoverlapping_completed_kst_weeks(self):
        result=pulse.windows(dt.date(2026,10,22))
        self.assertEqual(result["recent"],{"start":"2026-10-15","end":"2026-10-21"})
        self.assertEqual(result["previous"],{"start":"2026-10-08","end":"2026-10-14"})
        self.assertEqual(result["timezone"],"Asia/Seoul")

    def test_unconnected_account_never_calls_google_or_invents_clicks(self):
        root,_=self.temp()
        def forbidden(*args):raise AssertionError("No outgoing calls without credentials")
        result=pulse.execute("","",as_of=dt.date(2026,10,22),output=root/"out",
                             fetcher=forbidden,token_loader=forbidden)
        self.assertEqual(result["status"],"awaiting_account_connection")
        self.assertIsNone(result["actual_click_counts"])
        self.assertFalse((root/"out"/"recent-dashboard").exists())
        self.assertFalse((root/"out"/"recent-actual.ga4.actual.csv").exists())

    def test_current_only_real_aggregate_creates_private_chart_without_false_change(self):
        root,credential=self.temp()
        fetch,calls=self.fake(recent=recent_data(),previous=[])
        result=pulse.execute("1234567",credential,as_of=dt.date(2026,10,22),
                             output=root/"out",fetcher=fetch,token_loader=lambda _: "synthetic-token-only")
        self.assertEqual(result["status"],"current_only_no_baseline")
        self.assertEqual(result["current_booking_entry_clicks"],30)
        self.assertIsNone(result["previous_booking_entry_clicks"])
        self.assertIsNone(result["trend_review_candidates"])
        self.assertEqual(len(calls),2)
        self.assertTrue((root/"out"/"recent-dashboard"/"dashboard.html").exists())
        self.assertFalse((root/"out"/"trend-review.json").exists())

    def test_two_valid_periods_produce_real_data_marked_comparison_and_review(self):
        root,credential=self.temp()
        fetch,calls=self.fake(recent=recent_data(clicks=10),previous=recent_data(clicks=45))
        result=pulse.execute("1234567",credential,as_of=dt.date(2026,10,22),
                             output=root/"out",fetcher=fetch,token_loader=lambda _: "synthetic-token-only")
        self.assertEqual(result["status"],"insufficient_current_click_sample")
        self.assertEqual(result["current_booking_entry_clicks"],10)
        self.assertEqual(result["previous_booking_entry_clicks"],45)
        self.assertTrue((root/"out"/"trend-review.json").exists())
        trend=json.loads((root/"out"/"trend-review.json").read_text("utf8"))
        self.assertEqual(trend["review_candidate_count"],1)
        self.assertTrue(all(not ("private_key" in str(x)) for x in (result,trend)))
        self.assertEqual(calls,[("2026-10-15","2026-10-21"),("2026-10-08","2026-10-14")])

    def test_sufficient_current_and_previous_clicks_can_be_qualified(self):
        root,credential=self.temp()
        fetch,_=self.fake(recent=recent_data(clicks=36),previous=recent_data(clicks=40))
        result=pulse.execute("1234567",credential,as_of=dt.date(2026,10,22),
                             output=root/"out",fetcher=fetch,token_loader=lambda _: "synthetic-token-only")
        self.assertEqual(result["status"],"qualified_weekly_review_ready")
        self.assertEqual(result["confirmed_bookings"],None)

    def test_bad_current_operator_blocks_rank_before_private_csv(self):
        root,credential=self.temp()
        fetch,calls=self.fake(recent=recent_data(clicks=22,wrong=True),previous=recent_data())
        result=pulse.execute("1234567",credential,as_of=dt.date(2026,10,22),
                             output=root/"out",fetcher=fetch,token_loader=lambda _: "synthetic-token-only")
        self.assertEqual(result["status"],"current_attribution_review")
        self.assertEqual(len(calls),1)
        self.assertIsNone(result["actual_click_counts"])
        self.assertFalse((root/"out"/"recent-dashboard").exists())

    def test_incomplete_api_error_does_not_generate_comparison(self):
        from v98_ga4_data_api import AnalyticsDataError
        root,credential=self.temp()
        def broken(*args):raise AnalyticsDataError("Partial GA4 report")
        result=pulse.execute("1234567",credential,as_of=dt.date(2026,10,22),
                             output=root/"out",fetcher=broken,token_loader=lambda _: "synthetic-token-only")
        self.assertEqual(result["status"],"source_unavailable")
        self.assertIsNone(result["actual_click_counts"])
        self.assertFalse((root/"out"/"recent-dashboard").exists())

    def test_previous_period_with_wrong_attribution_never_compares_weeks(self):
        root,credential=self.temp()
        fetch,_=self.fake(recent=recent_data(clicks=30),previous=recent_data(clicks=30,wrong=True))
        result=pulse.execute("1234567",credential,as_of=dt.date(2026,10,22),
                             output=root/"out",fetcher=fetch,token_loader=lambda _: "synthetic-token-only")
        self.assertEqual(result["status"],"prior_attribution_review")
        self.assertIsNone(result["trend_review_candidates"])
        self.assertFalse((root/"out"/"trend-review.json").exists())

    def test_invalid_calendar_period_rejected(self):
        with self.assertRaises(ValueError):
            pulse.windows(dt.date(2026,10,22),days=0)
        with self.assertRaises(ValueError):
            pulse.windows(dt.datetime(2026,10,22),days=7)

if __name__=="__main__":unittest.main()
