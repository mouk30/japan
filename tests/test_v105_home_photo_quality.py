"""V105: regressions for 18 key homepage images; never fabricate photo provenance."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import v105_home_photo_quality as v105

class HomeImageQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/"site/index.html").read_text("utf8")
        cls.manifest=json.loads((ROOT/"scripts/v105_home_photo_manifest.json").read_text("utf8"))

    def test_all_18_home_images_and_licensing_metadata_currently_clean(self):
        r=v105.run()
        self.assertEqual(r["errors"],[])
        self.assertEqual(r["status"],"source_clean")
        self.assertEqual(r["card_counts"],{"popular":8,"daytrips":4,"themes":6})
        self.assertEqual(r["images_inspected"],18)
        self.assertEqual(r["illustrations"],12)
        self.assertEqual(r["licensed_or_reference"],6)

    def test_wrong_region_image_is_rejected_from_pinned_manifest(self):
        html=self.html.replace("/images/editorial/okinawa-kouri-bridge.webp",
                               "/images/venues/kobe-meriken-park-night.webp",1)
        errors,_=v105.audit_markup(html,self.manifest)
        self.assertTrue(any("오키나와" in e and "expected" in e for e in errors),errors)

    def test_wrong_card_target_is_caught(self):
        html=self.html.replace('class="v65-photo" href="/japan/tokyo/"',
                               'class="v65-photo" href="/japan/osaka/"',1)
        errors,_=v105.audit_markup(html,self.manifest)
        self.assertTrue(any("target URL changed" in e for e in errors),errors)

    def test_staged_image_without_disclosure_is_caught(self):
        html=self.html.replace('<span class="v104-photo-origin">여행 분위기 연출 이미지</span>',
                               "",1)
        errors,_=v105.audit_markup(html,self.manifest)
        self.assertTrue(any("staged artwork disclosure disappeared" in e for e in errors),errors)

    def test_photographer_credits_cannot_disappear(self):
        html=self.html.replace("Felix Filnkössl","Unknown Photographer")
        errors,_=v105.audit_markup(html,self.manifest)
        self.assertTrue(any("Licensed photographer attribution missing" in e for e in errors),errors)

    def test_aspect_ratio_must_stay_same(self):
        html=self.html.replace(".v65-photo{display:block;position:relative;aspect-ratio:16/10;",
                               ".v65-photo{display:block;position:relative;aspect-ratio:1/1;")
        errors,_=v105.audit_markup(html,self.manifest)
        self.assertTrue(any("original image aspect ratio" in e for e in errors),errors)

    def test_misleading_true_capture_description_must_not_return(self):
        html=self.html.replace("대표 이미지는 지역 상징 풍경을 우선했습니다.",
             "도쿄 이미지는 실제 야경 사진입니다. 대표 이미지는 지역 상징 풍경을 우선했습니다.")
        errors,_=v105.audit_markup(html,self.manifest)
        self.assertTrue(any("Obsolete photo-origin statement" in e for e in errors),errors)

    def test_missing_image_or_wrong_image_format_is_detected(self):
        info=copy.deepcopy(self.manifest)
        info["sections"]["popular"][0]["src"]="/images/venues/this-image-is-intentionally-missing.webp"
        errors,_=v105.audit_assets(ROOT,info)
        self.assertTrue(any("source image not in repository" in e for e in errors),errors)

    def test_too_strict_resolution_budget_causes_explicit_review(self):
        info=copy.deepcopy(self.manifest)
        info["image_format_rules"]["minimum_width"]=5000
        errors,_=v105.audit_assets(ROOT,info)
        self.assertTrue(any("unexpectedly small" in e for e in errors),errors)

    def test_image_root_does_not_accept_url_traversal(self):
        info=copy.deepcopy(self.manifest)
        info["sections"]["popular"][0]["src"]="/images/../../.github/workflows/no-image.webp"
        errors,_=v105.audit_assets(ROOT,info)
        self.assertTrue(any("source image not in repository" in e for e in errors),errors)

    def test_v104_browser_qa_targets_still_match_manifest(self):
        self.assertEqual(v105.audit_v104_reference(ROOT,self.manifest),[])

    def test_alt_text_must_describe_actual_regional_subject(self):
        html=self.html.replace("오사카 도톤보리 강변의 글리코 간판과 네온 야경",
                               "도쿄 여행 스카이트리 전경",1)
        errors,_=v105.audit_markup(html,self.manifest)
        self.assertTrue(any("alt description" in e and "오사카" in e for e in errors),errors)

    def test_themed_staged_images_are_not_implicitly_treated_as_photos(self):
        info=copy.deepcopy(self.manifest)
        info["sections"]["themes"][1]["kind"]="reference"
        errors,_=v105.audit_markup(self.html,info)
        self.assertTrue(any("non-staged image incorrectly marked" in e for e in errors),errors)

if __name__=="__main__":unittest.main()
