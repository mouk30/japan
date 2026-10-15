#!/usr/bin/env python3
"""V42 finalize: 52-image metadata/copyright audit after 11 verified replacements.

Do not represent pre-existing editorial artwork without source records as original
documentary photography. Preserve original URL/SEO copy and the unique comparison
illustration for kimono/yukata.
"""
import html,json,re
from pathlib import Path

SITE=Path("site"); OUT=Path("docs/v42-image-audit")
old=json.loads((OUT/"inventory.json").read_text("utf-8"))
new=json.loads(Path("docs/v42-deployed-photo-credits.json").read_text("utf-8"))
assert len(old["rows"])==52 and len(new)==11
changed={r["slug"]:r for r in new}
hubpath=SITE/"things-to-do/index.html"
hub=hubpath.read_text("utf-8")
rows=[]
for oldrow in old["rows"]:
    slug=oldrow["slug"]
    articlefile=SITE/"things-to-do"/slug/"index.html"
    page=articlefile.read_text("utf-8")
    key=f'href="/things-to-do/{slug}/"'
    i=hub.find(key)
    assert i>=0,slug
    b=hub.find("</a>",i)
    assert b>=0,slug
    card=hub[i:b]
    match=re.search(r'<img\b[^>]*\bsrc="([^"]+)"',card)
    assert match,slug
    asset=match.group(1)
    assert asset.startswith("/images/"),(slug,asset)
    assert (SITE/asset.lstrip("/")).is_file(),slug
    assert f'src="{asset}"' in page,(slug,"article cover missing")
    url="https://www.nipponferry.com"+asset
    # Social meta values must align with corresponding selected hero.
    for meta in ('og:image','twitter:image'):
        attr='property' if meta=='og:image' else 'name'
        pat=re.compile(r'<meta\b(?=[^>]*\b'+attr+r'\s*=\s*["\']'+re.escape(meta)+r'["\'])[^>]*>',re.I)
        replacement=f'<meta {attr}="{meta}" content="{url}">'
        if pat.search(page):page=pat.sub(replacement,page,count=1)
        else:page=page.replace("</head>",replacement+"\n</head>",1)
    assert f'<meta property="og:image" content="{url}">' in page,slug
    assert f'<meta name="twitter:image" content="{url}">' in page,slug
    # A two-person kimono/yukata comparison is purpose-made editorial artwork,
    # not a documentary photograph of a named real-life location.
    if slug=="kimono-vs-yukata-culture":
        part=hub[i:b]
        part=part.replace("<em>주제 참고 이미지</em>","<em>복식 비교 편집 이미지</em>")
        part=part.replace("게시글 대표 이미지","복식 비교 편집 이미지")
        hub=hub[:i]+part+hub[b:]
        if "v42-comparison-note" not in page:
            note=('<p class="v42-comparison-note" style="font-size:12px;line-height:1.65;color:#657b90">'
                  '위 대표 그림은 기모노와 유카타의 특징을 함께 이해하기 위한 비교 편집 이미지로, '
                  '특정 인물·착용 장소의 현장 촬영 기록이 아닙니다.</p>')
            # Add note after the lead image, preserving original markup.
            img=re.search(r'<img\b[^>]*src="/images/editorial/kimono-yukata-hero\.webp"[^>]*>',page)
            assert img,slug
            page=page[:img.end()]+note+page[img.end():]
    # For other editorial imagery without verified provenance, avoid labels
    # that could be read as independently verified documentary photography.
    if slug not in changed and slug!="kimono-vs-yukata-culture":
        has_source="commons.wikimedia.org/wiki/File:" in page and bool(re.search(r'CC BY(?:-SA)?|CC0|Public domain',page,re.I))
        if not has_source:
            start=hub.find(key)
            end=hub.find("</a>",start)
            card=hub[start:end]
            card=card.replace("<em>게시글 대표 이미지</em>","<em>주제 편집 이미지</em>",1)
            card=card.replace("<em>주제 참고 이미지</em>","<em>주제 편집 이미지</em>",1)
            hub=hub[:start]+card+hub[end:]
    articlefile.write_text(page,encoding="utf-8")
    source_match=re.search(r'https://commons\.wikimedia\.org/wiki/File:[^"\s<>]+',page)
    has_cc=bool(re.search(r'CC BY(?:-SA)?\s*[1-4](?:\.\d)?|CC0|Public domain',page,re.I))
    credit=changed.get(slug)
    original_status=("V42-photo-and-attribution-verified" if credit else
        "prior-photo-credit-visible" if source_match and has_cc else
        "editorial-or-undocumented-source")
    rows.append({
      "slug":slug,"title":oldrow["title"],"previous_class":oldrow["category"],
      "image":asset,"article":f"/things-to-do/{slug}/",
      "in_article":True,"og_matches":True,"twitter_matches":True,
      "provenance":original_status,
      "photo_source":credit["source_page"] if credit else (source_match.group(0) if source_match and has_cc else None),
      "licence":credit["licence"] if credit else None,
      "limitation":("A comparative editorial visual; not a verified documentary photo" if slug=="kimono-vs-yukata-culture" else
         "Existing source authorship/license not yet separately verified" if not credit and not (source_match and has_cc) else ""),
    })
hubpath.write_text(hub,encoding="utf-8")
summary={
"total":52,
"new_verified_real_photos":sum(x["provenance"]=="V42-photo-and-attribution-verified" for x in rows),
"prior_pages_with_visible_source_licence":sum(x["provenance"]=="prior-photo-credit-visible" for x in rows),
"editorial_or_unverified_source":sum(x["provenance"]=="editorial-or-undocumented-source" for x in rows),
"webp_files_present":sum((SITE/x["image"].lstrip("/")).is_file() for x in rows),
"hero_matches":len(rows),"og_matches":len(rows),"twitter_matches":len(rows),
"visual_review":"contact sheets visually reviewed by editor; source-uncertain artwork is not claimed to be a verified camera photograph",
"changed_card_count":11,"comparative_editorial_kept":["kimono-vs-yukata-culture"]}
assert summary["new_verified_real_photos"]==11
assert summary["webp_files_present"]==52
(OUT/"finalized-52.json").write_text(json.dumps({"summary":summary,"rows":rows},ensure_ascii=False,indent=2),encoding="utf-8")

# Update the inventory's subjects, but separate verified photos from existing
# unverified editorial reference art; do not inflate source-verified counts.
auditpath=Path("docs/v36-hub-cards-audit.json")
audit=json.loads(auditpath.read_text("utf-8"))
index={x["slug"]:x for x in rows}
for row in audit["things"]["mappings"]:
    if row["slug"] not in index:continue
    current=index[row["slug"]]
    row["image"]=current["image"]
    if row["slug"] in changed:
       row["kind"]="verified-real-photo"
       row["photo_source"]=changed[row["slug"]]["source_page"]
       row["licence"]=changed[row["slug"]]["licence"]
    elif row["slug"]=="kimono-vs-yukata-culture":
       row["kind"]="editorial-comparison"
    elif row["kind"] in ("exact","topic"):
       row["kind"]=("previously-credited-photo" if current["provenance"]=="prior-photo-credit-visible" else "editorial-unverified")
counts={}
for row in audit["things"]["mappings"]:counts[row["kind"]]=counts.get(row["kind"],0)+1
audit["things"]["kinds"]=counts
audit["last_quality_refresh"]="2026-10-15 V42"
audit["v42"]={
 "audit_total":52,"source_verified_replacements":11,"existing_credit_visible":summary["prior_pages_with_visible_source_licence"],
 "editorial_or_unverified":summary["editorial_or_unverified_source"],
 "html_metadata_verified":52,"unfixed_hero_links":0,"unfixed_og_links":0,"unfixed_twitter_links":0,
 "source_register":"docs/v42-deployed-photo-credits.json","finalized_inventory":"docs/v42-image-audit/finalized-52.json",
 "production_http_test":"docs/v42-live-qa.json"}
audit["caveat"]="V37-V42 source-verified new Commons WebP photo upgrades: 111 cards (100 previous + 11 new). V42 checked all remaining 52 visually and technically; 40 original matched-asset cards include both previously credited real photographs and editorial imagery without independently documented provenance; kimono/yukata retains explicitly labelled comparative editorial art. 52/52 metadata links repaired; production HTTP QA and mobile/desktop crop QA are separate."
auditpath.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"summary":summary,"audit_counts":counts},ensure_ascii=False,indent=2),flush=True)
