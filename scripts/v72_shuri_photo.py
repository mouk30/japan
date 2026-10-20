#!/usr/bin/env python3
"""V72 single-image guarded replacement: Shuri Castle roof restoration photograph (February 2025).
Only the exact Commons file inspected visually and whose license was verified is allowed.
"""
from pathlib import Path
from PIL import Image
from io import BytesIO
from urllib.request import urlopen,Request
from urllib.error import HTTPError,URLError
import hashlib,json,re,time
ROOT=Path(__file__).resolve().parents[1]
SLUG="okinawa-shuri-castle"
SOURCE="https://commons.wikimedia.org/wiki/File:Shuri_Castle_Reconstruction.jpg"
AUTHOR="おにく"
LICENSE_URL="https://creativecommons.org/publicdomain/zero/1.0/"
IMAGE_NAME="v72-shuri-reconstruction-feb2025.webp"
SOURCE_URLS=[
 "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Shuri_Castle_Reconstruction.jpg/1280px-Shuri_Castle_Reconstruction.jpg",
 "https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1f/Shuri_Castle_Reconstruction.jpg/960px-Shuri_Castle_Reconstruction.jpg",
 "https://upload.wikimedia.org/wikipedia/commons/1/1f/Shuri_Castle_Reconstruction.jpg"
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
 im.save(out,"WEBP",quality=86,method=5)
 if out.stat().st_size<30000:raise SystemExit("Suspiciously small WebP")
 html_path=ROOT/"site/things-to-do"/SLUG/"index.html"
 text=html_path.read_text(encoding="utf-8")
 if 'id="nf-v72-verified-photo"' in text:
  print("Already done");return
 old='<img class="hero" src="/images/editorial/okinawa-shuri-castle.webp" width="1600" height="900" alt="오키나와 슈리성 여행 이해를 돕는 참고 이미지(실제 현장 사진 여부 미검증)" loading="eager">'
 image_path="/images/v72-verified/"+IMAGE_NAME
 new=f'<img class="hero" src="{image_path}" width="{im.width}" height="{im.height}" alt="2025년 2월 11일 슈리성 정전 지붕 복원 공사 중 비계와 붉은 기와 실사, 현재 완공 모습 아님" loading="eager" decoding="async">'
 if text.count(old)!=1:raise SystemExit("Hero mismatch")
 text=text.replace(old,new,1)
 credit=f'<p id="nf-v72-verified-photo" class="note"><strong>실제 장소 사진 · 2025년 공사 당시:</strong> 슈리성 정전 기와 지붕 복원 공사 · 2025년 2월 11일 촬영 · 사진: {AUTHOR} · <a href="{SOURCE}" target="_blank" rel="noopener noreferrer">Wikimedia Commons 원본</a> · <a href="{LICENSE_URL}" target="_blank" rel="noopener noreferrer">CC0 1.0</a> · 원본 JPG에서 WebP로 크기 및 파일 형식 변경 · 현재 완공된 정전 모습이 아닙니다.</p>'
 text=text.replace(new,new+credit,1)
 fixes=[
  ("이 이미지는 여행 이해를 위한 참고자료입니다. 촬영지 일치·실제 현장 사진 여부·사용 권한은 아직 독립 검증되지 않았습니다.","이 이미지는 슈리성 정전의 2025년 실제 복원공사 사진이며 원본과 CC0 이용 조건을 대조했습니다."),
  ("이미지는 이해를 돕기 위한 AI 생성 이미지이며 실제 현장 사진이 아닙니다.","실제 2025년 복원공사 장면입니다. 현재 정전의 완공 모습이 아닙니다."),
  ("AI 여행 참고 이미지는 실제 시설 상태와 다를 수 있습니다.","2025년 복원 공사 사진은 현재 시설 모습과 다를 수 있습니다."),
  ("이미지 실사 여부와 상업적 이용 권한은 별도로 검증해야 합니다.","대표 사진 원본과 CC0 사용 조건은 확인했지만 현재 운영 상태는 별도 확인해야 합니다."),
  ("사진: 현장 및 권리 검증 대기.</strong> 기존 사진의 위치·실사 여부·이용 허락을 이번 디자인 변경만으로 확인 완료로 처리하지 않습니다.","사진: 2025년 공사 사진 검증.</strong> Wikimedia Commons 원본과 CC0 조건을 확인했으나 현재 시설 상태는 별도 확인해야 합니다."),
  ("복원 과정의 과거 사진이나 AI 이미지가 현재 정전 내부의 실제 모습을 보여주는 것처럼 오인하지 않도록 주의하세요.","위 2025년 2월 복원공사 사진을 현재 정전 내부의 완공 모습으로 오인하지 않도록 주의하세요."),
  ("본문에 표기된 이미지 유형은 유지합니다. 실제 장소 사진 원본·저작권 사용조건·현재 현장 일치 여부는 미검증이므로 사진을 실제 촬영물로 단정하지 않습니다.","대표 사진은 2025년 공사 현장의 실제 촬영본으로 출처·CC0 이용 조건을 확인했습니다. 사진의 촬영 시점과 현재 시설 상태는 구분하세요."),
  ("현재 게시글 대표 이미지는 <strong>원본 실사로 검증된 사진이 아닙니다.</strong> 아래는 별도로 확인한 실제 장소 사진의 원본 자료로, 아직 이 페이지의 대표 이미지로 교체하지 않았습니다.","현재 대표 이미지는 <strong>원본과 촬영 장소·CC0 조건을 확인한 2025년 슈리성 복원공사 사진</strong>입니다."),
  ("원본과 교체 사진의 육안 대조·파일 해시 확인·WebP 등록은 아직 미완료이며, 시점이 오래된 사진은 현재 운영 상황을 보증하지 않습니다.","2025년 원본에서 WebP로 변환하고 SHA-256을 기록했습니다. 현재 완공·운영상태는 보증하지 않습니다."),
  ("id=\"nf-v69-photo-original-reference\"","id=\"nf-v72-historic-photo-reference\""),
  ("실제 장소 사진 원본 참고</h2>","대표 사진 실제 촬영 기록 (V72)</h2>")
 ]
 for oldstr,newstr in fixes:
  if oldstr not in text:raise SystemExit("Expected phrase missing: "+oldstr[:50])
  text=text.replace(oldstr,newstr,1)
 text=text.replace("/images/editorial/okinawa-shuri-castle.webp",image_path)
 assert "AI 생성" not in text
 assert 'href="/favicon.svg"' in text
 assert "https://www.nipponferry.com/things-to-do/"+SLUG+"/" in text
 assert SOURCE in text and LICENSE_URL in text
 html_path.write_text(text,encoding="utf-8")
 report={"slug":SLUG,"source":SOURCE,"creator":AUTHOR,"license":"CC0 1.0","photo_date":"2025-02-11","visual_observation":"Photograph of red tiled Seiden roof within scaffolding under construction shelter, not completed Shuri Castle","checked_preview":"Reviewed Wikimedia Commons official preview 2026-10-21","source_download_url":download_url,"input_sha256":sha,"webp":image_path,"dimensions":[im.width,im.height],"output_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"limitation":"The photograph does not establish current castle completion or admission status"}
 rp=ROOT/"audit-reports/v72"/(SLUG+".json");rp.parent.mkdir(parents=True,exist_ok=True);rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("V72 Shuri source photo published",out.stat().st_size)
if __name__=="__main__":main()
