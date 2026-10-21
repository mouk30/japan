"""V98 mocked Data API, no external credentials or real GA4 data in CI."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import v98_ga4_data_api as m

class LiveExportTests(unittest.TestCase):
    def metadata(self):
        return {"dimensions":[{"apiName":d} for d in m.DIMENSIONS],
                "metrics":[{"apiName":m.METRIC}]}
    def payload(self,items,row_count=None,metadata=None):
        return {"dimensionHeaders":[{"name":d} for d in m.DIMENSIONS],
                "metricHeaders":[{"name":m.METRIC}],
                "rowCount":str(len(items) if row_count is None else row_count),
                "rows":[{"dimensionValues":[{"value":d} for d in ds],
                         "metricValues":[{"value":str(n)}]} for ds,n in items],
                "metadata":metadata or {}}
    def fake_client(self,items,metadata=None):
        calls=[]
        def fetch(url,payload,token):
            self.assertEqual(token,"synthetic-access-token")
            calls.append((url,payload))
            if url.endswith("/metadata"):return metadata or self.metadata()
            limit=int(payload["limit"]);start=int(payload["offset"])
            return self.payload(items[start:start+limit],row_count=len(items))
        return fetch,calls

    def test_no_property_or_file_is_unknown_not_zero(self):
        self.assertEqual(m.config_status("",""),"missing_ga4_property_id")
        self.assertEqual(m.config_status("G-FAKESTREAM","/nonexistent"),"invalid_ga4_property_id")
        self.assertEqual(m.config_status("1234567",""),"missing_service_account_credentials")

    def test_filter_only_six_approved_event_names(self):
        p=m.create_request()
        self.assertEqual([x["name"] for x in p["dimensions"]],list(m.DIMENSIONS))
        self.assertEqual(p["dimensionFilter"]["filter"]["inListFilter"]["values"],list(m.EVENTS))
        self.assertEqual(p["metrics"][0]["name"],"eventCount")
        self.assertEqual(p["dateRanges"][0],{"startDate":"7daysAgo","endDate":"yesterday"})

    def test_one_real_aggregate_row_mapping_without_personal_data(self):
        d=["ferry_operator_click","osaka","ferry_hub","hub_card","panstar","operator_search"]
        parsed=m.parse_report(self.payload([(d,19)]))
        self.assertEqual(parsed,[{"Event name":"ferry_operator_click","Event count":19,
              "route":"osaka","page_area":"ferry_hub","placement":"hub_card",
              "operator":"panstar","destination_step":"operator_search"}])
        self.assertEqual(set(parsed[0]),set(m.HEADER))

    def test_pagination_all_rows_must_be_present(self):
        first=["ferry_operator_click","osaka","ferry_hub","hub_card","panstar","operator_search"]
        records=[(first,1)]*1002
        fake,calls=self.fake_client(records)
        rows=m.fetch_paginated("1234567","synthetic-access-token",request_func=fake)
        self.assertEqual(len(rows),1002)
        self.assertEqual([x[1]["offset"] for x in calls[1:]],["0","1000"])
        self.assertTrue(calls[0][0].endswith("/metadata"))

    def test_malformed_missing_dim_fails_instead_of_silent_report(self):
        metadata=self.metadata()
        metadata["dimensions"]=[x for x in metadata["dimensions"] if x["apiName"]!="customEvent:route"]
        with self.assertRaisesRegex(m.AnalyticsDataError,"route"):
            m.ensure_metadata(metadata)

    def test_thresholding_and_other_row_not_counted(self):
        d=["ferry_operator_click","tsushima","booking_hub","hub_card","panstar","operator_search"]
        for flag in ("dataLossFromOtherRow","subjectToThresholding"):
            with self.assertRaises(m.AnalyticsDataError):
                m.parse_report(self.payload([(d,7)],metadata={flag:True}))

    def test_partial_pages_abort_without_export(self):
        d=["ferry_operator_click","tsushima","booking_hub","hub_card","panstar","operator_search"]
        def fake(url,payload,token):
            if url.endswith("metadata"):return self.metadata()
            return self.payload([(d,9)],row_count=4)
        with self.assertRaisesRegex(m.AnalyticsDataError,"pagination"):
            m.fetch_paginated("1234567","synthetic-access-token",request_func=fake)

    def test_nonneg_integer_only_and_whitelisted_events(self):
        d=["ferry_operator_click","osaka","ferry_hub","hub_card","panstar","operator_search"]
        raw=self.payload([(d,5)])
        raw["rows"][0]["metricValues"][0]["value"]="-7"
        with self.assertRaisesRegex(m.AnalyticsDataError,"Invalid aggregate"):
            m.parse_report(raw)
        d[0]="purchase"
        with self.assertRaisesRegex(m.AnalyticsDataError,"outside"):
            m.parse_report(self.payload([(d,1)]))

    def test_creds_are_not_logged_or_auto_committed(self):
        row={"Event name":"ferry_operator_click","Event count":8,"route":"fukuoka",
             "page_area":"booking_hub","placement":"hub_card","operator":"koreaferry",
             "destination_step":"booking_search"}
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/"actual-ga4-private.csv"
            m.write_private_csv([row],target)
            with target.open("r",encoding="utf-8") as f:
                read=list(csv.DictReader(f))
            self.assertEqual(len(read),1)
            self.assertEqual(read[0]["Event count"],"8")
            self.assertNotIn("token",target.read_text("utf8").lower())

if __name__=="__main__":unittest.main()
