# V39 — 즐길거리 안내 그래픽 20편 실사 교체 완료

- 작업 날짜: 2026-10-15.
- 범위: 기존 `/things-to-do/`의 주제 안내 그래픽 60개 중 20개. 기존 게시글 **20편 수정**, 신규 게시글 **0편**.
- 반영: CC 허용 사진 → 내부 WebP로 저장 → 페이지 본문 대표 이미지, 152개 디렉터리의 해당 카드, OG/Twitter 이미지 주소 통일 → 사진 출처 및 라이선스 표시.
- 원래 게시글 URL·canonical·사이트맵은 유지.
- 실제 서버 응답 검증: **41/41 성공** = 이미지 20건(HTTP 200 및 WebP 헤더 검사), 본문 20건(HTTP 200 및 OG/Twitter 경로 검사), `/things-to-do/` 목록 1건(HTTP 200 및 20개 썸네일 참조). [실제 운영 사이트 검수 JSON](v39-live-qa.json).
- [GitHub 실사 20편 교체 커밋](https://github.com/mouk30/japan/commit/0e0326ca0447da2ce5165936989cfaa967fc8978).
- 검수 범위와 한계: 실제 페이지 HTTP 검사까지 완료. 모바일·PC 브라우저의 눈으로 보는 크롭·레이아웃 검수, 전체 사이트 누락 이미지 전수 검사는 이 결과에 포함되지 않음.

## 20편 사진·저작권 명세

|번호|게시글|사진의 실제 대상·제약|원본 출처|라이선스|
|---:|---|---|---|---|
|1|[japanese-machiya-townhouses](https://www.nipponferry.com/things-to-do/japanese-machiya-townhouses/)|교토 기온의 좁은 골목에 늘어선 전통 마치야 가옥 실제 사진. 교토 기온의 마치야 외관 사례이며 주택 내부를 촬영한 사진은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Streets_of_Gion%2C_Kyoto_-_Gion7712.jpg)|CC0|
|2|[japan-ainu-embroidery](https://www.nipponferry.com/things-to-do/japan-ainu-embroidery/)|홋카이도 아이누 민족의 19세기 자수와 덧댐 장식이 있는 의복 유물. 로스앤젤레스 카운티 미술관 소장 역사 의복이며 현재 공방에서 제작하는 장면은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Robe%2C_%27Retara_Kapara_Amip%27_LACMA_M.71.87.1.jpg)|Public domain|
|3|[japan-amami-oshima-tsumugi](https://www.nipponferry.com/things-to-do/japan-amami-oshima-tsumugi/)|아마미 오시마쓰무기 전통 염색과 연관된 가나이 공방의 진흙 염색 작업 장소. 염색 공방의 진흙 염색 공간으로 완성된 직물 제품 사진은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Mud_Dyeing_Kanai_Workshop.jpg)|CC0|
|4|[noh-japanese-mask-theater](https://www.nipponferry.com/things-to-do/noh-japanese-mask-theater/)|베를린 박물관에 전시된 일본 전통 노(能) 공연 가면 실물. 박물관 소장 가면 유물로 실제 무대 공연 중인 배우의 사진은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Noh_mask_in_Berlin_museum_2.jpg)|CC BY-SA 3.0|
|5|[bunraku-japanese-puppet-theater](https://www.nipponferry.com/things-to-do/bunraku-japanese-puppet-theater/)|오사카 국립분라쿠극장의 실제 분라쿠 인형 공연 또는 전시 사진. 오사카 분라쿠극장에서 촬영된 사진이며 각 인형의 제작 시기는 따로 확인해야 합니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Bunraku_theater_4.jpg)|CC BY 2.0|
|6|[shamisen-japanese-three-string-instrument](https://www.nipponferry.com/things-to-do/shamisen-japanese-three-string-instrument/)|메트로폴리탄 미술관 소장 일본 전통 삼현악기 샤미센 실물. 실제 샤미센 악기 유물의 사진으로 연주 현장을 촬영한 것은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Shamisen_MET_midp69.271.2a.jpg)|CC0|
|7|[ukiyoe-japanese-woodblock-art](https://www.nipponferry.com/things-to-do/ukiyoe-japanese-woodblock-art/)|메트로폴리탄 미술관 소장 일본 목판 삽화 제작용 실제 판목. 서적 삽화용 목판 유물로 모든 우키요에 다색판 제작 공정을 그대로 보여주는 사진은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:MET_27_117_1_O2_sf.jpg)|CC0|
|8|[temari-japanese-thread-balls](https://www.nipponferry.com/things-to-do/temari-japanese-thread-balls/)|실로 촘촘한 기하학 무늬를 수놓은 일본식 테마리 공예품 실제 사진. 완성된 일본식 테마리 공예품 사례이며 일본 현지 공방 사진은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Japanese_Temari_ball_flanked_by_a_maneki_neko_%2801%29_%2850532211976%29.jpg)|CC BY 2.0|
|9|[sashiko-japanese-repair-stitching](https://www.nipponferry.com/things-to-do/sashiko-japanese-repair-stitching/)|일본 보로 천에 기능과 장식을 더한 사시코 바느질 실제 직물 유물. 일본 직물의 사시코 바느질을 담은 실물 사진이며 실제 바느질 작업 장면은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Boro_textile_from_Japan%2C_with_sashiko.jpg)|CC BY 4.0|
|10|[udon-japanese-regional-noodles](https://www.nipponferry.com/things-to-do/udon-japanese-regional-noodles/)|2015년 히로시마 식당에서 촬영한 일본 우동 한 그릇. 히로시마 지역 식당 음식 사진으로 일본 전국의 우동 품종을 모두 보여주지는 않습니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Udon_noodles_in_a_bowl_in_a_restaurant_in_Hiroshima%2C_Japan_-_September_2015.jpg)|CC BY-SA 4.0|
|11|[yakitori-japanese-skewer-culture](https://www.nipponferry.com/things-to-do/yakitori-japanese-skewer-culture/)|닭고기와 파를 구운 일본식 네기마 야키토리 꼬치 요리 실제 사진. 미국 농무부의 요리 예시 사진으로 일본 현지 식당에서 촬영한 사진은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:MyPlate_gov_Cultural_Food_%2820241025-USDA-FNS-UNK-0031%29.jpg)|Public domain|
|12|[onigiri-japanese-rice-ball](https://www.nipponferry.com/things-to-do/onigiri-japanese-rice-ball/)|김과 밥으로 만든 일본 전통 오니기리 삼각 주먹밥 실제 음식 사진. 일본에서 볼 수 있는 주먹밥 음식 예시이며 특정 편의점 제품 사진은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Onigiri_001.jpg)|CC0|
|13|[konbini-japanese-convenience-store-life](https://www.nipponferry.com/things-to-do/konbini-japanese-convenience-store-life/)|일본 편의점 내부의 실제 음료 진열 코너 촬영 사진. 2009년 촬영 자료이며 현재 판매 상품 및 진열 구성을 뜻하지 않습니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Konbini_drink_corner_2009_%283819547946%29.jpg)|CC BY 2.0|
|14|[japanese-hightech-public-toilets](https://www.nipponferry.com/things-to-do/japanese-hightech-public-toilets/)|일본 비데식 화장실의 실제 세정·중지 조작 버튼 사진. 비데 조작 버튼 사례로 모든 일본 공중화장실에 동일한 버튼이 있다는 뜻은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Japanese_toilet_buttons.jpg)|CC BY-SA 2.0|
|15|[yatai-japanese-food-stalls](https://www.nipponferry.com/things-to-do/yatai-japanese-food-stalls/)|홋카이도 오비히로에 모인 일본식 야타이 노점 음식 거리 실제 사진. 홋카이도 오비히로의 겨울 야타이로 후쿠오카 야타이 현장 사진은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:ObihiroYatai.jpg)|CC BY-SA 3.0|
|16|[omikuji-japanese-fortune](https://www.nipponferry.com/things-to-do/omikuji-japanese-fortune/)|가나가와현 가마쿠라 신사에 묶어둔 일본 오미쿠지 운세 종이 실제 사진. 가마쿠라 신사 운세의 한 가지 사례입니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Kamakura_omikuji.jpg)|CC BY 2.0|
|17|[japan-small-streets](https://www.nipponferry.com/things-to-do/japan-small-streets/)|교토 폰토초의 좁은 골목길을 담은 실제 거리 사진. 교토 폰토초 골목의 과거 촬영 자료이며 현재 가게 구성은 달라질 수 있습니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Pontocho_by_Aleksander_Dragnes.jpg)|CC BY 2.0|
|18|[setsubun-japanese-beans](https://www.nipponferry.com/things-to-do/setsubun-japanese-beans/)|하코네 신사에서 열린 일본 세쓰분 마메마키 콩 뿌리기 행사 실제 사진. 하코네 신사의 실제 세쓰분 의례 사례로 매년 행사 운영 내용은 달라질 수 있습니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Hakone_Shrine_Setsubun_mamemaki_02.jpg)|CC BY-SA 4.0|
|19|[ume-japanese-plum-blossoms](https://www.nipponferry.com/things-to-do/ume-japanese-plum-blossoms/)|이바라키현 미토 가이라쿠엔 공원의 일본 매화꽃 실제 사진. 가이라쿠엔 매화꽃 사례이며 현재 개화 상황을 나타내지 않습니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Plum_Kairakuen_%28201573725%29.jpeg)|CC BY-SA 3.0|
|20|[tsukimi-japanese-moon-viewing](https://www.nipponferry.com/things-to-do/tsukimi-japanese-moon-viewing/)|일본 쓰키미 달맞이 상차림의 경단과 억새 장식 실제 사진. 일본 달맞이 행사 상차림 예시이며 특정 축제 개최장 사진은 아닙니다.|[Commons 원본](https://commons.wikimedia.org/wiki/File:Tsukimi%2Cmoon-viewing-party%2Cjapan.JPG)|CC BY 3.0|

## 남은 152개 카드의 분류

- **60편:** V37~V39에서 실물 사진의 촬영 대상을 확인하고 라이선스·출처를 연결한 카드.
- **40편:** 기존 이미지 파일명과 콘텐츠 주제가 직접 연동되었으나 실사/출처까지 추가 검수할 대상.
- **12편:** 사진이 주제와 관련되지만 전용 사진이 아닌 참고 이미지.
- **40편:** 원본이 없는 경우의 안내 그래픽. 다음 V40/V41에서 각 20편씩 순차 교체할 대상.

사진을 교체할 때는 실제 공연·박물관 유물·해외 전시·예전 촬영본·현재 시설 사진을 혼동하지 않고, 출처가 명시된 사항만 사실로 설명합니다.
