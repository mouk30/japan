#!/usr/bin/env python3
"""V158 extra Miyakojima factual operations and SEO/media regression.
Independent of remote baseline; verifies existing indexed guide, local licensed
photo and the new official entry / booking / safe-return action panel.
"""
from html.parser import HTMLParser
from pathlib import Path
from collections import Counter
import re, json, xml.etree.ElementTree as ET

root = Path("site")
file = root / "things-to-do/hirara-miyakojima-cruise-port-day-trip/index.html"
html = file.read_text(encoding="utf-8")
class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[]; self.links=[]; self.img=[]; self.h1=0; self.canon=[]; self.desc=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if "id" in a: self.ids.append(a["id"])
        if tag=="a": self.links.append(a.get("href", ""))
        if tag=="img": self.img.append(a)
        if tag=="h1": self.h1+=1
        if tag=="link" and a.get("rel")=="canonical": self.canon.append(a.get("href",""))
        if tag=="meta" and a.get("name")=="description": self.desc.append(a.get("content",""))
p=Tags();p.feed(html)
start=html.find('<section id="nf-v158-miyakojima"')
end=html.find('<section id="v71-verification"',start)
panel=html[start:end] if start>=0 and end>start else ""
checks={
 "one_official_panel":p.ids.count("nf-v158-miyakojima")==1,
 "three_decision_cards":panel.count('class="nf-v158-step"')==3,
 "panel_visible_before_original":start>=0 and end>start,
 "original_guide_present":p.ids.count("v71-verification")==1,
 "government_source_link": "https://www.city.miyakojima.lg.jp/soshiki/shityo/kensetsu/kouwan/oshirase/2024-0222-0902-121.html" in p.links,
 "operator_real_booking_portal":"https://act.shigira.com/top/filedleisure?lng=en-US" in p.links,
 "confirmed_operational_details":all(x in panel for x in ["렌터카 인도","2026년 9월 28일","12월 28일","선박검사","귀선","집합장소","취소 조건"]),
 "no_undocumented_ship_pickup":all(x in panel for x in ["항만 구내가 아닌","크루즈 승객 전용 귀선 교통이 아닙니다"]),
 "all_external_links_newtab_safe":all('rel="noopener noreferrer"' in a for a in re.findall(r'<a\\b[^>]*href="https?[^"]+"[^>]*>',panel)),
 "no_fake_reservation_assertions":not any(x in panel for x in ["예약 확정","실시간 잔여석 확보","무료 셔틀 보장"]),
 "single_h1":p.h1==1,
 "original_canonical":p.canon==["https://www.nipponferry.com/things-to-do/hirara-miyakojima-cruise-port-day-trip/"],
 "description_present":len(p.desc)==1 and len(p.desc[0])>30,
 "unchanged_specific_webp":any(x.get("src")=="/images/venues/miyakojima-yonaha-maehama.webp" and "2024년" in x.get("alt","") and x.get("width")=="1150" and x.get("height")=="766" for x in p.img),
 "all_local_images_exist":all((root/x.get("src","").lstrip("/").split("?")[0]).is_file() for x in p.img if x.get("src","").startswith("/") and not x.get("src","").startswith("//")),
 "original_photo_attribution":"https://commons.wikimedia.org/wiki/File:202408_Yonaha_Maehama_Beach_around_11_o%27clock_in_summer_(JK-DSC0765).jpg" in p.links and "https://creativecommons.org/licenses/by-sa/4.0/" in p.links,
 "unique_html_ids":len(p.ids)==len(set(p.ids)),
 "mobile_large_touch_targets":'id="nf-v158-operation-styles"' in html and "@media(max-width:700px)" in html and "min-height:52px" in html,
 "sitemap_still_lists_existing": "https://www.nipponferry.com/things-to-do/hirara-miyakojima-cruise-port-day-trip/" in [u.find("{*}loc").text for u in ET.parse(root/"sitemap.xml").getroot().findall("{*}url")]
}
failures=[k for k,v in checks.items() if not v]
report={"version":"V158","guide":"hirara-miyakojima-cruise-port-day-trip","new_articles":0,"real_time_booking_stock_or_private_analytics_checked":False,"checks":checks,"failures":failures}
out=Path("audit-output/v158");out.mkdir(parents=True,exist_ok=True)
(out/"miyakojima-official-gate-closed-tour-return.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
print("Miyakojima V158 QA",sum(checks.values()),"/",len(checks),"failures:",failures)
if failures:raise SystemExit(1)
