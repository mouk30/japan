"use strict";
/* V306: a truthful, accessible fallback for failed Wikimedia hotlinks on existing /food/ cards.
   Keep original image URLs, alt descriptions and credited sources unchanged. */
(() => {
  const externalPrefix = "https://upload.wikimedia.org/";
  const images = document.querySelectorAll(".hub-main .dirgrid .dircard > img");
  for (const img of images) {
    if (!img.getAttribute("src")?.startsWith(externalPrefix)) continue;
    const card = img.closest(".dircard");
    if (!card) continue;
    const showFallback = () => {
      if (card.classList.contains("nf-v306-photo-failed")) return;
      const fallback = document.createElement("span");
      fallback.className = "nf-v306-image-fallback";
      fallback.setAttribute("role", "img");
      fallback.setAttribute("aria-label", "외부 사진을 불러오지 못했습니다. 사진 원본과 저작권은 페이지 아래 사진 출처에서 확인할 수 있습니다.");
      const headline = document.createElement("strong");
      headline.textContent = "사진을 표시할 수 없습니다";
      const detail = document.createElement("small");
      detail.textContent = "여행 가이드와 사진 출처는 계속 확인할 수 있습니다";
      fallback.append(headline, detail);
      img.insertAdjacentElement("afterend", fallback);
      card.classList.add("nf-v306-photo-failed");
      const disclosure = card.querySelector(".v36-food-photo-note");
      if (disclosure) disclosure.textContent = "외부 사진 로딩 실패 · 원본 출처는 하단 확인";
    };
    img.addEventListener("error", showFallback, {once: true});
    if (img.complete && img.naturalWidth === 0) showFallback();
  }
})();
