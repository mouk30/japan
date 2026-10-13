#!/usr/bin/env python3
"""NIPPONFERRY parents guides 15x3 quality: honest photo sources, 4:3 cards, practical mobility guidance.
Existing verified local WebP images are reused with original Wikimedia attribution;
new images are fetched only from an explicit licensed exact-place allowlist.
Do not substitute fictional or neighboring-location photos.
"""
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
import io, re, json, html, time
site=Path("site");venue_dir=site/"images/venues";venue_dir.mkdir(parents=True,exist_ok=True)
report_dir=Path("audit-reports");report_dir.mkdir(parents=True,exist_ok=True)
manifest=json.loads(Path("scripts/parents-v11-manifest.json").read_text(encoding="utf-8"))
specs=manifest["data"]
download_results={}
for asset,filename,author,lic,licurl in manifest["newPhotos"]:
    path=venue_dir/asset
    source="https://commons.wikimedia.org/wiki/File:"+quote(filename.replace(" ","_"),safe="()_,")
    try:
        if not path.exists():
            req=Request("https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(filename,safe="")+"?width=1100",
                headers={"User-Agent":"NipponFerryEditorialParents/1.0 (https://www.nipponferry.com/)","Accept":"image/*"})
            with urlopen(req,timeout=32) as response:
                if not response.headers.get("Content-Type","").startswith("image/"):raise ValueError("non-image response")
                data=response.read(15_000_000)
            img=ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
            img.thumbnail((1100,850),Image.Resampling.LANCZOS)
            img.save(path,"WEBP",quality=82,method=6)
            if path.stat().st_size<3500:raise ValueError("thumbnail unexpectedly small")
        fig=('<figure class="ct-photo nf-parents-photo"><img src="/images/venues/'+asset+'" loading="lazy" decoding="async" width="960" height="720" alt="현장 실사">'
        '<figcaption>사진: '+html.escape(author)+' · '+html.escape(lic)+' · <a href="'+source+'" target="_blank" rel="noopener noreferrer">원본·촬영정보</a> · <a href="'+licurl+'" target="_blank" rel="noopener noreferrer">라이선스</a> · WebP 변환·크기 조정</figcaption></figure>')
        download_results[asset]={"ok":True,"fig":fig,"source":source,"bytes":path.stat().st_size}
    except Exception as e:
        download_results[asset]={"ok":False,"error":str(e)[:200],"source":source}
# Only files with both verified source captions and actual existing images are eligible.
references={}
for page in sorted((site/"things-to-do").glob("*-cruise-*-guide/index.html")):
    if "-parents-" in page.as_posix():continue
    content=page.read_text(encoding="utf8")
    for figure in re.findall(r'<figure\b[^>]*>[\s\S]*?</figure>',content):
        src=re.search(r'<img[^>]*\bsrc="/images/venues/([^"]+\.webp)"',figure)
        if not src or not (venue_dir/src.group(1)).is_file():continue
        if '<figcaption>' not in figure or 'commons.wikimedia.org' not in figure:continue
        references.setdefault(src.group(1),figure)
results=[]
for port,entries in specs.items():
    page=site/"things-to-do"/(port+"-cruise-parents-guide")/"index.html"
    doc=page.read_text(encoding="utf8")
    if len(entries)!=3:raise ValueError("Three cards expected "+port)
    start=doc.find('id="ct-topic-dashboard"')
    end=doc.find('<div class="ct-panel"',start)
    if start<0 or end<0:raise ValueError("TOP3 dashboard missing in "+port)
    part=doc[start:end]
    matches=list(re.finditer(r'<article class="ct-card">([\s\S]*?)</article>',part))
    if len(matches)!=3:raise ValueError("Three TOP3 cards missing "+port)
    updated=0
    for title,asset,note,walking,transit,rest,caution in entries:
        needle='<h3>'+title+'</h3>'
        if part.count(needle)!=1:raise ValueError("TOP3 venue mismatch "+port+" "+title)
        idx=part.find(needle);cut=part.find('</article>',idx)
        original=part[idx:cut]
        # Non-photo mobility support services stay clearly informational. No fake photo.
        figure=None
        image_kind="no_photo_service"
        if asset:
            if asset.startswith("NEW:"):
                obj=download_results.get(asset[4:],{})
                if obj.get("ok"):figure=obj["fig"];image_kind="verified_new"
                else:image_kind="new_photo_unavailable"
            elif (venue_dir/asset).is_file() and asset in references:
                figure=references[asset]
                image_kind="verified_reused"
            else:image_kind="source_unverified"
        if figure:
            alt_text=title+" 관련 실제 장소 사진"+(" (장소 구분은 아래 설명 참고)" if note else "")
            figure=re.sub(r'alt="[^"]*"', 'alt="'+html.escape(alt_text,quote=True)+'"', figure,count=1)
            figure=figure.replace('<figcaption>','<figcaption>'+html.escape(note)+' ',1) if note else figure
            # Replace older remote figure only if a verified self-hosted source is ready.
            original=re.sub(r'<figure\b[^>]*>[\s\S]*?</figure>','',original)
            original=original.replace(needle,needle+figure,1)
        advisory=(
          '<div class="nf-parents-facts">'
          '<div><strong>🚶 걷기·승하차</strong><span>'+html.escape(walking)+'</span></div>'
          '<div><strong>🚕 항만부터 이동</strong><span>'+html.escape(transit)+'</span></div>'
          '<div><strong>🪑 휴식·화장실</strong><span>'+html.escape(rest)+'</span></div>'
          '<div><strong>⚠️ 방문 전 확인</strong><span>'+html.escape(caution)+'</span></div>'
          '</div>')
        if 'nf-parents-facts' not in original:
            original=original.replace('<div class="ct-distance">',advisory+'<div class="ct-distance">',1)
        part=part[:idx]+original+part[cut:]
        results.append({"port":port,"venue":title,"photo":image_kind,"asset":asset,"mobility":True,"reference": (download_results.get(asset[4:],{}).get("source") if asset and asset.startswith("NEW:") else None)})
        updated+=1
    doc=doc[:start]+part+doc[end:]
    if "nf-parents-summary" not in doc:
        lead=('<section id="nf-parents-summary" class="nf-parents-summary" aria-label="부모님 크루즈 편안한 여행 선택 기준">'
          '<p class="nf-parents-eyebrow">부모님 여행 · 무리 없는 기항지 일정</p><h2>관광지를 많이 보는 것보다, 덜 걷고 안전하게 돌아오는 일정</h2>'
          '<p>하선 당일 실제 부두와 승객 게이트부터 확인하세요. 가까운 시설 <strong>1곳 중심</strong>으로 여행을 구성하고, 차량 이동·계단·화장실·앉아 쉬는 시간을 함께 계획하세요.</p>'
          '<div class="nf-parent-key-grid"><div><strong>🚕 항만 픽업</strong><span>실제 접안 부두와 차량 진입 허용 구역·기사를 확인</span></div>'
          '<div><strong>🚶 도보 부담</strong><span>거리 미확인 구간에 임의의 분·미터 수치를 사용하지 않음</span></div>'
          '<div><strong>🪑 휴식</strong><span>시설 내 화장실과 좌석·실내 대안을 미리 확보</span></div>'
          '<div><strong>🚢 귀선 마감</strong><span>출항시각이 아닌 선사의 최종 승객 귀선 마감 기준</span></div></div>'
          '<p class="nf-parent-caution">무장애 시설·승강기는 기항일 실제 가동과 개별 이동 능력에 따라 달라집니다. 실제 이동 시간·휠체어 탑승·당일 이용/예약 여부는 시설·선사·교통업체에 재확인하세요.</p>'
          '<a class="nf-parent-jump" href="#ct-topic-dashboard">부모님 추천 시설 3곳과 걷기·휴식 정보 보기 →</a></section>')
        # Place directly ahead of the existing TOP3 display, following booking/vehicle information.
        pos=doc.find('<section id="ct-topic-dashboard"')
        if pos<0:raise ValueError("TOP3 insertion missing")
        doc=doc[:pos]+lead+doc[pos:]
    if '/companion-card-standard.css' not in doc:
        doc=doc.replace('</head>','<link rel="stylesheet" href="/companion-card-standard.css?v=20261014"></head>',1)
    if '/companion-parents-v11.css' not in doc:
        doc=doc.replace('</head>','<link rel="stylesheet" href="/companion-parents-v11.css?v=20261014"></head>',1)
    page.write_text(doc,encoding="utf8")
summary={"pages":len(specs),"cards":len(results),"photos_new":sum(x["photo"]=="verified_new" for x in results),"photos_reused":sum(x["photo"]=="verified_reused" for x in results),"no_photo_services":sum(x["photo"]=="no_photo_service" for x in results),"photo_unavailable":sum(x["photo"] in ("new_photo_unavailable","source_unverified") for x in results)}
(report_dir/"parents-v11.json").write_text(json.dumps({"summary":summary,"photos":{k:{a:b for a,b in v.items() if a!="fig"} for k,v in download_results.items()},"cards":results},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(summary,ensure_ascii=False))
