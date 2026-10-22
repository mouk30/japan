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
        self.assertEqual(r["illustrations"],10)
        self.assertEqual(r["licensed_or_reference"],8)

    def test_v109_all_documentary_cards_have_origin_metadata(self):
        photos={item["src"] for items in self.manifest["sections"].values()
                for item in items if item["kind"]!="illustrative"}
        credited={item["src"] for item in self.manifest["licensed_credits"]}
        self.assertEqual(photos,credited)
        self.assertEqual(len(photos),8)
        image="/images/venues/osaka-kaiyukan-aquarium.webp"
        metadata=json.loads((ROOT/"site/images/venues/osaka-kaiyukan-aquarium.source.json").read_text("utf8"))
        self.assertEqual(metadata["git_blob_sha1"],"d3344df4055136ca831da376ba708538c6267ce3")
        self.assertEqual(metadata["photographer"],"Sakai Yayoi")
        self.assertEqual(metadata["license"],"CC0 1.0")
        self.assertEqual(metadata["original"],"https://commons.wikimedia.org/wiki/File:Kaiy%C5%ABkan.jpg")
        self.assertIn("Sakai Yayoi",self.html)
        errors,_=v105.audit_assets(ROOT,self.manifest)
        self.assertEqual(errors,[])
        lacking=copy.deepcopy(self.manifest)
        lacking["licensed_credits"]=[x for x in lacking["licensed_credits"] if x["src"]!=image]
        errors,_=v105.audit_assets(ROOT,lacking)
        self.assertTrue(any("V109 homepage documentary/reference photos lack source credits" in e for e in errors))

    def test_v109_osaka_detail_photo_and_seo_retained(self):
        article=(ROOT/"site/things-to-do/osaka-one-day/index.html").read_text("utf8")
        self.assertIn('<link rel="canonical" href="https://www.nipponferry.com/things-to-do/osaka-one-day/">',article)
        self.assertIn('application/ld+json',article)
        self.assertIn('og:image" content="https://www.nipponferry.com/images/venues/nf-v85-osaka-dotonbori-licensed.webp"',article)
        self.assertNotIn("/images/venues/osaka-dotonbori.webp",article)
        self.assertIn("Kristoffer Trolle",article)
        self.assertIn("CC BY 2.0",article)

    def test_v108_theme_cards_images_and_provenance(self):
        cards=v105.extract_cards(self.html)["themes"]
        expectations=[
          (0,"돈코츠","/images/culture-verified/ramen-japanese-noodle-evolution.webp","reference"),
          (1,"돈키호테","/images/culture-verified/shotengai-japanese-shopping-arcades.webp","reference"),
          (2,"에이사","/images/editorial/okinawa-eisa-dance-festival.webp","illustrative"),
          (3,"커플","/images/couple.jpg","illustrative"),
          (4,"가비라만","/images/editorial/ishigaki-kabira-bay.webp","illustrative"),
          (5,"편의점","/images/culture-verified/konbini-japanese-convenience-store-life.webp","reference"),
        ]
        for pos,subject,src,kind in expectations:
            with self.subTest(subject=subject):
                self.assertEqual(cards[pos]["images"][0]["src"],src)
                self.assertIn(subject,cards[pos]["images"][0]["alt"])
                self.assertEqual(self.manifest["sections"]["themes"][pos]["kind"],kind)
                self.assertEqual("v63-photo-disclosure" in cards[pos]["labels"],kind=="illustrative")
        for name in ("Syced","Mugu-shisai","Yuya Tamai","bryan...","Saigen Jiro"):
            self.assertIn(name,self.html)
        self.assertEqual(len(self.manifest["licensed_credits"]),8)

    def test_v107_regional_cards_reuse_matching_existing_place_images(self):
        expected=[
            (1,"가이유칸","/images/venues/osaka-kaiyukan-aquarium.webp"),
            (2,"가라토시장","/images/venues/v62-karato-market-real.webp"),
            (3,"이즈하라항","/images/venues/v62-izuhara-port-real.webp"),
        ]
        actual=v105.extract_cards(self.html)["daytrips"]
        for pos,place,src in expected:
            with self.subTest(place=place):
                self.assertEqual(actual[pos]["images"][0]["src"],src)
                self.assertIn(place,actual[pos]["images"][0]["alt"])
                self.assertEqual(self.manifest["sections"]["daytrips"][pos]["kind"],"reference")
                self.assertNotIn("v104-photo-origin",actual[pos]["labels"])
        for place,url,src in [
            ("시모노세키","shimonoseki-one-day","/images/venues/v62-karato-market-real.webp"),
            ("대마도","tsushima-one-day","/images/venues/v62-izuhara-port-real.webp"),
        ]:
            detail=(ROOT/"site/things-to-do"/url/"index.html").read_text("utf8")
            with self.subTest(detail=place):
                self.assertIn('property="og:image" content="https://www.nipponferry.com'+src+'"',detail)

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

    def test_same_filename_image_bytes_cannot_change_silently(self):
        info=copy.deepcopy(self.manifest)
        info["sections"]["popular"][0]["git_blob_sha1"]="0"*40
        errors,_=v105.audit_assets(ROOT,info)
        self.assertTrue(any("image bytes changed since visual approval" in e for e in errors),errors)

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
        info["sections"]["themes"][2]["kind"]="reference"
        errors,_=v105.audit_markup(self.html,info)
        self.assertTrue(any("non-staged image incorrectly marked" in e for e in errors),errors)

if __name__=="__main__":unittest.main()
