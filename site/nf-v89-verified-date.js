/* V89: no API/availability promises. Age comes only from editorial verification date. */
(() => {
  const oneDay = 86400000;
  const parseDate = (value) => {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return null;
    const date = new Date(value + 'T00:00:00Z');
    return Number.isFinite(date.getTime()) && date.toISOString().slice(0,10) === value ? date : null;
  };
  const today = new Date();
  const utcToday = Date.UTC(today.getFullYear(),today.getMonth(),today.getDate());
  document.querySelectorAll('.nf89-review[data-verified-on]').forEach((section) => {
    const verified = parseDate(section.dataset.verifiedOn);
    const status = section.querySelector('.nf89-review__status');
    if (!verified || !status) return;
    const days = Math.max(0,Math.floor((utcToday - verified.getTime())/oneDay));
    section.dataset.age = days >= 45 ? 'overdue' : days >= 21 ? 'review' : 'checked';
    if (days >= 45) {
      status.textContent = '마지막 정보 대조 후 ' + days + '일 경과 · 공지 재검증 필요. 예약 가능·정상 운항 보장이 아닙니다.';
    } else if (days >= 21) {
      status.textContent = '마지막 정보 대조 후 ' + days + '일 경과 · 최신 요금·항차를 선사에서 다시 확인하세요.';
    } else {
      status.textContent = '과거 공개 자료 대조일입니다. 실시간 운항·요금·예약 가능 여부를 확인한 것이 아닙니다.';
    }
  });
})();
