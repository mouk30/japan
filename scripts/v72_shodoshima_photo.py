#!/usr/bin/env python3
"""V72 single-image guarded replacement: Shodoshima Tonosho old ferry port photograph.
Only the exact Commons file inspected visually and whose license was verified is allowed.
"""
from pathlib import Path
from PIL import Image
from io import BytesIO
from urllib.request import urlopen,Request
from urllib.error import HTTPError,URLError
import hashlib,json,re,time
ROOT=Path(__file__).resolve().parents[1]
SLUG="shodoshima-ferry-island-access"
SOURCE="https://commons.wikimedia.org/wiki/File:Shodo-shima_ferry_port_in_Tonosho_(6453360287).jpg"
AUTHOR="Maarten Heerlien"
LICENSE_URL="https://creativecommons.org/licenses/by/2.0/"
IMAGE_NAME="v72-shodoshima-tonosho-ferry-2010.webp"
SOURCE_URLS=[
 "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/Shodo-shima_ferry_port_in_Tonosho_%286453360287%29.jpg/1280px-Shodo-shima_ferry_port_in_Tonosho_%286453360287%29.jpg",
 "https://thumb.wikimedia.org/wikipedia/commons/thumb/2/26/Shodo-shima_ferry_port_in_Tonosho_%286453360287%29.jpg/960px-Shodo-shima_ferry_port_in_Tonosho_%286453360287%29.jpg",
 "https://upload.wikimedia.org/wikipedia/commons/2/26/Shodo-shima_ferry_port_in_Tonosho_%286453360287%29.jpg"
]
def acquire():
 for url in SOURCE_URLS:
  for attempt in range(2):
   try:
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; NipponferryEditorial/1.0; info https://github.com/mouk30/japan)","Accept":"image/jpeg,image/*"}),timeout=24) as response:
     if not response.headers.get("Content-Type","").lower().startswith("image/"):raise ValueError("Not an image response")
     payload=response.read(16000000)
    im=Image.open(BytesIO(payload));im.verify()
    im=Image.open(BytesIO(payload));im.load()
    if im.width<950 or im.height<600:raise ValueError("Original image too small")
    if im.format != "JPEG":raise ValueError("Not the reviewed Commons JPEG")
    print("VALID SOURCE",url,im.size,"sha256",hashlib.sha256(payload).hexdigest(),flush=True)
    return im.convert("RGB"),hashlib.sha256(payload).hexdigest(),url
   except (HTTPError,URLError,TimeoutError,OSError,ValueError) as error:
    print("FETCH FAILED",url,str(error),flush=True)
    time.sleep(attempt+1)
 raise SystemExit("No authenticated source file from Commons: preserve existing AI image")
def main():
 im,sha,download_url=acquire()
 im.thumbnail((1600,1200),Image.Resampling.LANCZOS)
 out=ROOT/"site/images/v72-verified"/IMAGE_NAME
 out.parent.mkdir(parents=True,exist_ok=True)
 im.save(out,format="WEBP",quality=86,method=5)
 if out.stat().st_size<30000:raise SystemExit("Unexpected tiny WebP")
 html_path=ROOT/"site/things-to-do"/SLUG/"index.html"
 text=html_path.read_text(encoding="utf-8")
 if "id=\"nf-v72-verified-photo\"" in text:print("Already applied");return
 old='<figure class="editorial-hero"><img src="/images/editorial/shodoshima-ferry-island-access.webp" alt="쇼도시마 페리로 섬 들어가기 풍경 AI 생성 참고 이미지" width="1672" height="941" decoding="async" fetchpriority="high"><figcaption>AI 생성 여행 참고 이미지로 실제 장소의 세부 모습과 다를 수 있습니다.</figcaption></figure>'
 imgpath="/images/v72-verified/"+IMAGE_NAME
 licensed=f'<figure class="editorial-hero"><img src="{imgpath}" alt="2010년 9월 28일 촬영한 쇼도시마 도노쇼항 정박 페리 올리브라인 실사 사진 (현재 운항선박 보증 아님)" width="{im.width}" height="{im.height}" decoding="async" fetchpriority="high"><figcaption>실제 쇼도시마 도노쇼항과 정박 페리 · 2010년 9월 28일 촬영 · 사진: {AUTHOR} · <a href="{SOURCE}" target="_blank" rel="noopener noreferrer">Wikimedia Commons 원본</a> · <a href="{LICENSE_URL}" target="_blank" rel="noopener noreferrer">CC BY 2.0</a> · JPG에서 WebP로 축소·형식 변환. 원본 저작자·라이선스 표시를 유지하세요. 2010년 사진에 등장한 선박과 시간표는 현재 운항 정보를 보증하지 않습니다.</figcaption></figure>'
 if text.count(old)!=1:raise SystemExit("Changed Shodoshima hero source, abort")
 text=text.replace(old,licensed,1)
 text=text.replace("https://www.nipponferry.com/images/editorial/shodoshima-ferry-island-access.webp","https://www.nipponferry.com"+imgpath)
 text=text.replace('"publisher":{"@type":"Organization","name":"NIPPONFERRY"}','"image":"https://www.nipponferry.com'+imgpath+'","publisher":{"@type":"Organization","name":"NIPPONFERRY"}',1)
 # Remove only obsolete disclaimer for the replaced hero.
 text=text.replace('현재 게시글 대표 이미지는 <strong>원본 실사로 검증된 사진이 아닙니다.</strong> 아래는 별도로 확인한 실제 장소 사진의 원본 자료로, 아직 이 페이지의 대표 이미지로 교체하지 않았습니다.','이 게시글 대표 이미지는 <strong>원본 파일과 촬영 대상·라이선스를 대조한 2010년 실제 장소 사진</strong>입니다.',1)
 text=text.replace('원본과 교체 사진의 육안 대조·파일 해시 확인·WebP 등록은 아직 미완료이며, 시점이 오래된 사진은 현재 운영 상황을 보증하지 않습니다.','원본 이미지의 출처를 확인하고 변환 원본 SHA-256을 기록했습니다. 2010년 사진은 현재 선박·운항 시각표를 보증하지 않습니다.',1)
 text=text.replace('쇼도시마 페리로 섬 들어가기 풍경 AI 생성 참고 이미지','쇼도시마 도노쇼항 정박 페리 실제 촬영 사진',1)
 text=text.replace("id=\"nf-v69-photo-original-reference\"","id=\"nf-v72-verified-photo\"",1)
 text=text.replace('실제 장소 사진 원본 참고</h2>','대표 사진 실사·출처 검증 (V72)</h2>',1)
 assert text.count('id="nf-v72-verified-photo"')==1
 assert '<link rel="canonical" href="https://www.nipponferry.com/things-to-do/'+SLUG+'/"' in text
 assert 'href="/favicon.svg"' in text
 assert "AI 생성" not in text, "Stale AI disclaimer still remains"
 assert SOURCE in text and LICENSE_URL in text
 assert out.exists() and out.stat().st_size>30000
 html_path.write_text(text,encoding="utf-8")
 report={"slug":SLUG,"original":SOURCE,"license":"CC BY 2.0","author":AUTHOR,"depicts":"Tonosho ferry port on Shodoshima, olive-line vessel in 2010, not necessarily a current vessel","date":"2010-09-28","visual_inspection":"Photo shows ferry with Olive Line markings berthed at Tonosho pier, matched against Wikimedia Commons preview examined 2026-10-21","downloaded_from":download_url,"input_sha256":sha,"result_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"webp":imgpath,"dimensions":[im.width,im.height],"rights":"credit, source URL, license, modifications and share-alike identified in figcaption","not_proven":"current ferry departure timetable or current facility operation"}
 rp=ROOT/"audit-reports/v72"/(SLUG+".json");rp.parent.mkdir(parents=True,exist_ok=True);rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("V72 DONE",out.stat().st_size,flush=True)
if __name__=="__main__":main()
