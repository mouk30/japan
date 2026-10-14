from pathlib import Path
import html
from datetime import date
ROOT=Path("site/things-to-do")
DATA={
"hiroshima":{
"intro":"접안 부두가 우지나 외무부두(크루즈터미널)인지 이쓰카이치 부두인지 먼저 확인하세요. 두 곳은 승객 동선과 시내 진입 방식이 다릅니다.",
"transfer":"우지나 외무부두 제5선석은 히로시마항 크루즈터미널에 인접합니다. 히로시마 항만 운영기관은 이 부두의 택시가 선석 내부에 들어가지 않고 크루즈터미널 택시풀을 이용하도록 안내합니다. 이쓰카이치 부두는 항만 통제구역에 일반 차량 접근 제한이 있으므로 항차별 공식 셔틀·차량 승차장을 확인해야 합니다.",
"plan":"우지나 하선 확인 → 터미널의 공식 탑승지점 → 히로시마항 전차·공식 셔틀 연결 확인 → 원폭돔·평화기념공원 중 가까운 권역에 집중 → 역순 복귀. 이쓰카이치 하선 시 이 동선을 그대로 적용하지 말고 항만 지정 환승 위치부터 다시 결정하세요.",
"warning":"이쓰카이치 부두를 우지나로 혼동하면 복귀에 실패할 수 있습니다. 선사 최종 승객 귀선 마감(출항 시간과 다름)과 게이트, 셔틀 막차는 각 항차별로 확인해야 합니다.",
"sources":[("히로시마항 우지나 공식 안내","https://hiroshima-minato.jp/enaccessujina/"),("이쓰카이치 공식 접근 안내","https://hiroshima-minato.jp/enaccessitsukaichi/"),("우지나→평화공원 공식 관광 교통","https://hiroshima-minato.jp/enkankoujina/")]},
"iwakuni":{
"intro":"야마구치현 공식 항만 자료는 이와쿠니항의 신코 미나미 선석과 무로노키 선석 등을 소개합니다. 배정은 항차별 확정이므로 항구 이름만으로 하선 게이트를 정하면 안 됩니다.",
"transfer":"야마구치현 공식 이와쿠니항 안내는 긴타이쿄를 자동차 약 20분 거리의 관광지로 소개합니다. 이는 일반적인 접근 기준이며 실제 승객 게이트·차량 대기·교통체증은 포함하지 않습니다.",
"plan":"실제 접안 선석·승객 출입구 확인 → 공식 지정 차량/택시 탑승지점 확인 → 긴타이쿄 도착 → 다리 주변 관광 → 예약된 왕복 이동편으로 같은 승객 게이트 복귀. 시간이 충분하지 않으면 이와쿠니성까지 무리하게 추가하지 않습니다.",
"warning":"신코 미나미/무로노키 선석은 동일한 출발지가 아닙니다. 임의의 무료 셔틀 운행이나 승객 최종 귀선 시간을 확정 정보로 표시하지 않습니다.",
"sources":[("야마구치현 이와쿠니항 공식 크루즈 안내","https://www.pref.yamaguchi.lg.jp/soshiki/91/21621.html"),("항만 및 관광 교통 자료","https://www.pref.yamaguchi.lg.jp/uploaded/attachment/57474.pdf")]},
"kure":{
"intro":"구레는 항만 주변의 야마토뮤지엄과 해상자위대 구레사료관 관광권을 중심으로 계획할 수 있지만, 크루즈 실제 접안 선석은 선사 공지를 확인해야 합니다.",
"transfer":"구레역·구레 중앙부두 터미널·야마토뮤지엄은 서로 구분되는 장소입니다. 중앙부두 인근 관광시설로 이동하기 전 선박의 실제 승객 하선 게이트와 접근 가능한 도보 동선을 현장에서 확인하세요.",
"plan":"지정 크루즈 승객 출입구 → 접근 가능 여부를 확인한 후 중앙부두/박물관 권역 이동 → 박물관 운영·예약 및 입장 가능 여부 확인 → 귀선 교통 수단을 먼저 확보하고 항구로 복귀.",
"warning":"과거의 사진과 후기만으로 박물관 개관일, 크루즈 선석, 무료 셔틀을 단정하지 않습니다. 특히 박물관 공사·개관 일정은 방문일 공식 공지를 최우선으로 확인해야 합니다.",
"sources":[("구레 관광 안내(시설·교통 추가 확인)","https://www.city.kure.lg.jp/"),("야마토뮤지엄 공식 안내","https://yamato-museum.com/")]},
"mojiko":{
"intro":"기타큐슈시는 크루즈 접안 후보를 모지 서해안 1·2호, 6호, 고쿠라 아사노 1호, 히비키 컨테이너터미널 등으로 구분합니다. '모지항'이라는 표기만으로 모지코 레트로 도보 관광을 가정하면 안 됩니다.",
"transfer":"모지 서해안 1·2호 선석은 모지코 레트로 관광권과 가까운 곳이지만 6호 및 고쿠라·히비키 터미널은 도보 동선이 다릅니다. 항차별 승객 게이트와 보안구역 출구, 차량 대기장 및 셔틀 유무를 반드시 확인하세요.",
"plan":"모지 서해안 1·2호 접안과 출입 허용 동선이 확인된 경우 → 모지코 레트로·모지코역을 중심으로 한 곳 또는 두 곳 관광 → 항만 지정 출입구로 복귀. 다른 선석이면 관광 출발 전에 공식 교통편을 먼저 확정합니다.",
"warning":"기타큐슈시 2026년 9월 갱신 자료에서도 접안 선석은 여러 곳입니다. 예전 항차에 제공된 셔틀이나 도보 동선을 오늘의 선박에 적용하면 안 됩니다.",
"sources":[("기타큐슈시 크루즈 입항·선석 공식 안내","https://www.city.kitakyushu.lg.jp/contents/30400002.html")]},
"aburatsu":{
"intro":"아부라쓰항과 니치난시 오비성 관광구역은 동일한 장소가 아닙니다. 크루즈의 정확한 선석·승객 출입구 및 차량 탑승 가능 지역을 먼저 확인해야 합니다.",
"transfer":"오비성 오테몬은 니치난시의 옛 성곽 구역에 있는 관광 명소로, 항만에서 바로 내려 도보로 관광하는 항만 부속 시설이 아닙니다. 왕복 버스·택시·선사 공식 투어를 여행일 운영 상황에 맞게 확인하세요.",
"plan":"실제 하선 출구 확인 → 귀선용 차량이나 왕복 투어 먼저 확보 → 오비성 오테몬·옛 성곽 거리 산책 → 미리 확보한 차량으로 부두 복귀. 이동편이 불확실하면 오비성 추가 관광을 취소하고 항구 인근으로 제한하세요.",
"warning":"공식 항차별 셔틀 운행·버스 배차·승객 최종 귀선 시각은 현재 미확인입니다. 관광 예상 이동시간을 확정값으로 제공하지 않으며, 선사 안내를 우선하세요.",
"sources":[("니치난시 공식 관광·교통 확인","https://www.city.nichinan.lg.jp/"),("미야자키현 항만·크루즈 운영 확인","https://www.pref.miyazaki.lg.jp/")]}
}
for slug,v in DATA.items():
 file=ROOT/f"{slug}-cruise-port-day-trip"/"index.html"
 s=file.read_text()
 if 'id="nf-v26b5-grounded-route"' in s: continue
 links=" ".join(f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{html.escape(title)}</a>' for title,url in v["sources"])
 section=f'''<section id="nf-v26b5-grounded-route" aria-label="공식 자료 기반 승객 동선과 귀선 점검"><h2>실제 하선 게이트부터 관광지까지 · 공식 정보 점검</h2><p><strong>출발점:</strong> {html.escape(v["intro"])}</p><h3>게이트·현지 교통</h3><p>{html.escape(v["transfer"])}</p><h3>당일 관광 동선 — 확정 시간표가 아닌 계획 예시</h3><p>{html.escape(v["plan"])}</p><div class="warn"><strong>승객 귀선 안전 확인</strong><p>{html.escape(v["warning"])}</p><p>선박 출항시간과 승객 최종 귀선 마감은 다릅니다. 선사 앱·선내 안내에서 선박명, 항차, 부두, 귀선 게이트, 지정 귀선 시각을 반드시 확인하세요.</p></div><p class="small">공식·기관 자료 확인 링크: {links}</p><p class="small">정보 검토일: 2026-10-14. 링크가 제공되어도 해당 항차 셔틀 운행·시설 예약 가능·귀선 시각이 확정된 것은 아닙니다.</p></section>'''
 if '<section' not in s:raise RuntimeError(slug)
 insert=s.index('<section',s.index('<main'))
 s=s[:insert]+section+s[insert:]
 file.write_text(s)
 print("V26_B5_ROUTE",slug)
