/* NIPPONFERRY V93: consent-gated GA4 ferry journey events. No analytics ID = no collection.
 * Events are only declared from trusted operator/route links. No PII, URLs, dates or fares in custom parameters.
 */
(function () {
  'use strict';
  var tag = document.currentScript;
  var measurementId = (tag && tag.getAttribute('data-nf-ga4')) || '';
  if (!/^G-[A-Z0-9]{7,15}$/.test(measurementId)) return;

  var consentKey = 'nf93_analytics_choice_v1';
  var storage = {
    get: function () { try { return localStorage.getItem(consentKey); } catch (_) { return null; } },
    set: function (v) { try { localStorage.setItem(consentKey, v); } catch (_) {} }
  };
  var enabled = false;
  var started = false;

  function cleanRoute(str) {
    var s = String(str || '').toLowerCase();
    if (s.indexOf('osaka') >= 0) return 'osaka';
    if (s.indexOf('fukuoka') >= 0 || s.indexOf('hakata') >= 0) return 'fukuoka';
    if (s.indexOf('shimonoseki') >= 0) return 'shimonoseki';
    if (s.indexOf('tsushima') >= 0 || s.indexOf('hitakatsu') >= 0 || s.indexOf('izuhara') >= 0 || s.indexOf('daemado') >= 0) return 'tsushima';
    return 'unknown';
  }
  function pageArea() {
    var p = location.pathname || '/';
    if (p === '/' || p === '/index.html') return 'home';
    if (p.indexOf('/booking/japan-cruise/') === 0) return 'booking_hub';
    if (p.indexOf('/ferry/') === 0) return 'ferry_hub';
    if (p.indexOf('/guide/busan-') === 0) return 'route_guide';
    return 'editorial';
  }
  function getPlacement(link) {
    if (link.closest('#nf91-direct-operators')) return 'hub_card';
    if (link.closest('.nf86-intro')) return 'guide_hero';
    if (link.closest('.nf86-booking')) return 'guide_end';
    if (link.closest('.nf86-side')) return 'guide_sidebar';
    if (link.closest('.nf84-route')) return 'route_banner';
    return 'other';
  }
  function categorize(link) {
    if (!link || !link.href) return null;
    var url;
    try { url = new URL(link.href, location.href); } catch (_) { return null; }
    if (url.protocol !== 'https:' && url.protocol !== 'http:') return null;
    var source = pageArea(), placement = getPlacement(link);
    var route = cleanRoute(link.closest('[data-route]') && link.closest('[data-route]').getAttribute('data-route'));
    if (route === 'unknown') route = cleanRoute(location.pathname);
    if (route === 'unknown') route = cleanRoute(url.pathname);
    var host = url.hostname.toLowerCase();
    var operator = null, step = 'other';

    if (host === 'www.panstarcruise.com' || host === 'panstarcruise.com') {
      operator = 'panstar'; step = url.pathname.indexOf('/product/') === 0 ? 'route_info' : 'operator_search';
      if (route === 'unknown') route = cleanRoute(url.pathname);
    } else if (['www.koreaferry.co.kr','koreaferry.co.kr','www.koreaferry.kr','koreaferry.kr'].indexOf(host) >= 0) {
      operator = 'koreaferry'; step = url.pathname.indexOf('/rs/idv/reservation/') === 0 ? 'booking_search' : 'operator_home';
      if (route === 'unknown') route = 'fukuoka';
    } else if (['www.kampuferry.co.jp','kampuferry.co.jp','yoyaku.kampuferry.co.jp'].indexOf(host) >= 0) {
      operator = 'kampuferry'; step = 'booking_instructions';
      if (route === 'unknown') route = 'shimonoseki';
    } else if (host === location.hostname.toLowerCase()) {
      var isGuide = /^\/guide\/busan-(osaka|fukuoka|shimonoseki|tsushima)-ferry\/?$/.test(url.pathname);
      if (isGuide) return { name: 'ferry_route_select', route: cleanRoute(url.pathname),
        placement: placement, page_area: source, operator: 'internal', destination_step: 'route_guide' };
      if (url.pathname === '/ferry/' || url.pathname === '/booking/japan-cruise/') {
        return { name: 'ferry_hub_open', route: 'unknown', placement: placement, page_area: source,
          operator: 'internal', destination_step: 'booking_hub' };
      }
      if (link.classList.contains('nf92-side-link') || link.classList.contains('nf92-facts-link') || link.classList.contains('nf91-direct-secondary')) {
        return { name: 'ferry_info_open', route: route, placement: placement, page_area: source,
          operator: 'internal', destination_step: 'operator_facts' };
      }
      return null;
    } else {
      return null; // no tracking of unrelated external links
    }

    // Provider route/fare instructions are not the same as booking/search handoff.
    // Count approved official destination clicks; segment downstream by destination_step.
    return { name: 'ferry_operator_click', route: route, placement: placement,
      page_area: source, operator: operator, destination_step: step };
  }
  function track(spec) {
    if (!enabled || !started || typeof window.gtag !== 'function' || !spec) return;
    var allowed = ['route','placement','page_area','operator','destination_step'];
    var p = {};
    allowed.forEach(function (k) { p[k] = spec[k] || 'unknown'; });
    p.transport_type = 'beacon';
    window.gtag('event', spec.name, p);
  }
  function start() {
    if (started) { enabled = true; return; }
    started = true; enabled = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', measurementId, {send_page_view: true, anonymize_ip: true});
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
    document.head.appendChild(script);
    // Comparable denominators for aggregate 'button clicks per page view'.
    // These are NOT unique visitors, confirmed reservations or purchase conversions.
    var area = pageArea();
    if (area === 'ferry_hub' || area === 'booking_hub') {
      track({name:'ferry_hub_view',route:'all',placement:'page',page_area:area,
        operator:'internal',destination_step:'hub_view'});
    } else if (area === 'route_guide') {
      track({name:'ferry_route_view',route:cleanRoute(location.pathname),placement:'page',
        page_area:area,operator:'internal',destination_step:'guide_view'});
    }
  }

  // Prevent accidental click double count when multiple listeners/elements are nested.
  document.addEventListener('click', function (event) {
    if (!event.isTrusted || !enabled) return;
    var link = event.target && event.target.closest ? event.target.closest('a[href]') : null;
    if (!link) return;
    track(categorize(link));
  }, true);

  function render() {
    if (!document.body) return;
    var footer = document.querySelector('footer') || document.body;
    var control = document.createElement('button');
    control.type = 'button'; control.className = 'nf93-manage';
    control.textContent = '방문 통계 설정';
    control.setAttribute('aria-label','익명 방문 통계 수집 동의 설정');
    control.addEventListener('click', function () { dialog.hidden = false; });
    footer.appendChild(control);

    var dialog = document.createElement('section');
    dialog.className = 'nf93-consent';
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-label', '방문 통계 수집 선택');
    dialog.innerHTML = '<strong>예약 안내 이용 통계</strong>' +
      '<p>어떤 항로의 공식 예약 버튼이 눌리는지 집계해 안내를 개선합니다. 동의하면 Google Analytics가 방문·클릭 정보를 처리합니다. 여권·이름·예약일·결제정보는 이벤트에 보내지 않습니다. 동의하지 않아도 예약 링크를 이용할 수 있습니다.</p>' +
      '<div class="nf93-consent-actions"><button type="button" class="nf93-accept">통계 수집 허용</button><button type="button" class="nf93-reject">허용 안 함</button></div>';
    document.body.appendChild(dialog);
    function decide(value) {
      storage.set(value);
      if (value === 'yes') start();
      else {
        enabled = false;
        // Explicitly revoke data collection on subsequent interactions, including after opt-in.
        if (typeof window.gtag === 'function') window.gtag('consent','update',{analytics_storage:'denied'});
      }
      dialog.hidden = true;
    }
    dialog.querySelector('.nf93-accept').addEventListener('click',function () { decide('yes'); });
    dialog.querySelector('.nf93-reject').addEventListener('click',function () { decide('no'); });
    var choice = storage.get();
    dialog.hidden = choice === 'yes' || choice === 'no';
    if (choice === 'yes') start();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',render,{once:true});
  else render();
})();
