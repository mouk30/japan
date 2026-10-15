# V43 — 출처 미확인 이미지 21편 및 포토스팟 지도 진입 오류 해결

작업 기준일: 2026-10-15. 사이트: [NIPPONFERRY](https://www.nipponferry.com/)

## 조치 완료

- 이전 V42 검수에서 확인된 원본 출처가 없는 주제 편집 이미지 **20편 모두 실제 촬영 사진으로 변경**. 사진 원본, 저작자, 저작권 라이선스, 촬영 대상과 사진의 의미상 한계를 기사 대표 이미지 아래에 공개.
- **기모노·유카타 비교 편집 이미지 1편은 유지**. 실제 현장 촬영 사진이 아니라 비교용 편집 이미지임을 안내하고 원본 실사로 잘못 주장하지 않는다.
- 개별 글·목록 카드 이미지 및 OG/Twitter 이미지 주소 동기화. 기존 글 URL과 canonical·내부링크 유지.
- 실제 픽셀을 살펴보며 **료칸, 고타쓰, 화과자, 이자카야, 라멘 5편**의 첫 번째 선택을 더 관련성이 높은 원본 사진으로 재교체. [수정 대상·원본](v43-photo-visual-corrections.json).
- 기존 즐길거리 목록의 320–540px 좁은 화면 카드 폭/글씨 크기 보강. 모바일 한 칸 카드, PC 2열 구조와 이미지 비율을 유지.
- 홈페이지 **포토스팟 메뉴와 테마 카드 2곳**의 잘못된 `/explore/` 링크를 새로운 **`/photo-spots/`**로 수정. `/explore/` 자체는 일본 탐험지도 기능이므로 그대로 두고, 사진 명소 안내는 별도 페이지에서 지도 없이 시작할 수 있도록 분리.
- [포토스팟](https://www.nipponferry.com/photo-spots/)에서 후쿠오카, 오사카, 대마도, 시모노세키 4개 지역의 사진 명소 간단 소개·촬영 시간대 참고·여행시 유의점, 기존 상세 가이드 링크, 선택형 지도 링크 제공.
- `site/sitemap.xml`에 신규 `/photo-spots/` 경로 등록. 총 **1,045개 URL** 유지.

## 완료 검증

- [실제 공개 사이트 HTTP 검증](v43-live-qa.json): **49/49 통과**. 사진 WebP 20건 **운영 사이트와 GitHub 파일 SHA-256 정확히 동일**, 기사 20건(대표 이미지, OG, Twitter, 출처), 즐길거리 목록 1건, 홈 1건, 포토스팟 1건, 기존 지도 1건, 사이트맵 1건, 지역별 사진 가이드 4건.
- [실제 크로미움 브라우저 PC·모바일](https://github.com/mouk30/japan/blob/main/audit-reports/v43/browser-qa.json): **6/6 통과**. 카드 화면 너비 320·390·768·1440px, 포토스팟 홈페이지 클릭 390·1440px, 이미지 로딩 및 문서 가로 스크롤 넘침 검사 완료.
- 변경된 20장 실제 픽셀 스냅샷도 원본 다운로드 후 검토, 5장 교체 선택에 반영.
- 배포: Vercel 신규 사진 적용과 포토스팟 페이지 배포 성공 확인.

## 즐길거리 카드 총 152편의 이미지 상태

| 유형 | 카드 수 | 주의사항 |
|---|---:|---|
| 신규 원본 사진과 저작권 검증 후 WebP 교체 | 131 | V37~V43 작업 사진은 촬영자·라이선스 게시글에 표시 |
| 이전부터 본문에 저작권·출처 표기가 확인된 사진 | 20 | 이 대목은 V42에 기존 본문 표기를 확인한 것이며 독립 현장 진위 확인까지 의미하지 않음 |
| 기모노·유카타 설명용 편집 비교 이미지 | 1 | 실제 촬영본이 아님을 명시 |
| 출처 없는 주제 편집 이미지 | 0 | 신규 실사로 보강 완료 |

## 신규 실사 20편 실제 출처·라이선스

| 번호 | 기존 게시글 | 검증한 사진 속 대상과 범위 | Wikimedia 원본 | 라이선스 |
|---:|---|---|---|---|
| 1 | [omamori-japanese-amulet-culture](https://www.nipponferry.com/things-to-do/omamori-japanese-amulet-culture/) | 후지산 혼구 센겐타이샤 신사의 오마모리 부적 실물. 실제 신사 오마모리 사진으로 모든 신사에서 같은 부적을 판매하는 것은 아닙니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Omamori_of_Fujisan_Hongu_Sengen_Taisha.jpg) | CC BY 3.0 |
| 2 | [ema-japanese-wish-wooden-plaques](https://www.nipponferry.com/things-to-do/ema-japanese-wish-wooden-plaques/) | 후쿠이현 신사의 소원 에마 나무패 실제 사진. 일본 신사에서 소원을 적는 에마 사례이며 특정 관광지의 운영시간과 관계없습니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Shinto_shrine_votive_tablets_in_rural_Fukui_prefecture.jpg) | CC BY-SA 4.0 |
| 3 | [goshuin-temple-shrine-stamps](https://www.nipponferry.com/things-to-do/goshuin-temple-shrine-stamps/) | 2024년 일본 순례자가 받은 실제 고슈인 수첩의 한 페이지. 실제 고슈인 기록 사진이며 현재 특정 신사의 접수시간과 디자인은 다를 수 있습니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Emma_H._Leonhart%27s_Goshuinch%C5%8D_03.jpg) | CC BY 4.0 |
| 4 | [ryokan-japanese-inn-hospitality](https://www.nipponferry.com/things-to-do/ryokan-japanese-inn-hospitality/) | 일본 도시하루 료칸의 실제 밝은 다다미 객실과 후톤 침구. 실제 료칸 객실 사진이며 현재 객실 배치나 예약 가능 여부를 나타내지 않습니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:My_traditional_accomodation_at_Toshiharu_Ryokan_%2848885681992%29.jpg) | CC BY 2.0 |
| 5 | [tatami-floor-japanese-living](https://www.nipponferry.com/things-to-do/tatami-floor-japanese-living/) | 다다미와 쇼지가 있는 실제 일본식 방. 다다미방 실사 사례이며 특정 숙소의 현재 객실 사진은 아닙니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Japanese_room_with_tatami_mats.jpg) | Public domain |
| 6 | [futon-japanese-bedding-culture](https://www.nipponferry.com/things-to-do/futon-japanese-bedding-culture/) | 다카야마 아스나로 료칸의 실제 일본식 후톤 침구. 현지 료칸 침구의 예시이며 모든 료칸에서 같은 침구를 사용하지는 않습니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Futons_in_a_Ryokan.jpg) | CC BY 2.0 |
| 7 | [shoji-fusuma-japanese-doors](https://www.nipponferry.com/things-to-do/shoji-fusuma-japanese-doors/) | 후쿠오카 하카타 옛 미우라 가옥의 쇼지 종이문과 엔가와. 일본식 쇼지의 실제 사진이며 후스마와 쇼지를 한 화면에서 비교한 것은 아닙니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Sh%C5%8Dji_and_Engawa_of_the_former_Miura_residence_6-10_Reisenmachi_Hakata-ku_Fukuoka_20240119.jpg) | CC BY 4.0 |
| 8 | [kotatsu-japanese-winter-table](https://www.nipponferry.com/things-to-do/kotatsu-japanese-winter-table/) | 일본식 방에 이불이 둘러진 고타쓰 난방 테이블 실사. 전기 난방 테이블을 이불로 감싼 고타쓰 예시이며 현재 특정 숙소의 모습은 아닙니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:%E3%81%93%E3%81%9F%E3%81%A4_%283251928073%29.jpg) | CC BY-SA 2.0 |
| 9 | [furoshiki-japanese-wrapping-cloth](https://www.nipponferry.com/things-to-do/furoshiki-japanese-wrapping-cloth/) | 지바현 가토리시의 전통 후로시키 포장천 실제 사진. 일본 후로시키 보자기의 실물 예시로 특정 포장법 전체를 설명한 사진은 아닙니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Traditional_Japanese_wrapping_cloth%2Churoshiki%2Ckatori-city%2Cjapan.JPG) | CC BY 3.0 |
| 10 | [bento-japanese-lunchbox-everyday](https://www.nipponferry.com/things-to-do/bento-japanese-lunchbox-everyday/) | 일본식 도시락에 밥과 반찬을 담은 벤토 실제 사진. 일본 도시락 구성 예시이며 모든 가정·지역의 벤토가 같다는 뜻은 아닙니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:TOKYO_Cuisine%2CJapanese_style_lunch_box_%282030502153%29.jpg) | CC BY-SA 2.0 |
| 11 | [wagashi-japanese-seasonal-sweets](https://www.nipponferry.com/things-to-do/wagashi-japanese-seasonal-sweets/) | 해바라기 등 여름 계절을 표현한 여러 종류의 일본 화과자 실제 사진. 일본 여름 화과자의 실제 디자인 사례이며 현재 판매되는 제품은 아닙니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Summer_wagashi_10.jpg) | CC0 |
| 12 | [matcha-sencha-japanese-green-tea](https://www.nipponferry.com/things-to-do/matcha-sencha-japanese-green-tea/) | 말차 잎·분말·차를 배치한 실제 차 재료 사진. 말차에 관한 사진으로 센차의 추출 방식까지 동시에 보여주는 사진은 아닙니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Matcha_layout_with_leaf%2C_tea%2C_and_powder.jpg) | CC0 |
| 13 | [toshikoshi-soba-newyear-tradition](https://www.nipponferry.com/things-to-do/toshikoshi-soba-newyear-tradition/) | 일본 간사이식 연말 도시코시 소바 음식 실제 사진. 새해 전야에 먹는 도시코시 소바 사례이며 모든 지역에서 같은 재료를 사용하지는 않습니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:New_Year%27s_Kansai_style_soba_%2838825836845%29.jpg) | CC BY 2.0 |
| 14 | [ramen-japanese-noodle-evolution](https://www.nipponferry.com/things-to-do/ramen-japanese-noodle-evolution/) | 도쿄에서 촬영된 돈코츠 국물 라멘 한 그릇 실제 사진. 일본식 돈코츠 라멘 예시이며 모든 지역의 라멘 조리법을 보여주지는 않습니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Tonkotsu_ramen_in_Tokyo.jpg) | CC0 |
| 15 | [izakaya-japanese-afterwork-culture](https://www.nipponferry.com/things-to-do/izakaya-japanese-afterwork-culture/) | 교토 기온 갓파 이자카야 식당 내부에서 조리 중인 실제 장면. 일본 이자카야의 실제 조리·식당 장면으로 현재 영업 상태 및 메뉴는 별도 확인해야 합니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Gion_Kappa_Restaurant_in_Kyoto.jpg) | CC0 |
| 16 | [osechi-ryori-japanese-new-year-food](https://www.nipponferry.com/things-to-do/osechi-ryori-japanese-new-year-food/) | 일본 새해 음식 오세치를 찬합에 담은 실제 사진. 일본 오세치 요리 구성의 예시이며 특정 가정의 새해 풍습을 일반화하지 않습니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Osechi.jpg) | CC0 |
| 17 | [hanami-japanese-cherry-blossom-picnic](https://www.nipponferry.com/things-to-do/hanami-japanese-cherry-blossom-picnic/) | 도쿄 우에노공원에서 벚꽃 아래 피크닉을 즐기는 하나미 실사. 실제 하나미 소풍 사례이며 현재 개화 및 공원 규칙은 달라질 수 있습니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Hanami_Matsuri_picknick_in_Ueno_park%2C_Tokyo_Japan.jpg) | CC BY-SA 4.0 |
| 18 | [momijigari-japanese-autumn-leaves-culture](https://www.nipponferry.com/things-to-do/momijigari-japanese-autumn-leaves-culture/) | 교토 에이칸도 사찰에서 촬영한 가을 단풍 실제 사진. 실제 가을 풍경의 한 시점이며 현재 단풍 현황을 나타내지 않습니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:EikandoMomiji.jpg) | Public domain |
| 19 | [koinobori-childrens-day-japan](https://www.nipponferry.com/things-to-do/koinobori-childrens-day-japan/) | 2014년 일본 사가미강 고이노보리 축제에서 촬영한 잉어깃발. 고이노보리 실사이며 해당 행사의 올해 개최 여부를 보장하지 않습니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Koinobori_matsuri_at_Sagami_River%2C_Sagamihara%3B_May_2014_%2809%29.jpg) | CC BY 2.0 |
| 20 | [tanabata-japanese-star-festival](https://www.nipponferry.com/things-to-do/tanabata-japanese-star-festival/) | 2008년 센다이 다나바타 축제에 걸린 전통 장식 실제 사진. 실제 다나바타 축제 장식이며 현재 행사 일정 및 장소 운영과는 별개입니다. | [원본 사진](https://commons.wikimedia.org/wiki/File:Sendai-tanabata-streamers-aug2008.jpg) | CC BY 3.0 |

## 검수 범위 한계

- 브라우저에서 자동으로 확인한 것은 즐길거리 카드와 포토스팟의 실제 페이지 렌더링·이미지 로딩·가로 넘침·링크 동작이다. 모바일·PC에서 모든 화면의 수동 디자인 미세조정까지 전수 검수한 것은 아니다.
- 포토스팟 새 페이지의 지역별 대표 이미지는 기존 사이트의 지역 이미지를 재사용한다. 각 구체적 촬영 명소의 현장 사진을 각각 개별 촬영·검증해 놓았다고 주장하지 않는다.
- 위 152편 결과는 **즐길거리 카드**에 관한 것이지 사이트 전체의 모든 이미지 출처·저작권을 검증한 결과는 아니다.

