"""V308: exactly one source-verified Yamaguchi fugu image and attribution update."""
REPLACEMENTS = [["alt=\"일본 복어회 사진 · 시모노세키 현지 촬영 아님\"","alt=\"야마구치현에서 촬영된 복어회 · 시모노세키 현지 촬영 아님\""],["src=\"https://upload.wikimedia.org/wikipedia/commons/4/42/Fugo-sashimi.jpg\"","src=\"https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Fugu_sashimi_%2832738795990%29.jpg/1280px-Fugu_sashimi_%2832738795990%29.jpg\""],["<span class=\"v36-food-photo-note\">실제 주제 사진</span><div class=\"dirin\"><small>시모노세키 · 먹거리 베스트</small>","<span class=\"v36-food-photo-note\">야마구치현 복어회 · 2016년 촬영</span><div class=\"dirin\"><small>시모노세키 · 먹거리 베스트</small>"],["<li>일본 복어회 사진 · 시모노세키 현지 촬영 아님 — <a href=\"https://commons.wikimedia.org/wiki/File:Fugo-sashimi.jpg\" target=\"_blank\" rel=\"noopener noreferrer\">Hajime NAKANO / Wikimedia Commons</a> · <a href=\"https://creativecommons.org/licenses/by/2.0/\" target=\"_blank\" rel=\"noopener noreferrer\">CC BY 2.0</a></li>","<li>야마구치현 복어회 · 2016년 10월 9일 촬영, 시모노세키 현지 촬영 아님 (원본 5739×3826px, 1280px 축소·4:3 카드 크롭) — <a href=\"https://commons.wikimedia.org/wiki/File:Fugu_sashimi_%2832738795990%29.jpg\" target=\"_blank\" rel=\"noopener noreferrer\">Raita Futo / Wikimedia Commons · Flickr 원본</a> · <a href=\"https://creativecommons.org/licenses/by/2.0/\" target=\"_blank\" rel=\"noopener noreferrer\">CC BY 2.0</a></li>"]]

def allow_verified_v308_photo(baseline):
    for old, new in REPLACEMENTS:
        if old in baseline:
            assert baseline.count(old) == 1, "Ambiguous V308 baseline"
            baseline = baseline.replace(old, new)
    return baseline
