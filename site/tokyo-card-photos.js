/* Tokyo photo accuracy gate, 2026-10-17.
  NO category-wide substitutions and NO fallback photo.
  Only exact named subject -> existing editorial asset. Verify asset source/license
  and real-world depiction before growing the list. */
(()=>{"use strict";
const verifiedCandidates={
"tokyo-odaiba-waterfront-yurikamome":{src:"/images/editorial/tokyo-yurikamome-automated-train.webp",alt:"도쿄 유리카모메 열차 관련 이미지",caption:"유리카모메 참고 이미지"},
"tokyo-cruise-odaiba-3hours":{src:"/images/editorial/tokyo-cruise-port-day-trip.webp",alt:"도쿄 크루즈 기항지 관련 이미지",caption:"도쿄항 참고 이미지"}
};
document.querySelectorAll(".tky-card").forEach((card,i)=>{
 const slug=(card.getAttribute("href")||"").split("/").filter(Boolean).pop();
 const item=verifiedCandidates[slug];
 if(!item||card.querySelector("img"))return;
 const fig=document.createElement("span");fig.className="tky-card-photo";
 const img=document.createElement("img");
 img.src=item.src;img.alt=item.alt;img.loading=i<6?"eager":"lazy";
 img.decoding="async";img.width=720;img.height=420;
 img.addEventListener("error",()=>fig.remove(),{once:true});
 fig.append(img);card.insertBefore(fig,card.firstChild);
});
})();