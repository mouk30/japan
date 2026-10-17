/* Tokyo thumbnails: show a photograph only when it depicts the exact subject.
   Other cards stay text-first until individually reviewed photographs are added. */
(()=>{"use strict";
const exact={
"tokyo-cruise-odaiba-3hours":"/images/editorial/tokyo-cruise-port-day-trip.webp",
"tokyo-odaiba-waterfront-yurikamome":"/images/editorial/tokyo-yurikamome-automated-train.webp",
"tokyo-ramen-best-areas":"/images/culture-verified/ramen-japanese-noodle-evolution.webp",
"tokyo-yakitori-izakaya-guide":"/images/culture-verified/yakitori-japanese-skewer-culture.webp",
"tokyo-depachika-food-halls":"/images/culture-verified/depachika-japanese-department-food.webp",
"tokyo-kissaten-retro-cafe":"/images/culture-verified/kissaten-japanese-retro-coffee.webp",
"tokyo-matcha-wagashi":"/images/culture-verified/matcha-sencha-japanese-green-tea.webp"
};
document.querySelectorAll(".tky-card").forEach((card,i)=>{
const slug=(card.getAttribute("href")||"").split("/").filter(Boolean).pop();
const src=exact[slug];if(!src||card.querySelector("img"))return;
const fig=document.createElement("span");fig.className="tky-card-photo";
const img=document.createElement("img");img.src=src;
img.alt="글 주제를 보여주는 참고 사진";img.loading=i<6?"eager":"lazy";
img.decoding="async";img.width=720;img.height=420;
fig.append(img);card.insertBefore(fig,card.firstChild);
});
})();