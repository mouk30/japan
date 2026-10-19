#!/usr/bin/env python3
"""Synthetic unit tests ONLY. Do not treat test rows as real search performance."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location("report_longtail_3_search",Path(__file__).parent/"report_longtail_3_search.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ImportChecks(unittest.TestCase):
    def save(self,data):
        self.d=tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)
        path=Path(self.d.name)/"gsc.csv"
        path.write_text(data,encoding="utf-8-sig")
        return path

    def test_realistic_english_export(self):
        file=self.save(
            "Top pages,Clicks,Impressions,CTR,Position\n"
            "https://www.nipponferry.com/japan-cruise/busan-hakata-ferry-reservation/,4,100,4%,9.5\n"
            "https://www.nipponferry.com/japan-cruise/bukan-ferry-shimonoseki-price/,0,20,0%,14.5\n"
            "https://www.nipponferry.com/random-other/,100,1000,10%,1\n")
        found=mod.load(file)
        self.assertEqual(len(found),2)
        self.assertEqual(found["/japan-cruise/busan-hakata-ferry-reservation/"]["ctr_percent"],4.0)
        self.assertEqual(found["/japan-cruise/bukan-ferry-shimonoseki-price/"]["clicks"],0)
        self.assertNotIn(mod.TARGETS["panstar_cabins"],found)

    def test_korean_export_and_query_url(self):
        file=self.save(
            "상위 페이지,클릭수,노출수,게재순위\n"
            "https://nipponferry.com/japan-cruise/panstar-miracle-osaka-cabin-types?source=qr,3,70,12.5\n")
        found=mod.load(file)
        self.assertEqual(found[mod.TARGETS["panstar_cabins"]]["impressions"],70)

    def test_query_only_export_rejected(self):
        file=self.save("Top queries,Clicks,Impressions\npanstar,4,100\n")
        with self.assertRaisesRegex(ValueError,"URL별 페이지"):
            mod.load(file)

    def test_duplicate_pages_rejected_not_double_counted(self):
        url="https://www.nipponferry.com/japan-cruise/busan-hakata-ferry-reservation/"
        file=self.save(f"Page,Clicks,Impressions\n{url},1,20\n{url},2,50\n")
        with self.assertRaisesRegex(ValueError,"중복"):
            mod.load(file)

    def test_bad_numbers_rejected(self):
        file=self.save("Page,Clicks,Impressions\n/japan-cruise/busan-hakata-ferry-reservation/,1.5,10\n")
        with self.assertRaises(ValueError):
            mod.load(file)

if __name__=="__main__":
    unittest.main()
