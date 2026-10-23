#!/usr/bin/env python3
"""V143: existing-section content rescue with verified imagery and sitewide audit.
No page creation. Strict guards; preserve SEO, links, other content and layout.
"""
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from collections import Counter,defaultdict
from html import escape
from hashlib import sha256
import json, re, io, time, os
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
OUT=ROOT/"audit-reports/v143"
OUT.mkdir(parents=True,exist_ok=True)
SOURCE="https://commons.wikimedia.org/wiki/File:%E7%AC%AC65%E5%9B%9E%E3%81%95%E3%81%A3%E3%81%BD%E3%82%8D%E9%9B%AA%E3%81%BE%E3%81%A4%E3%82%8A%EF%BC%88SAPPORO_SNOW_FESTIVAL_65th%EF%BC%89_-_panoramio_(1).jpg"
FILENAME="第65回さっぽろ雪まつり（SAPPORO SNOW FESTIVAL 65th） - panoramio (1).jpg"
PHOTO="/images/venues/nf-v143-sapporo-snow-festival-2014-real.webp"
AUTHOR="t-konno"
LIC="https://creativecommons.org/licenses/by-sa/3.0/"
OFFICIAL="https://www.snowfes.com/"
SAPPORO="https://www.sapporo.travel/en/event/event-list/sapporo_snow_festival/"
JNTO="https://faq.japan-travel.jnto.go.jp/en/plan/wifi-and-connectivity/"

def b(title, desc):return (title,desc)
winter={
 "sapporo-snow-festival-2027":(
  "2027 눈축제 실제 방문 순서",
  [b("축제 일정은 2027년 2월 4~11일","오도리·스스키노·쓰도무 3개 회장의 날짜는 주최 측 공지 기준입니다. 세부 행사·체험 운영시간은 공개 시점마다 달라질 수 있으므로 출발 전 공식 회장별 안내를 다시 확인하세요."),
   b("오도리 회장: 대형 눈조각부터","오도리공원을 따라 대형·소형 눈조각을 감상하는 중심 관람 구역입니다. 혼잡한 시간에는 한쪽 방향으로 천천히 이동하고, 사진 촬영 시간을 별도로 잡는 편이 좋습니다."),
   b("스스키노 회장: 얼음조각·야경","도심의 얼음조각 전시를 보며 이동하는 구역입니다. 바닥이 미끄럽고 야간 기온이 내려가므로 짧은 관람과 실내 휴식을 묶어 계획하세요."),
   b("쓰도무 회장: 가족형 눈 체험","도심 오도리·스스키노와 위치가 다릅니다. 삿포로 지하철 도호선 사카에마치역 접근과 현장 이동안내를 출발 전 확인하고, 아이 체험 운영·안전 조건을 따로 체크하세요."),
   b("관람 전 체크리스트","방수 방한 신발, 보온 장갑, 휴대전화 보조배터리, 귀가 교통편을 준비하세요. 날씨가 악화되면 회장별 동선을 줄이고 지하철·실내 공간 위주로 변경하세요.")]),
 "sapporo-snow-festival-family":(
  "아이와 함께 보는 눈축제 코스",
  [b("회장을 한꺼번에 다 돌지 마세요","유모차·어린아이 동행이라면 쓰도무 체험과 오도리 눈조각 관람을 나눠 일정에 넣는 편이 여유롭습니다. 체험 가능 나이와 안전수칙은 공식 발표를 확인하세요."),
   b("도심에서는 오도리 중심으로","화장실·실내 휴식처를 먼저 확인하고 눈조각 관람은 구역을 좁혀 진행하세요. 매번 따뜻한 실내로 돌아올 수 있도록 계획하는 것이 중요합니다."),
   b("이동 선택","쓰도무는 도심과 거리가 있습니다. 사카에마치역·행사장 간 실제 이동 수단을 공식 안내로 확인하고, 아이가 피곤하면 한 회장만 선택해도 괜찮습니다."),
   b("귀가와 방한","발이 젖을 경우를 대비한 여분 양말·장갑, 간식, 보조배터리와 가족 연락처를 준비하세요. 어두워지기 전에 숙소 복귀 경로를 다시 확인하세요.")]),
 "sapporo-snow-festival-couple":(
  "연인 동행: 야간과 휴식을 함께",
  [b("오도리 눈조각부터 시작","해가 지기 전 전체 구도를 살펴보고 야간 조명 관람은 공식 점등 안내를 확인해 시간대를 결정하세요."),
   b("스스키노 얼음조각 연계","오도리 관람 후 스스키노로 이동하면 장소 성격이 달라집니다. 야간 얼음길에서는 사진을 위해 길 한복판에 오래 멈추지 마세요."),
   b("따뜻한 휴식 동선","관람 전후로 카페 또는 실내 식당을 한 번씩 넣고, 한겨울 옷차림에 맞춰 도보 거리를 짧게 구성하세요."),
   b("예약 시 확인","눈축제 기간 숙박과 인기 식당은 혼잡할 수 있습니다. 취소 조건을 확인하고 도심 역 주변 숙소를 우선 비교하세요.")]),
 "sapporo-snow-festival-2n3d":(
  "2박 3일, 회장별로 나누는 일정",
  [b("1일차: 삿포로 시내 적응","도착 시간에 맞춰 숙소에 짐을 맡기고 도심 이동수단을 확인합니다. 늦은 도착이면 스스키노를 짧게 걷는 정도로 마무리하세요."),
   b("2일차: 오도리와 쓰도무 중 선택","눈조각 중심이라면 오도리 구간을 충분히, 체험 중심 가족이라면 쓰도무 이동을 우선 배정하세요. 두 회장 모두 무리하게 넣지 않아도 됩니다."),
   b("3일차: 귀국·이동 여유","교통 상황과 겨울철 운행 지연 가능성을 고려해 관광을 길게 늘리지 말고 공항·역 이동을 우선하세요."),
   b("예약 우선순위","숙소 취소 규정, 지하철 역 접근성, 눈길 도보 부담, 공항 복귀 교통편을 순서대로 확인하세요.")]),
 "sapporo-snow-festival-3n4d":(
  "3박 4일, 관람과 휴식을 분리",
  [b("1일차: 도심 이동·숙소 확인","삿포로역과 숙소 간 보행거리 및 지하 통로 이용 가능 여부를 확인하고 가벼운 근거리 산책으로 시작하세요."),
   b("2일차: 오도리 + 스스키노","오도리 눈조각과 스스키노 얼음조각을 다른 시간대로 나눠 관람하세요. 야간 관람 전에는 실내에서 충분히 휴식하세요."),
   b("3일차: 쓰도무 또는 근교","아이 체험이 목적이면 쓰도무를, 조용한 여행이면 삿포로 시내 다른 관광을 선택하세요. 눈길 이동 상황에 따라 유연하게 바꾸세요."),
   b("4일차: 이동 우선","신치토세공항 또는 다음 이동지에 가야 한다면 겨울철 지연 가능성을 고려해 체크아웃 후 이동 시간을 넉넉히 확보하세요.")]),
 "sapporo-snow-festival-clothes":(
  "눈축제에서 덜 춥고 덜 미끄럽게",
  [b("옷은 겹쳐 입기","얇은 발열 내의, 보온 중간층, 바람을 막는 외투를 겹쳐 입고 실내에서는 쉽게 벗을 수 있게 구성하세요."),
   b("신발은 밑창이 우선","빙판에 적합한 접지력, 방수, 발목 지지와 여유 있는 양말 공간을 확인하세요. 평소 운동화라도 빙판에서는 쉽게 미끄러질 수 있습니다."),
   b("사진 촬영 때도 손 보온","장갑·귀마개·목 보호용 소품을 준비하고 스마트폰 배터리 소모에 대비하세요."),
   b("아이·부모님 동행","걸음이 느린 동행자가 있다면 회장마다 실내 휴식 위치를 확인하고, 보행을 줄일 수 있는 일정을 선택하세요.")]),
 "sapporo-snow-festival-hotel-area":(
  "숙소는 회장명보다 역 출입구를 확인",
  [b("오도리역 근처","오도리 눈조각 구역을 여러 번 볼 계획이라면 도심 접근성과 숙소까지의 도보 부담을 비교하기 쉽습니다."),
   b("삿포로역 주변","신치토세공항 이동이나 짐을 동반한 이동이 중요하면 교통 연결을 우선 비교하세요. 호텔까지의 지하 통로 연결 여부는 개별 숙소 안내를 확인하세요."),
   b("스스키노역 주변","저녁 외식과 얼음조각 관람에는 편리할 수 있으나 소음, 늦은 시간 보행과 겨울철 노면 상태를 함께 고려하세요."),
   b("예약할 때","가격표 외에도 무료 취소 기한, 난방·객실 시설, 역 출구에서 실제 보행시간, 계단 유무를 확인하세요.")]),
 "sapporo-snow-festival-photo":(
  "눈조각과 사람을 함께 담는 촬영 팁",
  [b("오도리에서는 구도 먼저","눈조각 전체가 들어오는 위치를 찾은 후 사람을 배치하면 장소가 잘 드러납니다. 사람의 통행을 방해하지 않는 위치를 택하세요."),
   b("야간에는 눈 표면 밝기 관리","밝은 눈과 어두운 주변의 노출 차이가 큽니다. 스마트폰 화면을 눌러 밝기를 조절하고 한 장보다는 여러 장을 찍어 비교하세요."),
   b("스스키노 얼음조각","조명의 반사로 얼음조각 윤곽이 더 잘 보일 수 있습니다. 촬영 전 전시구역 접근 제한과 안전 펜스를 확인하세요."),
   b("현장 안전","삼각대 사용 가능 여부는 현장 안내를 따르고, 빙판 위에서 뒤로 걷거나 도로 쪽으로 물러서지 마세요.")]),
 "sapporo-snow-festival-food":(
  "축제 관람과 지역 먹거리 묶기",
  [b("야외 관람 전에는 간단한 식사","긴 줄과 추위에 대비해 붐비는 시간대를 피하고 따뜻한 실내 식당을 동선에 포함하세요."),
   b("오도리 근처 식당 찾기","관람 시작·종료 지점에서 걸어서 갈 수 있는 식당을 두 곳 이상 후보로 정하세요. 특정 상점의 2027 영업 여부는 별도 확인이 필요합니다."),
   b("스스키노 저녁","얼음조각을 본 뒤 식사를 계획하면 야간 이동을 줄일 수 있습니다. 식당 예약 시 취소 가능 조건을 확인하세요."),
   b("현장 노점·가격","푸드 부스 위치·메뉴·영업시간은 연도별로 달라질 수 있으므로 2027 공식 현장 지도를 확인하세요.")])
}
practical={
 "japan-esim-vs-sim-wifi":("통신수단 3가지, 상황별 선택",[
  b("eSIM: 혼자·가볍게 다닐 때","휴대전화가 eSIM을 지원하고 구매 상품의 설치·활성화 조건을 이해한다면 별도 기기를 들고 다니지 않아도 됩니다. 음성통화·문자 포함 여부는 상품마다 다릅니다."),
  b("실물 유심: 교체형 휴대전화","SIM 슬롯과 잠금 해제 상태를 확인하세요. 한국 유심을 잃어버리지 않도록 보관하고 필요하면 귀국 후 원래 SIM으로 되돌리세요."),
  b("포켓 와이파이: 여러 명 공동 사용","같은 행동 반경에서 움직이는 동행자에게 유용할 수 있지만 배터리 충전, 반납 장소, 분실 비용, 동행자 분리 시 통신 단절을 함께 생각해야 합니다."),
  b("가격 비교에서 빠지기 쉬운 것","사용 일수·데이터 상한·속도 제한·환불·개통 시작 시점·테더링 허용 여부를 같은 조건으로 맞춰 비교하세요.")]),
 "japan-data-usage":("여행 데이터 용량을 정하는 순서",[
  b("지도·메신저 중심","지도 검색, 번역, 문자메시지 위주라면 영상 중심 사용자보다 데이터 사용량이 적을 수 있습니다. 집에서 휴대전화 앱별 데이터 사용량을 먼저 확인하세요."),
  b("사진·SNS를 자주 올릴 때","자동 백업·고화질 사진 업로드·동영상 피드가 데이터 사용을 늘릴 수 있습니다. Wi-Fi 연결 시에만 백업하도록 설정하면 예측이 쉬워집니다."),
  b("영상 시청·핫스팟 사용","동행자에게 연결을 나눠 주거나 장시간 영상 시청을 하면 사용량이 크게 달라집니다. 무제한이라도 속도 제한이 있는지 확인하세요."),
  b("결정 전 확인","지난달 일일 평균 사용량과 여행일수를 곱해 대략적인 범위를 만들고, 남은 용량 확인 방법과 부족할 때의 추가 충전 조건을 비교하세요.")]),
 "japan-esim-setup":("eSIM 구매 후 설치·현지 연결 순서",[
  b("1. 출발 전 지원 여부 확인","설정 메뉴에서 eSIM 추가 항목과 이동통신사 잠금 상태를 확인하세요. 기종뿐 아니라 국가·통신사 모델에 따라 지원이 다를 수 있습니다."),
  b("2. QR·설치 정보 백업","판매자가 안내한 QR 또는 활성화 코드를 오프라인으로 저장하고, 설치에는 인터넷 연결이 필요할 수 있으니 출국 전 판매처 지시를 확인하세요."),
  b("3. 일본 도착 후 데이터 회선 선택","휴대전화 설정에서 여행용 eSIM을 데이터 회선으로 선택하고 필요할 때 데이터 로밍을 허용하세요. 한국 회선의 해외요금이 발생하지 않는지 주의하세요."),
  b("4. 연결 확인·장애 대비","웹페이지와 지도 검색으로 실제 접속을 확인하고, 안 되면 재부팅·네트워크 자동 선택·APN 및 판매처 안내를 차례대로 확인하세요.")]),
 "japan-esim-iphone":("아이폰 eSIM 설정 체크",[
  b("지원 모델·잠금 상태","설정에서 eSIM 추가 여부와 통신사 잠금 상태를 먼저 확인하세요. 판매 국가와 iPhone 모델에 따라 기능이 다를 수 있습니다."),
  b("설치 정보 준비","설정 → 셀룰러 → eSIM 추가 등 메뉴 이름은 iOS 버전에 따라 달라집니다. 판매자가 준 QR 또는 링크를 사용하세요."),
  b("현지에서 회선 선택","데이터 회선을 일본 여행용으로 설정하되 기존 한국 회선의 통화·문자·로밍 설정을 확인해 예상치 못한 요금을 피하세요."),
  b("인터넷이 안 되면","비행기 모드 전환, 재부팅, 데이터 회선·로밍·APN 확인 후 판매처 고객센터로 문의하세요.")]),
 "japan-esim-galaxy":("갤럭시 eSIM 설정 체크",[
  b("모델·통신사 기능 확인","설정 → 연결 → SIM 관리자에서 eSIM 추가 메뉴를 확인하세요. 같은 모델명이어도 출시국과 통신사에 따라 다를 수 있습니다."),
  b("QR로 eSIM 등록","안정적인 Wi-Fi에서 판매자 지침대로 QR 또는 활성화 코드를 입력합니다. 유효기간 시작 시점은 요금제 약관을 확인하세요."),
  b("일본에서 데이터 회선 지정","모바일 데이터 회선을 여행용으로 선택하고, 구매 상품이 요구하는 경우에만 데이터 로밍을 켭니다."),
  b("연결 오류 대처","APN, 통신망 자동 선택, 재부팅 순서로 확인하고 eSIM을 무작정 삭제하지 마세요. 재발급이 유료이거나 불가능할 수 있습니다.")]),
 "japan-esim-troubleshooting":("eSIM이 안 될 때 순서대로",[
  b("1. 실제 개통 시점","eSIM이 설치만 된 상태인지, 현지 접속해야 시작되는 상품인지 판매자 안내부터 다시 읽으세요."),
  b("2. 데이터 회선·로밍","여행용 회선이 데이터 사용 기본값인지 확인하고 구매 상품의 로밍 사용 조건을 확인하세요."),
  b("3. 신호·APN·재부팅","수신 음영지역을 벗어나고 자동 네트워크 선택·APN 설정을 확인한 후 재부팅합니다."),
  b("4. 삭제보다 고객센터","문제 화면을 캡처하고 주문번호와 단말기 모델을 준비해 판매처에 문의하세요. eSIM 삭제는 재사용·재발급 조건 확인 후 결정하세요.")])
}
festival_shared=(
 "<div class='v143-verified-links'><strong>공식 확인:</strong> "
 "<a target='_blank' rel='noopener noreferrer' href='"+OFFICIAL+"'>삿포로 눈축제 공식 홈페이지 ↗</a> "
 "<a target='_blank' rel='noopener noreferrer' href='"+SAPPORO+"'>삿포로 관광정보의 2027 회장·날짜 ↗</a>"
 "<p>2027년 개최 기간은 2월 4~11일로 확인됐지만, 운영시간·체험·셔틀·일부 세부 행사 내용은 갱신될 수 있습니다. 출발 전 재확인하세요.</p></div>"
)
practical_shared=(
 "<div class='v143-verified-links'><strong>공식 안내:</strong> "
 "<a target='_blank' rel='noopener noreferrer' href='"+JNTO+"'>일본정부관광국(JNTO) 인터넷·통신 안내 ↗</a>"
 "<p>기기 지원, 상품 속도 제한, 환불·개통 조건은 판매처·통신사마다 다릅니다. 특정 요금제의 구매 가능성을 보증하지 않습니다.</p></div>"
)

def section(title, parts, kind):
  ret=["<section class='article-card v143-topic' data-v143='verified-topic'><h2>"+escape(title)+"</h2>",
       "<p class='v143-lead'>"+("회장·이동·방한·실제 일정 선택까지 확인할 수 있도록 정리했습니다." if kind=="snow" else "내 휴대전화와 동행 방식에 맞춰 선택하고 현지에서 바로 확인할 순서입니다.")+"</p>",
       "<div class='v143-guide-grid'>"]
  for idx,(head,body) in enumerate(parts):
    ret.append("<div class='v143-guide-step'><span class='v143-no'>"+str(idx+1).zfill(2)+"</span><h3>"+escape(head)+"</h3><p>"+escape(body)+"</p></div>")
  ret+=["</div>",festival_shared if kind=="snow" else practical_shared,"</section>"]
  return "".join(ret)

def compare_visual(slug,title,parts):
  # Accurate first-party information chart, not a pretend photograph.
  # Smaller topics adapt the three panels to the exact content of each guide.
  labels={
   "japan-esim-vs-sim-wifi":[("eSIM","호환 기종 · QR 설치"),("SIM","유심 슬롯 · 보관"),("Wi-Fi","충전 · 반납")],
   "japan-data-usage":[("지도 · 번역","이동 · 경로 검색"),("SNS · 사진","업로드 · 백업"),("영상 · 핫스팟","대용량 · 공유")],
   "japan-esim-setup":[("01","호환 기종 확인"),("02","QR 또는 코드 설치"),("03","데이터 회선 선택")],
   "japan-esim-iphone":[("iPhone","지원·잠금 확인"),("QR","셀룰러에 추가"),("DATA","현지 데이터 지정")],
   "japan-esim-galaxy":[("Galaxy","SIM 관리자 확인"),("QR","eSIM 추가"),("DATA","현지 회선 선택")],
   "japan-esim-troubleshooting":[("SIGNAL","통신 신호 확인"),("SIM","데이터 회선 확인"),("HELP","삭제 전 문의")]
  }[slug]
  return "<figure class='v143-explainer' aria-label='"+escape(title)+" 정보 도식'><div class='v143-visual-head'><span>TRAVEL CONNECTIVITY GUIDE</span><strong>"+escape(title)+"</strong></div><div class='v143-visual-cols'>"+ "".join("<div><b>"+escape(k)+"</b><span>"+escape(v)+"</span></div>" for k,v in labels)+"</div><figcaption>개념과 확인 순서를 정리한 자체 제작 정보 도식입니다. 실제 제품 사진이나 특정 통신사 상품은 아닙니다.</figcaption></figure>"

def safe_replace(path,slug,kind):
 original=path.read_text("utf8")
 assert original.count('<section class="article-card">')==1,(str(path),"unexpected article structure")
 # Protect SEO primitives and headings before any content edit.
 protected={}
 for token,pattern in [('title',r'<title>.*?</title>'),('description',r'<meta name="description"[^>]*>'),
   ('canonical',r'<link rel="canonical"[^>]*>'),('jsonld',r'<script type="application/ld\+json">.*?</script>')]:
  m=re.search(pattern,original,re.S);protected[token]=m.group() if m else None
 marker='<section class="article-card">'
 begin=original.index(marker);end=original.index('</section>',begin)+len('</section>')
 if 'data-v143' in original:raise RuntimeError("already applied "+str(path))
 title,parts= (winter if kind=="snow" else practical)[slug]
 updated=original[:begin]+section(title,parts,kind)+original[end:]
 if kind=="snow":
  old='<img class="article-cover" src="/images/hokkaido.jpg"'
  assert updated.count(old)==1,(slug,"snow cover unexpected")
  updated=updated.replace(old, '<figure class="v143-snow-photo"><img class="article-cover" src="'+PHOTO+'" loading="eager" fetchpriority="high" decoding="async"')
  img_tag=re.search(r'<figure class="v143-snow-photo"><img[^>]+>',updated)
  assert img_tag
  fixed=img_tag.group().replace('alt="'+escape(path.stem)+'"','alt="2014년 삿포로 눈축제 행사장 실제 눈조각 풍경"')
  # src element may have title-specific alt; retain best general factual alt by regexp.
  fixed=re.sub(r'alt="[^"]+"','alt="2014년 삿포로 눈축제 행사장에서 촬영한 실제 눈조각"',fixed)
  updated=updated.replace(img_tag.group(),fixed+"<figcaption>실제 삿포로 눈축제 현장 촬영(2014-02-05). 사진: <a href='"+SOURCE+"' target='_blank' rel='noopener noreferrer'>t-konno / Wikimedia Commons</a> · <a href='"+LIC+"' target='_blank' rel='noopener noreferrer'>CC BY-SA 3.0</a> · WebP 변환·크기 조정. <strong>2027년 축제 현장 사진은 아닙니다.</strong></figcaption></figure>")
 else:
  old='<img class="article-cover" src="/images/esim.jpg"'
  assert updated.count(old)==1,(slug,"practical cover unexpected")
  # Replace topic-mismatched generic photograph with topic-specific accessible diagram.
  pat=r'<img class="article-cover" src="/images/esim.jpg"[^>]*>'
  updated,count=re.subn(pat,compare_visual(slug,title,parts),updated,count=1)
  assert count==1
 # Replace repeated unrelated external NEXT QUESTION + OPEN THE MAP section with
 # relevant direct link to the page's category and current guide chain.
 start=updated.index('<div class="curiosity">')
 stop=updated.index('</div>',start)+6
 nexts= (
  [("축제 일정·3개 회장 비교","/season/sapporo-snow-festival-2027/"),
   ("눈축제 숙소·교통 준비","/season/sapporo-snow-festival-hotel-area/"),
   ("눈길에 맞는 신발·방한","/season/sapporo-winter-shoes/")]
  if kind=="snow" else
  [("eSIM·유심·포켓 와이파이 비교","/practical/japan-esim-vs-sim-wifi/"),
   ("설치·활성화 순서","/practical/japan-esim-setup/"),
   ("연결 오류 체크리스트","/practical/japan-esim-troubleshooting/")]
 )
 links="<nav class='v143-next' aria-label='주제와 연결되는 다음 안내'><h2>다음 단계 바로가기</h2>"+ "".join("<a href='"+url+"'>"+escape(t)+" <span aria-hidden='true'>→</span></a>" for t,url in nexts if url!=("/season/"+slug+"/" if kind=="snow" else "/practical/"+slug+"/"))+"</nav>"
 updated=updated[:start]+links+updated[stop:]
 if updated.count('<link rel="stylesheet" href="/style.css">')!=1:raise RuntimeError("base stylesheet missing "+str(path))
 updated=updated.replace('<link rel="stylesheet" href="/style.css">','<link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/nf-v143-topic-guides.css?v=20261023">',1)
 for token,pattern in [('title',r'<title>.*?</title>'),('description',r'<meta name="description"[^>]*>'),
  ('canonical',r'<link rel="canonical"[^>]*>'),('jsonld',r'<script type="application/ld\+json">.*?</script>')]:
  m=re.search(pattern,updated,re.S)
  assert protected[token]==(m.group() if m else None),("SEO DRIFT",slug,token)
 assert updated.count('data-v143=')==1
 path.write_text(updated,"utf8")
 return {"page":"/"+("season" if kind=="snow" else "practical")+"/"+slug+"/","title":title,"cards":len(parts),"image_status":"verified 2014 documentary photograph" if kind=="snow" else "custom topic-specific information illustration",
         "seo_preserved":True}

def get_image():
 p=SITE/PHOTO.lstrip("/")
 if p.exists():raise RuntimeError("photograph already exists; guard against overwrite")
 url="https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(FILENAME,safe="")+"?width=1450"
 data=None
 for i in range(3):
  try:
   with urlopen(Request(url,headers={"User-Agent":"NipponFerryEditorialVerification/1.0 (https://www.nipponferry.com/)"}),timeout=90) as res:
    if not res.headers.get("Content-Type","").startswith("image/"):
     raise RuntimeError("non-image Commons response")
    data=res.read(11_000_001)
   if not 40_000<len(data)<11_000_000:raise RuntimeError("size unexpected")
   break
  except Exception:
   if i==2:raise
   time.sleep(5)
 im=ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
 if im.width<1100 or im.height<700:raise RuntimeError("unexpected dimensions")
 im.thumbnail((1440,960),Image.Resampling.LANCZOS)
 blob=io.BytesIO();im.save(blob,format="WEBP",quality=86,method=6)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob.getvalue())
 return {"local_path":PHOTO,"source":SOURCE,"captured":"2014-02-05",
         "author":AUTHOR,"license":"CC BY-SA 3.0","license_url":LIC,
         "derivative":"resized and WebP converted; source event photo is NOT 2027",
         "dimensions":[im.width,im.height],"sha256":sha256(blob.getvalue()).hexdigest()}

def audit():
 pages=list(SITE.rglob("*.html"))
 phrases=[
 "계절 이벤트는 날짜와 날씨 변수의 영향을 크게 받습니다.",
 "서비스·교통·시설은 노선, 기기, 날짜와 지역에 따라 조건이 달라질 수 있습니다.",
 "행사만 보고 끝내기보다 지역 음식, 시장, 기념품, 카페와 함께",
 "NEXT QUESTION",
 "현장에서는 방한과 미끄럼 대비",
 "여행 전에 확인하세요"
 ]
 generic={q:[] for q in phrases};cover=Counter();cover_samples=defaultdict(list);no_img=[];short=[];details=[]
 for p in pages:
  h=p.read_text("utf8",errors="replace")
  rel="/"+p.relative_to(SITE).as_posix().removesuffix("index.html")
  if not rel.endswith("/"):rel+="/"
  for phrase in phrases:
   if phrase in h:generic[phrase].append(rel)
  m=re.search(r'<img class="article-cover" src="([^"]+)"',h)
  if m:
   cover[m.group(1)]+=1
   if len(cover_samples[m.group(1)])<12:cover_samples[m.group(1)].append(rel)
  elif 'article-card' in h and 'v143-explainer' not in h:
   if len(no_img)<100:no_img.append(rel)
  sec=re.search(r'<section class="article-card"[^>]*>(.*?)</section>',h,re.S)
  if sec:
   content=re.sub(r'<[^>]+>','',sec.group(1))
   if len(content)<260:
    if len(short)<250:short.append(rel)
  details.append(rel)
 return {"scan_count":len(pages),
    "generic_repetitions":{k:{"count":len(v),"example_paths":v[:20]} for k,v in generic.items()},
    "shared_covers":[{"path":k,"count":v,"sample_paths":cover_samples[k]} for k,v in cover.most_common(35)],
    "short_article_card_sample":short,
    "short_article_card_sample_size":len(short),
    "article_without_standard_cover_sample":no_img,
    "limits":"HTML heuristic audit: detects repeated text/images, not proof that a photo is from wrong place. Only pages in modified_pages were edited."}

def main():
 specs=[("season",slug) for slug in winter]+[("practical",slug) for slug in practical]
 for kind,slug in specs:
  p=SITE/kind/slug/"index.html"
  if not p.exists():raise RuntimeError("target page missing "+str(p))
  txt=p.read_text("utf8")
  assert '<section class="article-card">' in txt and ('/images/hokkaido.jpg' if kind=="season" else '/images/esim.jpg') in txt,slug
 # Download before altering HTML. Do not publish unverified cover substitution.
 photo=get_image()
 updates=[]
 for kind,slug in specs:updates.append(safe_replace(SITE/kind/slug/"index.html",slug,"snow" if kind=="season" else "practical"))
 report={"version":"V143","verified_at":"2026-10-23","modified_pages":updates,"modified_count":len(updates),
         "new_articles":0,"new_urls":0,"image_original":photo,
         "official_date_source":OFFICIAL,"official_tourism_source":SAPPORO,
         "separate_active_snow_festival_date":"2027-02-04 to 2027-02-11",
         "qa_requires":{"full_site_inventory":True,"browser_mobile_desktop":True,"production_crawl_after_deploy":True},
         "global_audit":audit()}
 (OUT/"sitewide-content-and-image-audit.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n","utf8")
 print(json.dumps({"updated":len(updates),"winter":len(winter),"practical":len(practical),
                   "scanned":report["global_audit"]["scan_count"],
                   "top_shared":report["global_audit"]["shared_covers"][:6]},ensure_ascii=False))
if __name__=="__main__":main()
