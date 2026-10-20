# V68 · 원본 사진 검증 후 게시하기

**현재 상태: 원본 미확보 / 이미지 미교체.** Wikimedia 원본 자동 다운로드가 HTTP 429로 차단되어 있습니다. 검증 없이 AI 이미지를 대체하지 않습니다.

## 지정한 4개 원본
| 기존 페이지 | 필요한 원본명 | 촬영 대상 | 사용 조건 |
| --- | --- | --- | --- |
| 미야지마 페리 | Miyajima-Ferry-STA JR-Gate.jpg | **미야지마섬 측** JR 페리 개찰구 및 매표소. 미야지마구치가 아님 | MaedaAkihiko, CC BY-SA 4.0 |
| 쇼도시마 페리 | Shodo-shima ferry port in Tonosho (6453360287).jpg | 도노쇼항, 과거 2010년 모습 | Maarten Heerlien, CC BY 2.0 |
| 슈리성 | Shuri Castle Reconstruction.jpg | 2025년 2월 복원 공사 현장. 현재 완공 상태 아님 | おにく, CC0 |
| 요코하마 아카렌가 | 20250101 Yokohama Red Brick Warehouse 115522.jpg | 2025년 1월 아카렌가 건물 외관. 크루즈 부두 아님 | Matthide127, CC0 |

## 실제 적용 전 절차
1. Wikimedia Commons의 **각 File 페이지에서 원본 이미지**를 내려받습니다. 출처 기록: `audit-reports/v68/photo-source-candidates.json`.
2. 원본을 위 파일명 그대로 저장소 내 `photo-intake/v68/`에 배치합니다.
3. 담당자가 각 사진을 열어 건물/표지/선착장 등의 **실제 장소**가 해당 페이지 설명과 일치하는지 시각 검토합니다. CC BY/CC BY-SA 사진의 저자·라이선스·원본 링크와 WebP 가공 사실을 명시합니다. CC BY-SA 사진은 변경·재사용 의무도 검토합니다.
4. 원본 확보 및 검토가 끝난 경우에만 `python scripts/v68_verified_photo_replacement.py` 를 실행합니다.
5. WebP 용량·ALT·캡션·canonical·파비콘·JSON-LD가 정상인지 검사하고 공개 PC/모바일을 재검증합니다.

**중요:** 원본이 없으면 스크립트는 실패하도록 보호됩니다. 이 절차는 사진의 진위에 대한 자동 보증이 아니며 수동 시각 대조가 필요합니다.


## V68 수동 검수 승인 파일 (필수)
원본 4개 파일을 저장한 뒤, 이미지별 실제 장소 대조·라이선스 검증 담당자가 `photo-intake/v68/visual-review-approval.json`을 작성합니다. 사진이 원본 URL에서 왔는지 확인하고 원본 SHA-256을 기재해야 합니다. 승인 정보가 없거나 파일 해시가 바뀌면 **교체·게시가 즉시 중단**됩니다.

```json
{
  "hiroshima-miyajima-ferry-crossing": {
    "original_sha256": "실제_원본_파일_SHA256",
    "confirmed_depicted_location": true,
    "license_verified": true,
    "reviewer": "검수자",
    "reviewed_at": "YYYY-MM-DD"
  }
}
```

동일 구조로 나머지 3곳도 입력합니다. `confirmed_depicted_location`은 사진 속 개찰구가 **미야지마섬 측**임을 직접 확인한 경우에만 true를 입력합니다. 슈리성은 2025년 공사 사진임을 반드시 표시합니다. 이 파일은 검수 기록일 뿐, 조작된 승인값까지 소프트웨어가 판단할 수 없으므로 사람이 원본을 육안 확인해야 합니다.
