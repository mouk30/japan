"""Explicit V307 allowlist: one verified /food/ card photo and its exact attribution.
Keep older V305/V306 regression gates strict for all unrelated changes.
"""
REPLACEMENTS = (
    ('alt="시모노세키 가라토시장의 초밥 실제 사진"',
     'alt="시모노세키 가라토시장 외관 · 2023년 6월 촬영"'),
    ('src="https://upload.wikimedia.org/wikipedia/commons/d/d5/Karato_market%2C_Shimonoseki.jpg"',
     'src="https://upload.wikimedia.org/wikipedia/commons/0/00/Karato_Fish_Market%2C_Shimonoseki_-_Jun_24%2C_2023.jpg"'),
    ('<span class="v36-food-photo-note">실제 주제 사진</span><div class="dirin"><small>시모노세키 · 시장 여행</small>',
     '<span class="v36-food-photo-note">가라토시장 실사 · 2023년 촬영</span><div class="dirin"><small>시모노세키 · 시장 여행</small>'),
    ('<li>시모노세키 가라토시장의 초밥 실제 사진 — <a href="https://commons.wikimedia.org/wiki/File:Karato_market%2C_Shimonoseki.jpg" target="_blank" rel="noopener noreferrer">Maria-Yamaguchi / Wikimedia Commons</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener noreferrer">CC BY-SA 4.0</a></li>',
     '<li>시모노세키 가라토시장 외관 · 2023년 6월 24일 촬영 (원본 4032×3024px, 4:3 카드 크롭) — <a href="https://commons.wikimedia.org/wiki/File:Karato_Fish_Market%2C_Shimonoseki_-_Jun_24%2C_2023.jpg" target="_blank" rel="noopener noreferrer">bryan... / Wikimedia Commons · Flickr 원본</a> · <a href="https://creativecommons.org/licenses/by-sa/2.0/" target="_blank" rel="noopener noreferrer">CC BY-SA 2.0</a></li>'),
)

def allow_verified_v307_photo(baseline):
    for old, new in REPLACEMENTS:
        if old in baseline:
            assert baseline.count(old) == 1, "Ambiguous V307 baseline"
            baseline = baseline.replace(old, new)
    return baseline
