/* GreenNode · Hyper-Targeted campaign draft
   One scroll-driven story for the hero + section 2 (replaces the original intro scroll code on hyper.html).

   How it works
   - The sticky intro (.sov-intro) gets a longer runway (hyper/story.css). Scroll position -> target progress 0..1.
   - Progress is smoothed every animation frame (exponential damping, TAU), so each wheel "notch"
     becomes a soft glide instead of a jump.
   - Every visual is a pure function of that progress, so scrolling up plays the story backwards.
   - Each scroll beat has its own motion. Short one-shot effects (blink, border-gate flash, pulse rings,
     padlock pop, LED chase) fire when a beat is crossed going forward.
   - A spring adds natural swing to the claw (and the block it carries) whenever it moves.

   Beats (progress)                                                  Process bar
   0.000-0.020  idle: claw bobs, invites the first scroll            1
   0.020-0.095  scan line classifies the global pile                 1
   0.095-0.205  pick customer data -> HAN                            2
   0.205-0.290  pick payments      -> HCM                            3
   0.290-0.375  pick eKYC          -> HAN                            4
   0.375-0.460  pick AI training   -> HCM                            5
   0.460-0.520  seal the Vietnam zone                                6
   0.520-0.880  section 2, local time o = 0..1
                o 0.00-0.70 title out, panel grows into the map, the board slides away,
                            the 4 protected workloads fly home to Vietnam              7
                o 0.56-0.80 the 5 availability zones light up (2 Hanoi, 3 HCMC), then blink 8
   0.880-1.000  hold (absorbs the smoothing lag before the section unpins) */
(function () {
  'use strict';
  var root = document.querySelector('.sov-intro[data-hyper]');
  var scene = document.getElementById('claw-scene');
  if (!root || !scene) return;

  var $ = function (s, r) { return (r || root).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || scene).querySelectorAll(s)); };

  /* =========================================================
     Math helpers
     ========================================================= */
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
  var c01 = function (v) { return clamp(v, 0, 1); };
  var seg = function (t, a, b) { return c01((t - a) / (b - a)); };          // 0..1 inside [a, b]
  var lerp = function (a, b, t) { return a + (b - a) * t; };
  var easeIO = function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
  var easeOut = function (t) { return 1 - Math.pow(1 - t, 3); };
  var easeBack = function (t) { var c1 = 1.2, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
  var easeQ = function (n, a, b) { var t = seg(n, a, b); return 1 - (1 - t) * (1 - t); };   // easing of the original intro
  var bez = function (a, c, b, t) { var u = 1 - t; return u * u * a + 2 * u * t * c + t * t * b; };
  var U = function (n) { return 'calc(var(--sov-u) * ' + n + ')'; };

  /* =========================================================
     Icons: 24 x 24, filled + rounded (GreenNode icon style).
     g / gs = glyph (currentColor) · c / cs = cut-out detail (var(--ic-cut) = the surface behind the icon)
     ========================================================= */
  var g = function (d) { return '<path class="g" d="' + d + '"/>'; };
  var c = function (d) { return '<path class="c" d="' + d + '"/>'; };
  var gs = function (d, w) { return '<path class="gs" stroke-width="' + w + '" d="' + d + '"/>'; };
  var cs = function (d, w) { return '<path class="cs" stroke-width="' + w + '" d="' + d + '"/>'; };
  var gc = function (x, y, r) { return '<circle class="g" cx="' + x + '" cy="' + y + '" r="' + r + '"/>'; };
  var cc = function (x, y, r) { return '<circle class="c" cx="' + x + '" cy="' + y + '" r="' + r + '"/>'; };
  var LOCK_BODY = g('M5.4 12.6a2 2 0 0 1 2-2h9.2a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H7.4a2 2 0 0 1-2-2z') +
    c('M12 13.4a1.5 1.5 0 0 1 .7 2.83v1.37h-1.4v-1.37A1.5 1.5 0 0 1 12 13.4z');
  var ICONS = {
    // Customer data: database + user badge
    db: g('M3.5 6.2C3.5 4.4 6.9 3 11 3s7.5 1.4 7.5 3.2v10.6c0 1.8-3.4 3.2-7.5 3.2s-7.5-1.4-7.5-3.2z') +
        cs('M3.5 6.2c0 1.8 3.4 3.2 7.5 3.2s7.5-1.4 7.5-3.2M3.5 11.6c0 1.8 3.4 3.2 7.5 3.2s7.5-1.4 7.5-3.2', 1.5) +
        cc(17.8, 17.6, 5.9) + gc(17.8, 17.6, 4.6) + cc(17.8, 16.1, 1.45) +
        c('M15.2 20.3c.5-1.4 1.5-2.1 2.6-2.1s2.1.7 2.6 2.1z'),
    // Payments: card + exchange arrows
    pay: g('M2.5 7.5A2.5 2.5 0 0 1 5 5h13a2.5 2.5 0 0 1 2.5 2.5v8a2.5 2.5 0 0 1-2.5 2.5H5a2.5 2.5 0 0 1-2.5-2.5z') +
         c('M2.5 8.4h18v2.4h-18z') + cs('M5.6 14h4.4', 1.6) +
         cc(18.2, 18.2, 5.7) + gc(18.2, 18.2, 4.5) +
         cs('M16 16.9h4.3M19.1 15.7l1.2 1.2-1.2 1.2M20.4 19.6h-4.3M17.3 18.4l-1.2 1.2 1.2 1.2', 1.2),
    // eKYC: face inside a scan frame
    kyc: gs('M3.5 8.2V6a2.5 2.5 0 0 1 2.5-2.5h2.2M15.8 3.5H18A2.5 2.5 0 0 1 20.5 6v2.2M20.5 15.8V18a2.5 2.5 0 0 1-2.5 2.5h-2.2M8.2 20.5H6A2.5 2.5 0 0 1 3.5 18v-2.2', 2) +
         gc(12, 9.8, 3.2) + g('M6.9 17.1c.7-2.3 2.8-3.8 5.1-3.8s4.4 1.5 5.1 3.8c.2.6-.3 1.2-.9 1.2H7.8c-.6 0-1.1-.6-.9-1.2z'),
    // AI training: AI chip
    ai: gs('M9 2.9v2.3M12 2.9v2.3M15 2.9v2.3M9 18.8v2.3M12 18.8v2.3M15 18.8v2.3M2.9 9h2.3M2.9 12h2.3M2.9 15h2.3M18.8 9h2.3M18.8 12h2.3M18.8 15h2.3', 1.8) +
        g('M5.2 8.2a3 3 0 0 1 3-3h7.6a3 3 0 0 1 3 3v7.6a3 3 0 0 1-3 3H8.2a3 3 0 0 1-3-3z') +
        cs('M8.5 15.3l2.2-6.6h.6l2.2 6.6M9.3 13.2h3.4M15.5 8.7v6.6', 1.5),
    // Website: browser window
    web: g('M2.5 7A2.5 2.5 0 0 1 5 4.5h14A2.5 2.5 0 0 1 21.5 7v10a2.5 2.5 0 0 1-2.5 2.5H5A2.5 2.5 0 0 1 2.5 17z') +
         cc(5.6, 7.3, 0.9) + cc(8.1, 7.3, 0.9) + cc(10.6, 7.3, 0.9) +
         cs('M2.5 10h19', 1.3) + cs('M6 13.2h7M6 16.2h10', 1.6),
    // CDN: globe
    cdn: gc(12, 12, 9) +
         cs('M12 3.3c-2.3 2.3-3.5 5.2-3.5 8.7s1.2 6.4 3.5 8.7M12 3.3c2.3 2.3 3.5 5.2 3.5 8.7s-1.2 6.4-3.5 8.7M3.8 9h16.4M3.8 15h16.4', 1.4),
    // Dev / Test: code window
    dev: g('M3 6.5A3.5 3.5 0 0 1 6.5 3h11A3.5 3.5 0 0 1 21 6.5v11a3.5 3.5 0 0 1-3.5 3.5h-11A3.5 3.5 0 0 1 3 17.5z') +
         cs('M9.2 9.2L6.4 12l2.8 2.8M14.8 9.2l2.8 2.8-2.8 2.8M13 8.3l-2 7.4', 1.7),
    // Media: play
    media: g('M2.5 7.5a3 3 0 0 1 3-3h13a3 3 0 0 1 3 3v9a3 3 0 0 1-3 3h-13a3 3 0 0 1-3-3z') +
           c('M10 9.3v5.4c0 .7.8 1.1 1.4.7l4-2.7c.5-.3.5-1.1 0-1.4l-4-2.7c-.6-.4-1.4 0-1.4.7z'),
    lockOpen: gs('M8.4 10.6V8.4a3.6 3.6 0 0 1 7.05-1.05', 2.2) + LOCK_BODY,
    lockClosed: gs('M8.4 10.6V8.4a3.6 3.6 0 0 1 7.2 0v2.2', 2.2) + LOCK_BODY,
    shield: g('M12 2.5l7.5 2.8v5.6c0 4.8-3.2 8.7-7.5 10.6-4.3-1.9-7.5-5.8-7.5-10.6V5.3z') + cs('M8.6 12.1l2.3 2.3 4.6-4.6', 2),
    cloud: g('M7 19a5 5 0 0 1-.6-9.96A6 6 0 0 1 17.9 9.6 4.75 4.75 0 0 1 17.5 19z'),
    arrow: gs('M12 4.5v14M6.5 13l5.5 5.5 5.5-5.5', 2.4)
  };
  function iconSvg(key, cls) {
    return '<svg class="hc-ico ' + (cls || '') + '" viewBox="0 0 24 24" aria-hidden="true">' + ICONS[key] + '</svg>';
  }

  /* =========================================================
     Claw: rounded vector on a 20 x 24 grid (same silhouette as the pixel version)
     ========================================================= */
  var CLAW_TOP =
    '<rect class="ck" x="7.6" y="0" width="4.8" height="2.6" rx="1.1"/>' +
    '<rect class="cw" x="8.8" y=".75" width="2.4" height="1.1" rx=".55"/>' +
    '<rect class="ck" x="3.6" y="2" width="12.8" height="6.6" rx="2.2"/>' +
    '<rect class="cw" x="4.5" y="2.9" width="11" height="4.8" rx="1.5"/>' +
    '<rect class="cl" x="13.4" y="2.9" width="2.1" height="4.8" rx="1"/>' +
    '<rect class="cm" x="5.3" y="4.1" width="8.4" height="2.4" rx="1.1"/>' +
    '<circle class="ck" cx="7.3" cy="5.3" r=".62"/><circle class="ck" cx="9.5" cy="5.3" r=".62"/><circle class="ck" cx="11.7" cy="5.3" r=".62"/>' +
    '<rect class="ck" x="7" y="8" width="6" height="2" rx=".9"/>' +
    '<rect class="cw" x="7.8" y="8.5" width="3.8" height="1" rx=".5"/>';
  var CLAW_PLATE =
    '<rect class="ck" x="3.8" y="9.3" width="12.4" height="2.1" rx="1.05"/>' +
    '<rect class="cw" x="4.6" y="9.85" width="10.4" height="1" rx=".5"/>';
  var CLAW_ARMS = {
    open:   { l: 'M5.2 10.4L1.4 13.4V22.3', r: 'M14.8 10.4L18.6 13.4V22.3', el: [1.4, 13.4], er: [18.6, 13.4], tl: [1.4, 22.3], tr: [18.6, 22.3] },
    half:   { l: 'M5.2 10.4L1.9 13.4V19Q1.9 21 3.6 22.3', r: 'M14.8 10.4L18.1 13.4V19Q18.1 21 16.4 22.3', el: [1.9, 13.4], er: [18.1, 13.4], tl: [3.6, 22.3], tr: [16.4, 22.3] },
    closed: { l: 'M5.2 10.4L2.6 13.4V18Q2.6 20.6 6 22.2', r: 'M14.8 10.4L17.4 13.4V18Q17.4 20.6 14 22.2', el: [2.6, 13.4], er: [17.4, 13.4], tl: [6, 22.2], tr: [14, 22.2] }
  };
  // Pixel claw (20 x 24 px) — the original version
  var PAL = { W: '#ffffff', L: '#d4ffe4', M: '#b4ffd0', D: '#0a602a', K: '#00210d' };
  var PX_TOP = ['........KKKK........', '........KWLK........', '.....KKKKKKKKKK.....', '....KWWWWWWWWWLK....',
    '....KWMMMMMMMMLK....', '....KWMKMKMKMMLK....', '....KLLLLLLLLLLK....', '.....KKKKKKKKKK.....',
    '.......KWWLLK.......', '....KKWWWWWLLLKK....', '...LW..........WL...', '..LW............WL..', '.LW..............WL.'];
  var PX_ARMS = {
    closed: ['.KK..............KK.', '.KK..............KK.', '.LW..............WL.', '.LW..............WL.', '.LW..............WL.', '.LW..............WL.', '.LW..............WL.', '..LW............WL..', '...LW..........WL...', '....LWD......DWL....', '....................'],
    half: ['KK................KK', 'KK................KK', 'LW................WL', 'LW................WL', '.LW..............WL.', '.LW..............WL.', '.LW..............WL.', '..LW............WL..', '..LWD..........DWL..', '....................', '....................'],
    open: ['KK................KK', 'KK................KK', 'LW................WL', 'LW................WL', 'LW................WL', 'LW................WL', 'LW................WL', 'LW................WL', 'DW................WD', '....................', '....................']
  };
  function clawSvg(grip) {
    var rows = PX_TOP.concat(PX_ARMS[grip]), out = '';
    rows.forEach(function (row, y) {
      for (var x = 0; x < row.length; x++) if (row[x] !== '.')
        out += '<rect x="' + x + '" y="' + y + '" width="1.02" height="1.02" fill="' + PAL[row[x]] + '"/>';
    });
    return '<svg class="hc-f hc-f--' + grip + '" viewBox="0 0 20 24" shape-rendering="crispEdges" aria-hidden="true">' + out + '</svg>';
  }

  /* =========================================================
     Board layout (board units; board = 400 x 670)
     ========================================================= */
  var TILE = 66;
  var colX = function (c) { return 25 + 70.5 * c; };
  var FLOOR = 650;
  var rowY = function (r) { return FLOOR - TILE - 70.6 * (3 - r); };
  var BORDER = 272, GLOBAL_TOP = 283, RAIL_Y = 30;
  var CLAW_W = 90, CLAW_H = 108, GRIP = 31.5;                      // claw = 20 x 24 grid at 4.5u
  var REST_TOP = 34, CARRY_Y = 66, REST_X = colX(2);
  var PED_TOP = 144, PED_W = 156, PED_TOP_H = 88, PED_FRONT_H = 18, BAY_Y = 152;
  var PEDS = [
    { x: 22,  name: 'HAN · Hanoi',       bays: [30, 104] },
    { x: 222, name: 'HCM · Ho Chi Minh', bays: [230, 304] }
  ];
  var PICKS = [
    { r: 0, c: 1, ped: 0, bay: 0, icon: 'db',  name: 'Customer\ndata' },
    { r: 1, c: 3, ped: 1, bay: 0, icon: 'pay', name: 'Payments' },
    { r: 1, c: 0, ped: 0, bay: 1, icon: 'kyc', name: 'eKYC' },
    { r: 0, c: 4, ped: 1, bay: 1, icon: 'ai',  name: 'AI\ntraining' }
  ];
  var GENERAL = [
    [2, 0, '#2c716c', 'cdn', 'CDN'],        [3, 0, '#1a4d4b'],
    [1, 1, '#22605c'], [2, 1, '#2c716c', 'media', 'Media'], [3, 1, '#3c8580'],
    [1, 2, '#3c8580', 'web', 'Website'],    [2, 2, '#22605c'], [3, 2, '#2c716c'],
    [2, 3, '#1a4d4b'],                      [3, 3, '#2c716c', 'dev', 'Dev / Test'],
    [1, 4, '#3c8580'], [2, 4, '#22605c'],   [3, 4, '#1a4d4b']
  ];

  /* =========================================================
     Story timeline
     ========================================================= */
  var IDLE_B = 0.02;
  var SCAN = { a: 0.02, b: 0.095 };
  var PICK_RANGES = [[0.095, 0.205], [0.205, 0.29], [0.29, 0.375], [0.375, 0.46]];
  var SEAL = { a: 0.46, b: 0.52 };
  var SEAL_AT = SEAL.a + (SEAL.b - SEAL.a) * 0.35;
  var S2 = { a: 0.52, b: 0.88 };
  var OUTRO = { a: 0.88, b: 0.985 };   // map shrinks + fades out, then the section unpins
  var mapX = 0;
  // Each workload flies to one availability zone (map % of the original pins), in section-2 time o.
  // Landing order follows the pins' own reveal order: HAN-01, HAN-02, then HCM.
  var FLY = [
    { o: [0.03, 0.56], pin: { x: 26.12, y: 13.33 } },    // Customer data -> HAN
    { o: [0.09, 0.66], pin: { x: 35.04, y: 78.06 } },    // Payments      -> HCM
    { o: [0.06, 0.60], pin: { x: 32.41, y: 14.98 } },    // eKYC          -> HAN
    { o: [0.12, 0.70], pin: { x: 42.65, y: 79.72 } }     // AI training   -> HCM
  ];
  var PINS_IN = [0.56, 0.8];        // o range in which the 5 AZ pins pop in (staggered by the original CSS)
  var STEP_COUNT = 8;
  var TAU = 0.18;                   // seconds; scroll smoothing (higher = softer, more lag)

  var picks = PICKS.map(function (p, k) {
    return { p: p, a: PICK_RANGES[k][0], b: PICK_RANGES[k][1], sx: colX(p.c), sy: rowY(p.r), bx: PEDS[p.ped].bays[p.bay] };
  });
  picks.forEach(function (pk, k) {
    pk.px = k ? picks[k - 1].bx : REST_X;
    pk.scanAt = (FLOOR - (pk.sy + TILE / 2)) / (FLOOR - (BORDER + 14));
  });

  /* =========================================================
     Board scene (inside the green SOVEREIGN board)
     ========================================================= */
  function blockInner(icon, name) {
    return iconSvg(icon, 'hc-icon') + '<span class="hc-name">' + name.replace('\n', '<br>') + '</span>';
  }
  scene.innerHTML =
    // Global zone (Figma 'KV Board / 07 Sealed'): flat teal from y 283, topped by a row of 11 square merlons (21.8, step 37.92, r 1.9) from y 272
    '<i class="hc-global" style="top:' + U(GLOBAL_TOP) + '"></i>' +
    Array.apply(null, Array(11)).map(function (_, i) {
      return '<i class="hc-merlon" style="left:' + U(-1 + 37.92 * i) + ';top:' + U(BORDER) + '"></i>';
    }).join('') +
    '<span class="hc-zl hc-zl--vn" style="top:' + U(8) + '">' + iconSvg('shield', 'hc-zl-ic') +
      'GreenNode Sovereign AI Cloud</span>' +
    '<span class="hc-zl hc-zl--gl" style="top:' + U(BORDER + 24) + '">' + iconSvg('cloud', 'hc-zl-ic') + 'GLOBAL CLOUD</span>' +
    '<i class="hc-rail" style="top:' + U(RAIL_Y) + '"></i>' +
    '<i class="hc-handle" style="left:' + U(20.5) + ';top:' + U(RAIL_Y - 4.5) + '"></i>' +
    '<i class="hc-handle" style="left:' + U(370.5) + ';top:' + U(RAIL_Y - 4.5) + '"></i>' +
    PEDS.map(function (p) {
      return '<div class="hc-ped" style="left:' + U(p.x) + ';top:' + U(PED_TOP) + ';width:' + U(PED_W) +
          ';height:' + U(PED_TOP_H + PED_FRONT_H) + '">' +
        '<i class="hc-ped-top" style="height:' + U(PED_TOP_H) + '"></i>' +
        p.bays.map(function (bx) {
          return '<i class="hc-socket" style="left:' + U(bx - p.x) + ';top:' + U(BAY_Y - PED_TOP) + '"></i>';
        }).join('') +
        '<div class="hc-ped-front" style="top:' + U(PED_TOP_H) + ';height:' + U(PED_FRONT_H) + '">' +
          '<span>' + p.name + '</span><span class="hc-leds"><i class="hc-led"></i><i class="hc-led"></i></span>' +
        '</div>' +
      '</div>';
    }).join('') +
    '<i class="hc-gate" id="hc-gate" style="top:' + U(BORDER - 8) + '"></i>' +
    GENERAL.map(function (q) {
      return '<div class="hc-block hc-gen" style="transform:translate(' + U(colX(q[1])) + ',' + U(rowY(q[0])) +
        ');background:' + q[2] + ';--ic-cut:' + q[2] + '">' + (q[3] ? blockInner(q[3], q[4]) : '') + '</div>';
    }).join('') +
    '<i class="hc-sweep" id="hc-sweep"></i>' +
    '<i class="hc-scan" id="hc-scan"></i>' +
    '<div class="hc-claw" id="hc-claw" data-grip="open" style="width:' + U(CLAW_W) + '">' +
      '<i class="hc-cable" id="hc-cable" style="left:' + U(CLAW_W / 2 - 1) + ';top:' + U(RAIL_Y) + '"></i>' +
      '<div class="hc-head" id="hc-head" style="width:' + U(CLAW_W) + ';height:' + U(CLAW_H) + '">' +
        '<div class="hc-swing" id="hc-swing">' + clawSvg('open') + clawSvg('half') + clawSvg('closed') + '</div>' +
      '</div>' +
    '</div>';

  var claw = document.getElementById('hc-claw'),
      cable = document.getElementById('hc-cable'),
      clawHead = document.getElementById('hc-head'),
      swing = document.getElementById('hc-swing'),
      gate = document.getElementById('hc-gate'),
      sweepEl = document.getElementById('hc-sweep'),
      scanEl = document.getElementById('hc-scan'),
      boardBox = scene.parentElement;
  var pedEls = $$('.hc-ped');
  var leds = picks.map(function (pk) { return $$('.hc-led', pedEls[pk.p.ped])[pk.p.bay]; });

  var tiles = picks.map(function (pk) {
    var el = document.createElement('div');
    el.className = 'hc-block hc-work is-hidden';
    el.innerHTML = blockInner(pk.p.icon, pk.p.name) +
      '<i class="hc-lock">' + iconSvg('lockOpen', 'hc-lock-open') + iconSvg('lockClosed', 'hc-lock-closed') + '</i>';
    el.style.transformOrigin = U(TILE / 2) + ' ' + U(-GRIP);   // = the claw pivot, so a held block swings with it
    scene.insertBefore(el, sweepEl);
    return el;
  });

  /* =========================================================
     Section 2 layer (flying workloads + process bar)
     ========================================================= */
  var stage = $('.sov-intro__stage'), container = $('.sov-intro__container'), row = $('.sov-intro__row'),
      surface = $('.sov-intro__surface'), map = $('.sov-intro__map'), lead = $('.sov-intro__note'),
      head = $('.sov-intro__head'), note = $('.sov-intro__panel--note'), flow = $('.sov-intro__panel--flow'),
      boardEl = $('.sov-intro__board');

  var layer = document.createElement('div');
  layer.className = 'hx-layer';
  var bar = '';
  for (var i = 0; i < STEP_COUNT; i++) bar += '<i></i>';
  layer.innerHTML =
    PICKS.map(function (p) {
      return '<i class="hx-ghost"></i><i class="hx-ghost"></i>' +
        '<div class="hx-fly"><div class="hx-fly-in">' + blockInner(p.icon, p.name) + '</div></div>';
    }).join('') +
    '<div class="hx-steps"><div class="hx-steps__bar">' + bar + '</div>' + iconSvg('arrow', 'hx-steps__arrow') + '</div>';
  stage.appendChild(layer);

  // 5 availability zones (2 Hanoi, 3 HCMC): square pins, pop in as the workloads land, then blink
  var AZ = [[26.12, 13.33, 0.56], [32.41, 14.98, 0.60], [35.04, 78.06, 0.66], [41.08, 75.25, 0.68], [42.65, 79.72, 0.70]];
  var azEls = AZ.map(function (a) {
    var p = document.createElement('i');
    p.className = 'hx-pin'; p.style.left = a[0] + '%'; p.style.top = a[1] + '%';
    map.appendChild(p);
    return p;
  });
  var flyers = $$('.hx-fly', layer), ghosts = $$('.hx-ghost', layer),
      steps = layer.querySelector('.hx-steps'), bars = $$('.hx-steps__bar i', layer);

  /* =========================================================
     One-shot effects
     ========================================================= */
  function blink(el) { el.classList.remove('is-target'); void el.offsetWidth; el.classList.add('is-target'); }
  function rings(x, y) {
    [0, 170].forEach(function (d) {
      var r = document.createElement('i');
      r.className = 'hc-ring';
      r.style.left = U(x); r.style.top = U(y);         // left/top so the CSS `scale` grows around the block
      r.style.animationDelay = d + 'ms';
      scene.insertBefore(r, sweepEl);
      setTimeout(function () { r.remove(); }, 1000 + d);
    });
  }
  function gateFlash(x) {
    gate.style.transform = 'translateX(' + U(x - 8) + ')';
    if (gate.animate) gate.animate([{ opacity: 0 }, { opacity: 1, offset: 0.25 }, { opacity: 0 }], { duration: 480, easing: 'linear' });
  }

  /* =========================================================
     Board render (hero beats)
     ========================================================= */
  function pickPose(pk, q) {
    var s, downTop = pk.sy - GRIP, carryTop = CARRY_Y - GRIP, bayTop = BAY_Y - GRIP;
    var pose = { x: pk.sx, top: REST_TOP, grip: 'open', hold: false, jig: 0 };
    if (q < 0.16) { s = q / 0.16; pose.x = lerp(pk.px, pk.sx, easeIO(s)); }                              // travel
    else if (q < 0.30) { s = (q - 0.16) / 0.14; pose.top = lerp(REST_TOP, downTop, easeBack(s)); }        // drop (bounce)
    else if (q < 0.38) {                                                                                  // grip: 3 frames
      s = (q - 0.30) / 0.08; pose.top = downTop;
      pose.grip = s < 0.34 ? 'open' : s < 0.67 ? 'half' : 'closed'; pose.hold = s >= 0.67;
    }
    else if (q < 0.42) {                                                                                  // strain / tug
      s = (q - 0.38) / 0.04; pose.top = downTop - 4 * easeOut(s); pose.grip = 'closed'; pose.hold = true;
      pose.jig = Math.sin(s * Math.PI * 3) * 1.6;
    }
    else if (q < 0.62) { s = (q - 0.42) / 0.20; pose.top = lerp(downTop - 4, carryTop, easeIO(s)); pose.grip = 'closed'; pose.hold = true; } // lift
    else if (q < 0.80) { s = (q - 0.62) / 0.18; pose.x = lerp(pk.sx, pk.bx, easeIO(s)); pose.top = carryTop; pose.grip = 'closed'; pose.hold = true; } // carry
    else if (q < 0.90) { s = (q - 0.80) / 0.10; pose.x = pk.bx; pose.top = lerp(carryTop, bayTop, easeBack(s)); pose.grip = 'closed'; pose.hold = true; } // lower
    else if (q < 0.94) { s = (q - 0.90) / 0.04; pose.x = pk.bx; pose.top = bayTop; pose.grip = s < 0.5 ? 'half' : 'open'; } // release
    else { s = (q - 0.94) / 0.06; pose.x = pk.bx; pose.top = lerp(bayTop, REST_TOP, easeIO(s)); }        // rise
    return pose;
  }

  var swingA = 0, swingV = 0, lastClawX = REST_X, forward = false, states = [];
  var lastBoardT = -1;

  function renderBoard(T, dt, time) {
    // idle bob at the start, and again (gentle sway) once all 4 workloads are home
    var idle = Math.max(1 - seg(T, 0, IDLE_B), easeIO(seg(T, SEAL_AT, SEAL.b)));
    var settled = Math.abs(swingA) < 0.01 && Math.abs(swingV) < 0.01;
    if (T === lastBoardT && settled && idle === 0) return;
    lastBoardT = T;

    var pose = { x: REST_X, top: REST_TOP, grip: 'open', hold: -1, jig: 0 };
    for (var k = 0; k < picks.length; k++) {
      var pk = picks[k];
      if (T >= pk.a && T < pk.b) {
        var pp = pickPose(pk, seg(T, pk.a, pk.b));
        pose = { x: pp.x, top: pp.top, grip: pp.grip, hold: pp.hold ? k : -1, jig: pp.jig };
        break;
      }
    }
    if (T >= picks[3].b) pose.x = lerp(picks[3].bx, REST_X, easeIO(seg(T, SEAL.a, SEAL_AT)));
    pose.top += Math.sin(time * 1.9) * 1.6 * idle;

    if (dt > 0) {
      var vx = (pose.x - lastClawX) / dt;
      var targetA = clamp(vx * 0.018, -9, 9) + Math.sin(time * 1.3) * (T >= SEAL_AT ? 3 : 1.2) * idle;
      swingV += (-60 * (swingA - targetA) - 7 * swingV) * dt;
      swingA += swingV * dt;
    } else { swingA = 0; swingV = 0; }
    lastClawX = pose.x;

    claw.style.transform = 'translateX(' + U(pose.x - (CLAW_W - TILE) / 2) + ')';
    clawHead.style.transform = 'translateY(' + U(pose.top) + ')';
    swing.style.transform = 'rotate(' + swingA.toFixed(2) + 'deg)';
    cable.style.height = U(Math.max(0, pose.top - RAIL_Y));
    if (claw.dataset.grip !== pose.grip) claw.dataset.grip = pose.grip;

    var sP = seg(T, SCAN.a, SCAN.b);
    picks.forEach(function (pk, k) {
      var el = tiles[k], q = seg(T, pk.a, pk.b);
      var attached = pose.hold === k, home = q >= 0.9, x, y, rot = 0;
      if (attached) { x = pose.x + pose.jig; y = pose.top + GRIP; rot = swingA; }
      else if (home) { x = pk.bx; y = BAY_Y; }
      else { x = pk.sx; y = pk.sy; }
      el.style.transform = 'translate(' + U(x) + ',' + U(y) + ') rotate(' + rot.toFixed(2) + 'deg)';
      setState(k, {
        tagged: sP >= pk.scanAt || q > 0,
        crossed: home || (attached && y + TILE / 2 < BORDER),
        home: home
      });
    });

    var sy = Math.round(lerp(FLOOR, BORDER + 14, sP) / 4) * 4;
    scanEl.style.transform = 'translateY(' + U(sy) + ')';
    scanEl.style.opacity = sP > 0 && sP < 1 ? '1' : '0';

    var e = seg(T, SEAL_AT, SEAL.b);
    sweepEl.style.transform = 'translateY(' + U(Math.round(lerp(BORDER - 24, -24, e) / 4) * 4) + ')';
    sweepEl.style.opacity = e > 0 && e < 1 ? '1' : '0';
    scene.classList.toggle('is-sealed', T >= SEAL_AT);
  }

  function setState(k, s) {
    var el = tiles[k], prev = states[k] || {};
    if (s.tagged !== prev.tagged) {
      el.classList.toggle('is-tagged', s.tagged); el.classList.toggle('is-hidden', !s.tagged);
      if (s.tagged && forward) blink(el);
    }
    if (s.crossed !== prev.crossed) {
      el.classList.toggle('is-crossed', s.crossed);
      if (s.crossed && !s.home && forward) gateFlash(picks[k].sx);
    }
    if (s.home !== prev.home) {
      el.classList.toggle('is-home', s.home);
      leds[k].classList.toggle('is-on', s.home);
      if (s.home && forward) rings(picks[k].bx, BAY_Y);
    }
    states[k] = s;
  }

  /* =========================================================
     Section 2 (original intro motion + workloads flying home + AZ pins)
     ========================================================= */
  var LIVE = 'sov-intro--live';
  var m = { ready: false };
  var query = window.matchMedia('(min-width: 992px) and (min-height: 480px) and (prefers-reduced-motion: no-preference)');

  function leadFactor() {
    var v = parseFloat(window.getComputedStyle(note).getPropertyValue('--sov-lead-scale'));
    return isFinite(v) && v > 0 ? v : 1.8;
  }
  function reset() {
    [head, boardEl, map, lead].forEach(function (el) { el.style.transform = ''; });
    ['width', 'height', 'margin-left', 'border-color', 'border-radius', '--sov-pins'].forEach(function (p) { note.style.removeProperty(p); });
    ['height', 'flex'].forEach(function (p) { flow.style.removeProperty(p); });
    ['width', 'height'].forEach(function (p) { surface.style.removeProperty(p); });
    root.classList.remove('sov-intro--done', 'flow-out', 'sov-intro--pins');
  }
  function measure() {
    reset();
    root.classList.add(LIVE);
    var e = stage.getBoundingClientRect(), i = row.getBoundingClientRect(), o = container.getBoundingClientRect(),
        r = note.getBoundingClientRect(), l = head.getBoundingClientRect(), gR = flow.getBoundingClientRect(),
        b = boardEl.getBoundingClientRect(), C = parseFloat(window.getComputedStyle(stage).top);
    m.stickyTop = isFinite(C) ? C : 0;
    m.headOut = l.bottom - e.top;
    m.flowOut = Math.max(0, o.right - gR.left);
    m.noteWidth = r.width; m.noteHeight = r.height;
    m.endWidth = o.width; m.endHeight = e.height;
    m.bleed = Math.max(0, i.left - o.left);
    flow.style.flex = '0 0 ' + gR.width + 'px';
    surface.style.width = o.width + 'px'; surface.style.height = e.height + 'px';
    var y = lead.getBoundingClientRect(), L = window.getComputedStyle(note),
        inner = r.width - (parseFloat(L.paddingLeft) || 0) - (parseFloat(L.paddingRight) || 0),
        Uf = 1 / leadFactor();
    m.leadStart = y.width > 0 ? Math.min(Uf, inner / y.width) : Uf;
    m.leadDrop = (y.height / 2) * (1 - m.leadStart);
    m.leadRise = e.top + e.height / 2 - (y.top + y.height / 2);
    m.leadXTravel = o.left + o.width / 2 - (r.left + r.width / 2);
    m.mapOut = Math.max(0, note.clientWidth - (map.offsetLeft - map.offsetWidth / 2));
    // stage coordinates for the flight paths
    m.sH = e.height;
    m.cL = o.left - e.left; m.cW = o.width;
    m.boardX = b.left - e.left; m.boardY = b.top - e.top; m.u = b.width / 400;
    m.flow = { x: gR.left - e.left, y: gR.top - e.top };
    m.mapH = 0.869 * e.height; m.mapW = m.mapH * 0.630795;
    m.mapL = m.cL + m.cW / 2 + 31.5 - m.mapW / 2; m.mapT = e.height / 2 - m.mapH / 2;
    m.pin = 0.0499 * m.mapW;                                                   // original pin size
    m.targets = FLY.map(function (f) { return { x: m.mapL + f.pin.x / 100 * m.mapW, y: m.mapT + f.pin.y / 100 * m.mapH }; });
    m.ready = r.width > 0 && r.height > 0 && o.width > 0 && e.height > 0 && y.width > 0;
    if (!m.ready) { root.classList.remove(LIVE); return; }
    layer.style.setProperty('--fu', m.u + 'px');
  }
  function shiftAt(o) {          // how far the note panel has pushed the board (original behaviour)
    var r = easeQ(o, 0, 0.6), W = m.noteWidth + (m.endWidth - m.noteWidth) * r;
    return W - m.noteWidth - m.bleed * r;
  }

  var lastO = -1;
  function renderIntro(o) {
    root.classList.toggle('sov-intro--done', o >= 0.8);
    head.style.transform = 'translate3d(0,' + (-m.headOut * easeQ(o, 0, 0.3)) + 'px,0)';
    var r = easeQ(o, 0, 0.6), l = easeQ(o, 0, 0.42);
    var W = m.noteWidth + (m.endWidth - m.noteWidth) * r,
        H = m.noteHeight + (m.endHeight - m.noteHeight) * l;
    note.style.width = W + 'px'; note.style.height = H + 'px'; note.style.marginLeft = (-m.bleed * r) + 'px';
    var rad = 12 * (1 - l);
    note.style.borderRadius = rad + 'px ' + rad + 'px 0 0';
    note.style.borderColor = rad > 2 ? '' : 'transparent';
    flow.style.height = H + 'px';
    var push = shiftAt(o);
    boardEl.style.transform = 'translate3d(' + push + 'px,0,0)';
    root.classList.toggle('flow-out', push >= m.flowOut);
    mapX = m.mapOut * (1 - r);
    var j = easeQ(o, 0.1, 0.7);
    lead.style.transform = 'translate(calc(-50% + ' + (m.leadXTravel * (j - r)) + 'px), ' +
      (m.leadDrop + (m.leadRise - m.leadDrop) * j) + 'px) scale(' + (m.leadStart + (1 - m.leadStart) * j) + ')';
    // the 5 availability zones (2 Hanoi, 3 HCMC) pop in as the workloads land, then blink
    AZ.forEach(function (a, k) {
      var on = o >= a[2];
      if (on !== azEls[k].classList.contains('is-in')) azEls[k].classList.toggle('is-in', on);
    });
    map.classList.toggle('hx-done', o >= 0.77);
  }

  function renderSection2(o) {
    if (o === lastO) return;
    var S0 = TILE * m.u;
    picks.forEach(function (pk, k) {
      var f0 = FLY[k].o[0], f1 = FLY[k].o[1], t = seg(o, f0, f1);
      tiles[k].style.visibility = o >= f0 ? 'hidden' : '';
      var fl = flyers[k], g1 = ghosts[k * 2], g2 = ghosts[k * 2 + 1];
      if (o >= f0 && o < f1) {
        var x0 = m.boardX + shiftAt(f0) + pk.bx * m.u + S0 / 2, y0 = m.boardY + BAY_Y * m.u + S0 / 2;
        var ex = m.targets[k].x, ey = m.targets[k].y, cx = (x0 + ex) / 2 - 60, cy = Math.min(y0, ey) - 150;
        var place = function (el, tt, op, k2) {
          var te = easeIO(c01(tt)), s = lerp(1, m.pin / S0, te) * k2;
          el.style.transform = 'translate(' + (bez(x0, cx, ex, te) - S0 / 2) + 'px,' + (bez(y0, cy, ey, te) - S0 / 2) + 'px) scale(' + s + ')';
          el.style.opacity = op;
        };
        place(fl, t, t > 0.94 ? (1 - t) / 0.06 : 1, 1);           // hands over to the pin on landing
        place(g1, t - 0.06, t > 0.1 ? 0.25 : 0, 0.55);
        place(g2, t - 0.12, t > 0.16 ? 0.12 : 0, 0.4);
        fl.classList.toggle('is-pin', t > 0.8);
      } else { fl.style.opacity = 0; g1.style.opacity = 0; g2.style.opacity = 0; }
    });

    // process bar: fades out in the white flow panel, reappears at the bottom-left of the map
    var inMap = o >= 0.2, show = seg(o, 0.34, 0.48);
    var sx = inMap ? m.cL + 48 : m.flow.x + 36,
        sy = inMap ? m.sH - 56 + (1 - easeOut(show)) * 16 : m.flow.y + 34;
    steps.style.transform = 'translate(' + sx + 'px,' + sy + 'px)';
    steps.style.opacity = (inMap ? show : 1 - seg(o, 0.02, 0.12)).toFixed(3);
    steps.style.setProperty('--hx-arrow', inMap ? '1' : '0');
    lastO = o;
  }

  /* =========================================================
     Process bar
     ========================================================= */
  var curStep = 0;
  function stepFor(T, o) {
    if (T < SCAN.b) return 1;
    for (var k = 0; k < picks.length; k++) if (T < picks[k].b) return 2 + k;
    if (T < SEAL.b) return 6;
    return o < PINS_IN[0] ? 7 : 8;
  }
  function setStep(n) {
    if (n === curStep) return;
    curStep = n;
    bars.forEach(function (b, i) { b.classList.toggle('is-done', i < n - 1); b.classList.toggle('is-cur', i === n - 1); });
  }

  /* =========================================================
     Main loop: scroll -> smoothed progress -> render
     ========================================================= */
  var target = 0, cur = 0, prevCur = 0, raf = null, lastTs = 0, primed = false;
  // Mode C (data-mode="c"): hero autoplays, only the board -> map hand-off is scroll-driven (short runway)
  var MODE_C = root.getAttribute('data-mode') === 'c', AUTO_DUR = 7, auto = 0, skip = null;
  if (MODE_C) {
    skip = document.createElement('button');
    skip.type = 'button'; skip.className = 'hx-skip';
    skip.innerHTML = 'Bỏ qua ' + iconSvg('arrow', 'hx-skip__ic');
    skip.addEventListener('click', function () {
      var r = root.getBoundingClientRect();
      window.scrollTo({ top: window.scrollY + r.bottom - m.stickyTop, behavior: 'smooth' });
    });
    stage.appendChild(skip);
  }
  function readTarget() {
    var rect = root.getBoundingClientRect(), span = rect.height - stage.offsetHeight - m.stickyTop;
    return span > 0 ? c01(-rect.top / span) : 0;
  }
  function render(T, dt, time) {
    renderBoard(T, dt, time);
    var o = seg(T, S2.a, S2.b);
    if (o !== lastO) renderIntro(o);
    renderSection2(o);
    // outro: the map (with its AZ pins) shrinks and fades before the section unpins
    var x = easeIO(seg(T, OUTRO.a, OUTRO.b));
    map.style.transform = 'translate(calc(-50% + ' + mapX + 'px), -50%) scale(' + (1 - 0.35 * x).toFixed(4) + ')';
    map.style.opacity = (1 - x).toFixed(3);
    if (x > 0) steps.style.opacity = Math.min(+steps.style.opacity, 1 - x).toFixed(3);
    setStep(stepFor(T, o));
  }
  function frame(ts) {
    raf = requestAnimationFrame(frame);
    if (!m.ready || !query.matches) return;
    var dt = lastTs ? Math.min(0.05, (ts - lastTs) / 1000) : 0.016;
    lastTs = ts;
    target = readTarget();
    if (MODE_C) {
      // hero plays on its own (AUTO_DUR s, 4x faster once the user scrolls); scroll only drives section 2
      auto = Math.min(SEAL.b, auto + dt * (SEAL.b / AUTO_DUR) * (target > 0.001 ? 4 : 1));
      target = auto < SEAL.b ? auto : SEAL.b + target * (1 - SEAL.b);
      if (skip) skip.classList.toggle('is-off', cur >= OUTRO.a);
    }
    prevCur = cur;
    if (!primed) { cur = target; primed = true; }
    else { cur += (target - cur) * (1 - Math.exp(-dt / TAU)); if (Math.abs(target - cur) < 0.00005) cur = target; }
    forward = primed && cur > prevCur + 1e-7;
    render(cur, dt, ts / 1000);
  }

  function staticState() {             // mobile, small screens, reduced motion: show the end of the hero story
    root.classList.remove(LIVE); reset(); m.ready = false;
    layer.style.display = 'none';
    tiles.forEach(function (t) { t.style.visibility = ''; });
    forward = false; lastBoardT = -1;
    renderBoard(SEAL.b, 0, 0);
    boardBox.style.backgroundColor = '';
  }
  function onViewportChange() {
    if (!query.matches) { staticState(); return; }
    layer.style.display = '';
    measure();
    lastO = -1; lastBoardT = -1; primed = false;
  }

  if (query.addEventListener) query.addEventListener('change', onViewportChange);
  window.addEventListener('resize', onViewportChange, { passive: true });
  onViewportChange();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(onViewportChange);
  window.addEventListener('load', onViewportChange);

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      var vis = es.some(function (e) { return e.isIntersecting; });
      if (vis && raf === null) { lastTs = 0; raf = requestAnimationFrame(frame); }
      else if (!vis && raf !== null) { cancelAnimationFrame(raf); raf = null; }
    }).observe(root);
    var heroIO = new IntersectionObserver(function (es) {
      if (es[es.length - 1].isIntersecting) { root.classList.add('hero-entered'); heroIO.disconnect(); }
    }, { rootMargin: '0px 0px -15% 0px' });
    heroIO.observe(head);
  } else {
    root.classList.add('hero-entered');
    raf = requestAnimationFrame(frame);
  }
})();
