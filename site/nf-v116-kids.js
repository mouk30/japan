/* V116: filters only published guide links; no hotel availability assertions. */
(()=>{"use strict";
const area=document.getElementById("kids-area"),age=document.getElementById("kids-age"),type=document.getElementById("kids-type");
const rows=[...document.querySelectorAll("#kids-result-grid .kid-card")];
const count=document.getElementById("kids-result-count"),empty=document.getElementById("kids-empty"),reset=document.getElementById("kids-reset");
if(!area||!age||!type||!count||!reset)return;
function render(){
 let visible=0;
 for(const row of rows){
  const matchArea=area.value==="all"||row.dataset.area==="all"||row.dataset.area===area.value;
  const matchAge=age.value==="all"||row.dataset.age==="all"||row.dataset.age===age.value;
  const matchType=type.value==="all"||row.dataset.type===type.value;
  row.hidden=!(matchArea&&matchAge&&matchType);
  if(!row.hidden)visible++;
 }
 count.textContent=String(visible);
 empty.hidden=visible!==0;
}
for(const select of [area,age,type])select.addEventListener("change",render);
reset.addEventListener("click",()=>{area.value="all";age.value="all";type.value="all";render();});
render();
})();