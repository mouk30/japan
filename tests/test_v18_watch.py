#!/usr/bin/env python3
"""V18 deterministic change-detection tests without touching official sources."""
import io, json, os, pathlib, runpy, tempfile, unittest
from unittest.mock import patch
SCRIPT=pathlib.Path(__file__).resolve().parents[1]/'scripts/v18-official-source-watch.py'
class Reply(io.BytesIO):
    status=200
class WatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        (self.root/'scripts').mkdir()
        (self.root/'scripts/v17-official-sailings.json').write_text(
            json.dumps({'ports':{'test-port':{'scheduleSource':'https://example.invalid/official'}}}),encoding='utf8')
        self.prev=os.getcwd()
        os.chdir(self.root)
        self.addCleanup(lambda:os.chdir(self.prev))
    def run_scan(self, payload=b'first', fail=False):
        import sys
        before=sys.argv
        sys.argv=[str(SCRIPT),'--previous','baseline.json','--output','out']
        try:
            with patch('urllib.request.urlopen',side_effect=OSError('offline') if fail else lambda req,timeout:Reply(payload)):
                runpy.run_path(str(SCRIPT),run_name='__main__')
        finally:
            sys.argv=before
        report=json.loads((self.root/'out/report.json').read_text())
        snap=json.loads((self.root/'out/snapshot.json').read_text())
        return report,snap
    def keep_baseline(self,snap):
        (self.root/'baseline.json').write_text(json.dumps(snap),encoding='utf8')
    def test_first_scan_creates_baseline(self):
        report,snap=self.run_scan()
        self.assertTrue(report['baseline_created'])
        self.assertEqual(report['changed_sources'],[])
        self.assertEqual(snap['sources']['test-port']['status'],'ok')
    def test_same_document_not_reported_as_change(self):
        _,base=self.run_scan()
        self.keep_baseline(base)
        report,_=self.run_scan()
        self.assertEqual(report['changed_sources'],[])
        self.assertEqual(report['action'],'NO_CHANGE_DETECTED')
    def test_changed_document_requires_manual_review(self):
        _,base=self.run_scan()
        self.keep_baseline(base)
        report,_=self.run_scan(b'second')
        self.assertEqual(report['changed_sources'],['test-port'])
        self.assertEqual(report['action'],'MANUAL_EVIDENCE_REVIEW_REQUIRED')
    def test_failed_fetch_preserves_prior_good_hash(self):
        _,base=self.run_scan()
        self.keep_baseline(base)
        report,current=self.run_scan(fail=True)
        self.assertTrue(report['fetch_warnings'])
        self.assertEqual(current['sources']['test-port']['sha256'],base['sources']['test-port']['sha256'])
if __name__=='__main__':
    unittest.main()
