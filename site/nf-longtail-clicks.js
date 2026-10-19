/* NIPPONFERRY long-tail click events: tracking-ready, not an analytics backend. */
(function () {
  'use strict';
  const group = 'longtail_ferry_trial';
  const urls = [
    '/japan-cruise/busan-hakata-ferry-reservation/',
    '/japan-cruise/bukan-ferry-shimonoseki-price/',
    '/japan-cruise/panstar-miracle-osaka-cabin-types/'
  ];
  if (!urls.includes(window.location.pathname)) return;
  document.addEventListener('click', function (event) {
    const element = event.target;
    const link = element && element.closest ? element.closest('a[href]') : null;
    if (!link) return;
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#')) return;
    let destination;
    try { destination = new URL(link.href, window.location.href); }
    catch (_) { return; }
    const internalBooking = destination.origin === window.location.origin && destination.pathname === '/booking/japan-cruise/';
    const officialOutbound = /^https?:$/.test(destination.protocol) && destination.origin !== window.location.origin;
    if (!internalBooking && !officialOutbound) return;
    const directBooking = officialOutbound && /\/rs\/idv\/reservation\//.test(destination.pathname) &&
      /(^|\.)koreaferry\.co\.kr$/.test(destination.hostname);
    const payload = {
      experiment: group,
      page_path: window.location.pathname,
      link_type: internalBooking ? 'internal_booking_guide' : (directBooking ? 'operator_booking_start' : 'operator_official_info'),
      destination_host: destination.hostname,
      destination_path: destination.pathname
    };
    // These calls emit events ONLY if an existing analytics collector is configured.
    // Neither branch records payments, confirmed reservations, or personal data.
    if (typeof window.gtag === 'function') {
      window.gtag('event', 'nf_travel_link_click', payload);
    } else if (window.google_tag_manager && Array.isArray(window.dataLayer)) {
      window.dataLayer.push({event: 'nf_travel_link_click', ...payload});
    }
  }, {capture: true});
}());
