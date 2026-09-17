/* ==========================================================================
   site.js · the interaction layer shared by every page. No dependencies.
   Shared with johnjayasankar.com; on Labs the palette reads JJ.builds.

   chrome     floating header, Work menu, drawer, scroll progress, clock, to-top
   motion     reveal on arrival, count-up figures, segmented-control indicators,
              the tabbed showcase under the home hero
   copy       email, links, case briefs; one toast reports every result
   bays       each system's story steps through its phases on one shared clock;
              phase tabs hold a phase, telemetry and the rail report position
   thumbs     stories at rest that wake on hover, or play while they are in view
   locus      j / k through whatever the page is made of, with Enter, y, t,
              e, digits and arrows; the palette's keys group lists them all
   palette    ⌘K / Ctrl K: systems, pages, notes, actions, keys
   work       facet filtering with URL state
   case       beat scroll-spy, segmented progress, copy beat and brief, embeds
   approach   the autonomy ladder
   simple     section locus, email reveal
   memory     the continue chip and 404 recents, from localStorage if allowed
   ========================================================================== */
(function () {
  'use strict';

  var doc = document, root = doc.documentElement, body = doc.body;
  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function mq(q) { return !!(window.matchMedia && window.matchMedia(q).matches); }

  var page = root.getAttribute('data-page') || '';
  var JJ = window.JJ || { systems: [], notes: [], pages: [], links: {} };
  var LINKS = JJ.links || {};
  var EMAIL = LINKS.email || 'johnjayasankar@gmail.com';
  var REDUCED = mq('(prefers-reduced-motion: reduce)');
  var FINE = mq('(pointer: fine)');
  var IS_MAC = /Mac|iPhone|iPad|iPod/.test(navigator.platform || '') || /Mac OS X/.test(navigator.userAgent || '');
  var MOD = IS_MAC ? '⌘K' : 'Ctrl K';
  var HAS_IO = 'IntersectionObserver' in window;

  root.classList.add('js');

  var store = {
    get: function (k, d) { try { var v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } }
  };
  if (store.get('jj:keys-learned', false)) root.classList.add('keys-on');

  /* shared state, declared up front because several modules read it */
  var locus = { current: null, until: 0 };
  var spies = [];
  var bays = [];
  var facetBtns = [];
  var rungs = [], ladderIdx = 0;
  var chipEl = null;
  var toggleEmail = function () {};
  var emailOpen = function () { return false; };
  var closeMega = function () { return false; };

  /* ---- platform key labels ------------------------------------------------ */
  if (!IS_MAC) {
    $$('[data-modkey]').forEach(function (el) { el.textContent = 'Ctrl '; });
    $$('[data-kbd]').forEach(function (el) { el.textContent = el.textContent.replace(/⌘K/g, 'Ctrl K'); });
    $$('kbd').forEach(function (el) { if (el.textContent === '⌘K') el.textContent = 'Ctrl K'; });
  }

  /* ---- toast and clipboard ---------------------------------------------- */
  var toastEl = $('[data-toast]'), toastTimer = 0;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove('is-on'); }, 2400);
  }
  function legacyCopy(text) {
    var ta = doc.createElement('textarea'), ok = false;
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;top:-1000px;left:0;opacity:0';
    body.appendChild(ta);
    ta.select();
    try { ok = doc.execCommand('copy'); } catch (e) { ok = false; }
    body.removeChild(ta);
    return ok;
  }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(function () { return true; }, function () { return legacyCopy(text); });
    }
    return Promise.resolve(legacyCopy(text));
  }
  function labelOf(el) { return (el && el.getAttribute('data-label')) || ''; }
  function copyEmail(btn) {
    copyText(EMAIL).then(function (ok) {
      toast(ok ? 'Email copied' : 'Could not copy. Select the address and copy.');
      if (ok && btn && btn.classList.contains('mail__copy')) {
        var was = btn.textContent;
        btn.textContent = 'Copied';
        btn.classList.add('is-done');
        setTimeout(function () { btn.textContent = was; btn.classList.remove('is-done'); }, 1800);
      }
    });
  }
  function linkFor(el) {
    var base = location.origin + location.pathname + location.search;
    return el && el.id && el.id !== 'top' && el.id !== 'dhead' ? base + '#' + el.id : base;
  }
  function copyLink(el) {
    var target = el || locus.current;
    var named = target && target.id && target.id !== 'top' && target.id !== 'dhead';
    copyText(linkFor(target)).then(function (ok) {
      toast(ok ? 'Copied · ' + (named ? labelOf(target) : (body.getAttribute('data-label') || 'page')) : 'Could not copy link');
    });
  }
  function copyBrief() {
    var el = $('#brief'), text = '';
    if (!el) return;
    try { text = JSON.parse(el.textContent).text; } catch (e) { return; }
    copyText(text).then(function (ok) { toast(ok ? 'Brief copied' : 'Could not copy brief'); });
  }

  /* ---- chrome --------------------------------------------------------------- */
  var hdr = $('[data-hdr]'), hdrBar = $('.hdr__bar'), beatbar = $('[data-beatbar]');
  var scrollFill = $('[data-scrollbar]'), totop = $('[data-totop]');
  var menuBtn = $('[data-menu]'), drawer = $('[data-drawer]');

  /* how much of the top of the viewport the fixed chrome covers */
  function headerOffset() {
    var h = hdrBar ? Math.max(0, hdrBar.getBoundingClientRect().bottom) : 0;
    if (beatbar) h += beatbar.getBoundingClientRect().height + 8;
    return h + 16;
  }
  function setDrawer(open) {
    if (!menuBtn || !drawer) return;
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    drawer.hidden = !open;
    if (hdr) hdr.classList.toggle('is-menu', open);
    if (open) { var first = $('a', drawer); if (first) first.focus(); }
  }
  if (menuBtn && drawer) {
    menuBtn.addEventListener('click', function () { setDrawer(drawer.hidden); });
    drawer.addEventListener('click', function (e) { if (e.target.closest('a')) setDrawer(false); });
    addEventListener('resize', function () { if (window.innerWidth > 900 && !drawer.hidden) setDrawer(false); });
  }

  var scrollQueued = false, lastY = 0, goingUp = false;
  function onScroll() {
    if (scrollQueued) return;
    scrollQueued = true;
    requestAnimationFrame(function () {
      scrollQueued = false;
      var y = window.scrollY || 0, max = root.scrollHeight - window.innerHeight;
      if (hdr) hdr.classList.toggle('is-float', y > 24);
      if (scrollFill) scrollFill.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0).toFixed(4) + ')';
      if (totop) {
        /* on a phone the button waits for a scroll back up, so it never sits on the text being read */
        if (Math.abs(y - lastY) > 8) { goingUp = y < lastY; lastY = y; }
        totop.classList.toggle('is-on', y > window.innerHeight * 1.1 && (goingUp || window.innerWidth > 760));
      }
      for (var i = 0; i < spies.length; i++) spies[i]();
    });
  }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);

  (function clock() {
    var clocks = $$('[data-clock]'), fmt = null;
    if (!clocks.length) return;
    try {
      fmt = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });
    } catch (e) { return; }
    function tick() {
      var s = 'NY ' + fmt.format(new Date());
      clocks.forEach(function (c) { c.textContent = s; c.hidden = false; c.setAttribute('aria-hidden', 'true'); });
    }
    tick();
    setInterval(tick, 15000);
  })();

  /* ---- the Work menu --------------------------------------------------------- */
  (function megaMenu() {
    var item = $('[data-mega]');
    if (!item) return;
    var btn = $('[data-mega-btn]', item), panel = $('[data-mega-panel]', item), timer = 0;
    function set(open) {
      item.classList.toggle('is-open', open);
      if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      /* the menu's picture loads the first time the menu opens, not with every page */
      if (open) $$('img[data-src]', item).forEach(function (im) { im.src = im.getAttribute('data-src'); im.removeAttribute('data-src'); });
    }
    if (FINE) {
      item.addEventListener('mouseenter', function () { clearTimeout(timer); timer = setTimeout(function () { set(true); }, 70); });
      item.addEventListener('mouseleave', function () { clearTimeout(timer); timer = setTimeout(function () { set(false); }, 160); });
    }
    if (btn) {
      btn.addEventListener('click', function () {
        var open = !item.classList.contains('is-open');
        set(open);
        if (open && panel) { var f = $('a', panel); if (f) f.focus(); }
      });
    }
    item.addEventListener('focusout', function (e) { if (!e.relatedTarget || !item.contains(e.relatedTarget)) set(false); });
    closeMega = function () {
      if (!item.classList.contains('is-open')) return false;
      set(false);
      if (btn) btn.focus();
      return true;
    };
  })();

  /* ---- memory: continue chip, 404 recents ---------------------------------- */
  var TRAIL_KEY = 'jj:trail';
  var herePath = location.pathname.replace(/\/+$/, '') || '/';
  var trail = store.get(TRAIL_KEY, []);
  if (!Array.isArray(trail)) trail = [];
  trail = trail.filter(function (t) {
    return t && typeof t.path === 'string' && /^\/(?!\/)/.test(t.path) && typeof t.at === 'number';
  });
  function ago(ts) {
    var s = (Date.now() - ts) / 1000;
    if (s < 60) return 'just now';
    if (s < 3600) return Math.floor(s / 60) + 'm ago';
    if (s < 86400) return Math.floor(s / 3600) + 'h ago';
    var d = Math.floor(s / 86400);
    return d === 1 ? 'yesterday' : d + 'd ago';
  }
  (function memory() {
    if (page === 'notfound') {
      var pathEl = $('[data-nf-path]'), list = $('[data-nf-list]'), wrap = $('[data-nf-recent]');
      if (pathEl) pathEl.textContent = location.pathname;
      var recent = trail.slice(0, 4);
      if (list && wrap && recent.length) {
        recent.forEach(function (t) {
          var li = doc.createElement('li'), a = doc.createElement('a');
          a.setAttribute('href', t.path);
          a.textContent = String(t.label || t.path);
          li.appendChild(a);
          list.appendChild(li);
        });
        wrap.hidden = false;
      }
      return;
    }
    var prev = null;
    for (var i = 0; i < trail.length; i++) {
      /* only a page from an earlier visit counts: the page just left is what Back is for */
      var age = Date.now() - trail[i].at;
      if (trail[i].path !== herePath && age > 30 * 60e3 && age < 14 * 864e5) { prev = trail[i]; break; }
    }
    if (prev) {
      $$('[data-continue]').forEach(function (a) {
        var l = $('[data-continue-label]', a), w = $('[data-continue-when]', a);
        a.setAttribute('href', prev.path);
        if (l) l.textContent = String(prev.label || prev.path);
        if (w) w.textContent = ago(prev.at);
        a.hidden = false;
      });
    }
    var here = { path: herePath, label: body.getAttribute('data-label') || doc.title, at: Date.now() };
    store.set(TRAIL_KEY, [here].concat(trail.filter(function (t) { return t.path !== herePath; })).slice(0, 8));
  })();

  /* ---- segmented controls: the white pill follows the selection ------------ */
  function placeSeg(seg) {
    var ind = $('.seg__ind', seg), on = $('[aria-pressed="true"], [aria-selected="true"]', seg);
    if (!ind || !on || !on.offsetWidth) return;
    ind.style.width = on.offsetWidth + 'px';
    ind.style.transform = 'translateX(' + on.offsetLeft + 'px)';
    if (!seg.classList.contains('is-ready')) requestAnimationFrame(function () { seg.classList.add('is-ready'); });
  }
  var segs = $$('[data-seg]');
  function placeSegs() { segs.forEach(placeSeg); }
  placeSegs();
  addEventListener('resize', placeSegs);
  if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(placeSegs);

  /* ---- reveal: blocks rise into place the first time they arrive ------------ */
  (function reveal() {
    var els = $$('[data-reveal]');
    if (!els.length) return;
    function settle(el) { el.classList.add('is-in'); }
    if (REDUCED || !HAS_IO) { els.forEach(settle); return; }
    var vh = window.innerHeight || 800;
    /* whatever is already on screen stays put: no flash, no late motion */
    els.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < vh * .94 && r.bottom > 0) settle(el);
    });
    root.classList.add('reveal-on');
    /* once a block has arrived its own hover transitions apply again */
    function release(el) {
      var d = parseFloat(getComputedStyle(el).getPropertyValue('--rd')) || 0;
      setTimeout(function () { el.classList.add('is-done'); }, 1300 + d * 90);
    }
    els.forEach(function (el) { if (el.classList.contains('is-in')) el.classList.add('is-done'); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        settle(en.target);
        release(en.target);
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0 });
    els.forEach(function (el) { if (!el.classList.contains('is-in')) io.observe(el); });
    addEventListener('beforeprint', function () { els.forEach(function (el) { el.classList.add('is-in', 'is-done'); }); });
  })();

  /* ---- figures count up when they arrive ------------------------------------ */
  (function countUp() {
    var els = $$('[data-count]');
    if (!els.length || REDUCED || !HAS_IO) return;
    function run(el) {
      var text = el.textContent, m = text.match(/\d+(?:\.\d+)?/);
      if (!m) return;
      var to = parseFloat(m[0]), dec = (m[0].split('.')[1] || '').length;
      var pre = text.slice(0, m.index), post = text.slice(m.index + m[0].length), t0 = 0;
      if (!(to > 0)) return;
      function frame(now) {
        if (!t0) t0 = now;
        var u = Math.min(1, (now - t0) / 1150), e = 1 - Math.pow(1 - u, 3);
        el.textContent = pre + (to * e).toFixed(dec) + post;
        if (u < 1) requestAnimationFrame(frame); else el.textContent = text;
      }
      requestAnimationFrame(frame);
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        io.unobserve(en.target);
        run(en.target);
      });
    }, { threshold: .6 });
    els.forEach(function (el) { io.observe(el); });
  })();

  /* ---- stories: the interface in each bay steps through its phases ---------- */
  function inSpec(spec, i) {
    return spec.split(',').some(function (p) {
      var m = p.split('-');
      if (m.length === 1) return +m[0] === i;
      return i >= (m[0] === '' ? 0 : +m[0]) && i <= (m[1] === '' ? 99 : +m[1]);
    });
  }
  function setStep(st, i) {
    if (!st || st.getAttribute('data-step') === String(i)) return;
    st.setAttribute('data-step', i);
    $$('[data-on]', st).forEach(function (el) { el.classList.toggle('is-on', inSpec(el.getAttribute('data-on'), i)); });
    if (REDUCED) return;
    /* a soft light crosses the window bar each time the story moves on */
    st.classList.remove('is-tick');
    void st.offsetWidth;
    st.classList.add('is-tick');
    clearTimeout(st.__tick);
    st.__tick = setTimeout(function () { st.classList.remove('is-tick'); }, 1100);
  }
  /* one clock per bay, all advanced by a single frame loop while their bays are on screen */
  var STEP_MS = 3400, clocks = [], ticking = false, lastTick = 0;
  function Clock(period, start, onCycle) {
    this.period = period;
    this.cyc = start;
    this.held = false;
    this.seen = false;
    this.onCycle = onCycle;
    clocks.push(this);
  }
  Clock.prototype.hold = function (c) {
    this.held = c != null;
    if (c != null) this.cyc = c;
    this.onCycle(this.cyc);
    wakeClocks();
  };
  function wakeClocks() {
    if (ticking || REDUCED) return;
    ticking = true;
    lastTick = 0;
    requestAnimationFrame(tickClocks);
  }
  function tickClocks(now) {
    var dt = lastTick ? Math.min(100, now - lastTick) : 0, live = false;
    lastTick = now;
    clocks.forEach(function (c) {
      if (c.held || c.paused || !c.seen || doc.hidden) return;
      live = true;
      c.cyc = (c.cyc + dt / c.period) % 1;
      c.onCycle(c.cyc);
    });
    if (live) requestAnimationFrame(tickClocks); else ticking = false;
  }
  doc.addEventListener('visibilitychange', wakeClocks);

  /* ---- bays ----------------------------------------------------------------- */
  function Bay(el) {
    var self = this;
    this.el = el;
    this.story = $('[data-story]', el);
    this.tabs = $$('[data-stop]', el);
    this.stops = this.tabs.map(function (b) { return parseFloat(b.getAttribute('data-stop')) || 0; });
    this.note = $('[data-bay-note]', el);
    this.live = $('[data-bay-live]', el);
    this.play = $('[data-bay-play]', el);
    this.phaseEl = $('[data-bay-phase]', el);
    this.stateEl = $('[data-bay-state]', el);
    this.progs = this.tabs.map(function (b) { return $('[data-prog]', b); });
    this.idx = -1;
    this.held = false;
    this.stage = null;
    this.railW = 0;
    this.tabs.forEach(function (b, i) { b.addEventListener('click', function () { self.select(i, true); }); });
    this.hover = false;
    /* a story waits while the pointer is over it, so a dense window can be read */
    if (FINE && !REDUCED) {
      el.addEventListener('pointerenter', function () { self.hover = true; if (self.stage) self.stage.paused = true; self.state(); });
      el.addEventListener('pointerleave', function () {
        self.hover = false;
        if (self.stage) { self.stage.paused = false; wakeClocks(); }
        self.state();
      });
    }
    if (REDUCED) {
      el.classList.add('is-static');
      if (this.stateEl) this.stateEl.textContent = 'Still';
    }
  }
  Bay.prototype.mount = function () {
    if (this.stage || !this.story) return;
    var self = this, rest = +this.story.getAttribute('data-step') || 0;
    /* start at the top of the phase the page was written at: nothing jumps on
       arrival, and that phase holds for a full step before the story moves on */
    var n = Math.max(1, this.stops.length);
    this.stage = new Clock(n * STEP_MS, (rest + .02) / n, function (c) { self.sync(c); });
    this.stage.paused = this.hover;
    if (this.held && this.idx >= 0) this.stage.hold(this.stops[this.idx]); else this.sync(this.stage.cyc);
    if (HAS_IO) {
      new IntersectionObserver(function (en) {
        self.stage.seen = en[0].isIntersecting;
        if (self.stage.seen) wakeClocks();
      }, { threshold: .1 }).observe(this.el);
    } else {
      this.stage.seen = true;
      wakeClocks();
    }
  };
  Bay.prototype.nearest = function (c) {
    var best = 0, bd = 2;
    for (var i = 0; i < this.stops.length; i++) {
      var d = Math.abs(c - this.stops[i]);
      d = Math.min(d, 1 - d);
      if (d < bd) { bd = d; best = i; }
    }
    return best;
  };
  /* how far through phase i the narrative is: phases meet halfway between stops */
  Bay.prototype.frac = function (c, i) {
    var s = this.stops, n = s.length;
    if (n < 2) return 0;
    var prev = i === 0 ? s[n - 1] - 1 : s[i - 1], next = i === n - 1 ? s[0] + 1 : s[i + 1];
    var a = (prev + s[i]) / 2, b = (s[i] + next) / 2, x = c;
    if (x < a) x += 1;
    if (x > b && x - 1 >= a) x -= 1;
    return Math.max(0, Math.min(1, (x - a) / (b - a)));
  };
  Bay.prototype.sync = function (c) {
    var i = this.held ? this.idx : this.nearest(c);
    if (i !== this.idx) this.show(i);
    if (this.play) {
      if (!this.railW) this.railW = this.play.parentNode.getBoundingClientRect().width;
      this.play.style.transform = 'translateX(' + (c * this.railW).toFixed(1) + 'px)';
    }
    var p = this.progs[this.idx];
    if (p) p.style.transform = 'scaleX(' + (this.held ? 1 : this.frac(c, this.idx)).toFixed(3) + ')';
  };
  Bay.prototype.tabLabel = function (b) {
    var l = $('.step__l, .ptab__l', b);
    return (l ? l.textContent : b.textContent).trim();
  };
  Bay.prototype.show = function (i) {
    var self = this, b = this.tabs[i];
    this.idx = i;
    setStep(this.story, i);
    this.tabs.forEach(function (t, j) {
      t.setAttribute('aria-pressed', j === i ? 'true' : 'false');
      if (j !== i && self.progs[j]) self.progs[j].style.transform = 'scaleX(0)';
    });
    if (!b) return;
    if (this.note) this.note.textContent = b.getAttribute('data-caption') || '';
    if (this.phaseEl) this.phaseEl.textContent = pad(i + 1) + ' / ' + pad(this.tabs.length);
  };
  Bay.prototype.select = function (i, user) {
    if (i < 0 || i >= this.tabs.length) return;
    if (user && this.held && this.idx === i) { this.release(); return; }
    this.held = true;
    this.el.classList.add('is-held');
    if (this.stateEl) this.stateEl.textContent = 'Held';
    if (this.story) this.story.classList.remove('is-paused');
    this.show(i);
    if (this.stage) this.stage.hold(this.stops[i]); else this.mount();
    if (this.progs[i]) this.progs[i].style.transform = 'scaleX(1)';
    if (user && this.live) this.live.textContent = this.tabLabel(this.tabs[i]) + '. ' + (this.tabs[i].getAttribute('data-caption') || '');
  };
  Bay.prototype.state = function () {
    if (this.stateEl && !REDUCED) this.stateEl.textContent = this.held ? 'Held' : (this.hover ? 'Paused' : 'Auto');
    if (this.story) this.story.classList.toggle('is-paused', this.hover && !this.held && !REDUCED);
  };
  Bay.prototype.release = function () {
    this.held = false;
    this.el.classList.remove('is-held');
    if (REDUCED) { if (this.stateEl) this.stateEl.textContent = 'Still'; } else this.state();
    if (this.stage) this.stage.hold(null);
    if (this.live) this.live.textContent = 'Playing every phase';
  };

  $$('[data-bay]').forEach(function (el) { var b = new Bay(el); el.__bay = b; bays.push(b); });
  if (bays.length) {
    if (HAS_IO) {
      var bayIO = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting && en.target.__bay) { en.target.__bay.mount(); bayIO.unobserve(en.target); }
        });
      }, { rootMargin: '600px 0px' });
      bays.forEach(function (b) { bayIO.observe(b.el); });
    } else {
      bays.forEach(function (b) { b.mount(); });
    }
    addEventListener('resize', function () { bays.forEach(function (b) { b.railW = 0; }); });
  }
  function bayInView() {
    var best = null, most = 0, vh = window.innerHeight;
    bays.forEach(function (b) {
      var r = b.el.getBoundingClientRect(), vis = Math.min(r.bottom, vh) - Math.max(r.top, 0);
      if (r.height && vis > 0 && vis / Math.min(r.height, vh) > .5 && vis > most) { most = vis; best = b; }
    });
    return best;
  }

  /* ---- the showcase under the home hero ------------------------------------- */
  (function showcase() {
    var box = $('[data-show]');
    if (!box) return;
    var tabs = $$('[data-show-tab]', box), seg = $('[data-seg]', box);
    var cur = 0, auto = !REDUCED, hovered = false, focused = false, inView = true, elapsed = 0, last = 0, DUR = 13000;
    function select(i, user) {
      cur = (i + tabs.length) % tabs.length;
      tabs.forEach(function (t, j) {
        var on = j === cur, p = doc.getElementById(t.getAttribute('aria-controls'));
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        t.style.setProperty('--p', '0');
        if (p) p.hidden = !on;
      });
      elapsed = 0;
      if (seg) placeSeg(seg);
      bays.forEach(function (b) { b.railW = 0; });
      if (user) { auto = false; box.classList.add('is-manual'); }
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(i, true); });
      t.addEventListener('keydown', function (e) {
        var k = e.key, n = k === 'ArrowRight' ? cur + 1 : k === 'ArrowLeft' ? cur - 1 : k === 'Home' ? 0 : k === 'End' ? tabs.length - 1 : null;
        if (n == null) return;
        e.preventDefault();
        e.stopPropagation();
        select(n, true);
        tabs[cur].focus();
      });
    });
    /* the clock only asks for frames while it is advancing, so a showcase that is hovered, scrolled away or in a hidden tab lets the page go idle */
    var raf = 0;
    function running() { return auto && !hovered && !focused && inView && !doc.hidden; }
    function tick(now) {
      raf = 0;
      if (!running()) { last = 0; return; }
      var dt = last ? Math.min(100, now - last) : 0;
      last = now;
      elapsed += dt;
      var t = tabs[cur];
      if (elapsed >= DUR) select(cur + 1, false);
      else if (t) t.style.setProperty('--p', (elapsed / DUR).toFixed(4));
      raf = requestAnimationFrame(tick);
    }
    function wake() { if (!raf && running()) raf = requestAnimationFrame(tick); }
    box.addEventListener('pointerenter', function () { hovered = true; });
    box.addEventListener('pointerleave', function () { hovered = false; wake(); });
    box.addEventListener('focusin', function () { focused = true; });
    box.addEventListener('focusout', function (e) { if (!e.relatedTarget || !box.contains(e.relatedTarget)) { focused = false; wake(); } });
    if (HAS_IO) new IntersectionObserver(function (en) { inView = en[0].isIntersecting; wake(); }, { threshold: .35 }).observe(box);
    doc.addEventListener('visibilitychange', wake);
    if (!auto) { box.classList.add('is-manual'); return; }
    wake();
  })();

  /* ---- case pages: the section bar steps aside once the case is over ---- */
  (function beatbarPast() {
    var bar = $('.beatbar'), end = $('.closeout');
    if (!bar || !end || !HAS_IO) return;
    new IntersectionObserver(function (en) {
      bar.classList.toggle('is-past', en[0].isIntersecting || en[0].boundingClientRect.top < 0);
    }).observe(end);
  })();

  /* ---- primary actions: the rim of light travels only while the button is on screen ---- */
  (function rims() {
    var btns = $$('.btn--primary');
    if (!btns.length || !HAS_IO || REDUCED) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { en.target.classList.toggle('is-away', !en.isIntersecting); });
    });
    btns.forEach(function (b) { io.observe(b); });
  })();

  /* ---- header: one highlight glides between the links under the pointer ---- */
  (function navHighlight() {
    var nav = $('.hdr__nav'), hl = nav && $('.nav__hl', nav);
    if (!nav || !hl || !FINE) return;
    nav.classList.add('has-hl');
    /* a still, invisible marker shares the highlight's containing block, so every
       placement is measured from a fixed origin, even while the highlight glides */
    var probe = doc.createElement('span');
    probe.setAttribute('aria-hidden', 'true');
    probe.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;visibility:hidden;pointer-events:none';
    nav.appendChild(probe);
    var on = false, last = null;
    function place(el) {
      var o = probe.getBoundingClientRect(), r = el.getBoundingClientRect();
      last = el;
      if (!on) hl.style.transition = 'opacity .3s';
      hl.style.width = r.width + 'px';
      hl.style.height = r.height + 'px';
      hl.style.transform = 'translate(' + (r.left - o.left).toFixed(1) + 'px, ' + (r.top - o.top).toFixed(1) + 'px)';
      if (!on) { void hl.offsetWidth; hl.style.transition = ''; on = true; }
      nav.classList.add('is-hl');
    }
    $$('.nav__item, .hdr__nav > .nav__link', nav).forEach(function (el) {
      el.addEventListener('pointerenter', function () { place(el); });
    });
    nav.addEventListener('pointerleave', function () { nav.classList.remove('is-hl'); on = false; });
    /* the bar changes shape when it floats; follow it if the pointer is still here */
    var bar = nav.closest('.hdr__bar');
    if (bar) bar.addEventListener('transitionend', function (e) { if (e.target === bar && e.propertyName === 'max-width' && on && last) place(last); });
  })();

  /* ---- before and after: the rows turn over once you are looking ------------ */
  (function beforeAfter() {
    var box = $('[data-ba]');
    if (!box) return;
    var btns = $$('[data-ba-set]', box), seg = $('[data-seg]', box), touched = false;
    function set(state, user) {
      box.setAttribute('data-state', state);
      btns.forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-ba-set') === state ? 'true' : 'false'); });
      $$('[data-ba-before]', box).forEach(function (el) { el.setAttribute('aria-hidden', state === 'before' ? 'false' : 'true'); });
      $$('[data-ba-after]', box).forEach(function (el) { el.setAttribute('aria-hidden', state === 'after' ? 'false' : 'true'); });
      if (seg) placeSeg(seg);
      if (user) touched = true;
    }
    btns.forEach(function (b) { b.addEventListener('click', function () { set(b.getAttribute('data-ba-set'), true); }); });
    if (REDUCED || !HAS_IO) return;
    var r0 = box.getBoundingClientRect();
    /* already on screen at load: leave it showing the result */
    if (r0.top < window.innerHeight && r0.bottom > 0) return;
    box.classList.add('is-instant');
    set('before', false);
    requestAnimationFrame(function () { requestAnimationFrame(function () { box.classList.remove('is-instant'); }); });
    var io = new IntersectionObserver(function (en) {
      if (!en[0].isIntersecting) return;
      io.disconnect();
      setTimeout(function () { if (!touched) set('after', false); }, 1500);
    }, { threshold: .35 });
    io.observe(box);
  })();

  /* ---- a soft light follows the pointer across the dark panels -------------- */
  (function spotlight() {
    if (!FINE || REDUCED) return;
    $$('[data-spot]').forEach(function (el) {
      var raf = 0, px = 0, py = 0;
      el.addEventListener('pointermove', function (e) {
        var b = el.getBoundingClientRect();
        px = e.clientX - b.left;
        py = e.clientY - b.top;
        if (raf) return;
        raf = requestAnimationFrame(function () {
          raf = 0;
          el.style.setProperty('--sx', px.toFixed(0) + 'px');
          el.style.setProperty('--sy', py.toFixed(0) + 'px');
          el.classList.add('is-spot');
        });
      });
      el.addEventListener('pointerleave', function () { el.classList.remove('is-spot'); });
    });
  })();

  /* ---- the footer's bands unfold when it arrives ---------------------------- */
  (function strata() {
    var bands = $('.stripes--ftr');
    if (!bands || REDUCED || !HAS_IO) return;
    /* already on screen when the page opens: leave it as it is */
    if (bands.getBoundingClientRect().top < (window.innerHeight || 800)) return;
    bands.classList.add('is-folded');
    var io = new IntersectionObserver(function (en) {
      if (!en[0].isIntersecting) return;
      io.disconnect();
      bands.classList.remove('is-folded');
    }, { rootMargin: '0px 0px -8% 0px' });
    io.observe(bands);
  })();

  /* ---- page heads: the dot grid lights up around the pointer ---------------- */
  (function gridLight() {
    if (!FINE || REDUCED) return;
    var R = 220, CELL = 24;
    $$('.hero, .phead, .casehead').forEach(function (el) {
      var box = doc.createElement('span'), lamp = doc.createElement('i'), raf = 0, cx = 0, cy = 0;
      box.className = 'gridlight';
      box.setAttribute('aria-hidden', 'true');
      box.appendChild(lamp);
      el.appendChild(box);
      el.addEventListener('pointermove', function (e) {
        cx = e.clientX;
        cy = e.clientY;
        if (raf) return;
        raf = requestAnimationFrame(function () {
          raf = 0;
          var b = el.getBoundingClientRect();
          /* the page's dots start at the top left of the document, 24px apart */
          var left = cx + window.scrollX - R, top = cy + window.scrollY - R;
          lamp.style.setProperty('--gl-x', (cx - b.left).toFixed(1) + 'px');
          lamp.style.setProperty('--gl-y', (cy - b.top).toFixed(1) + 'px');
          lamp.style.setProperty('--gl-bx', (-(left % CELL)).toFixed(2) + 'px');
          lamp.style.setProperty('--gl-by', (-(top % CELL)).toFixed(2) + 'px');
          el.classList.add('is-gridlit');
        });
      });
      el.addEventListener('pointerleave', function () { el.classList.remove('is-gridlit'); });
    });
  })();

  /* ---- the footer's big word catches the light ------------------------------ */
  (function wordLight() {
    if (!FINE || REDUCED) return;
    $$('.ftr__word').forEach(function (word) {
      var card = word.closest('.ftr__card') || word.parentNode, raf = 0, cx = 0, cy = 0;
      card.addEventListener('pointermove', function (e) {
        cx = e.clientX;
        cy = e.clientY;
        if (raf) return;
        raf = requestAnimationFrame(function () {
          raf = 0;
          var b = word.getBoundingClientRect();
          word.style.setProperty('--wx', (cx - b.left).toFixed(0) + 'px');
          word.style.setProperty('--wy', (cy - b.top).toFixed(0) + 'px');
          word.classList.toggle('is-lit', cy > b.top - 240 && cy < b.bottom + 60);
        });
      });
      card.addEventListener('pointerleave', function () { word.classList.remove('is-lit'); });
    });
  })();

  /* ---- thumbnails: stories on cards play in view on the bays' shared clock --- */
  function thumbClock(st) {
    if (st.__clock) return st.__clock;
    var n = +st.getAttribute('data-steps') || 1, ms = +st.getAttribute('data-ms') || STEP_MS;
    var rest = +st.getAttribute('data-rest') || 0, segs = [], last = -1;
    /* a quiet progress line: one segment per phase, the current one filling */
    if (n > 1) {
      var bar = doc.createElement('span');
      bar.className = 's-prog';
      bar.setAttribute('aria-hidden', 'true');
      for (var i = 0; i < n; i++) {
        var seg = doc.createElement('i');
        seg.appendChild(doc.createElement('b'));
        bar.appendChild(seg);
        segs.push(seg.firstChild);
      }
      st.appendChild(bar);
    }
    var row = st.closest('.wrow, .labcard'), names = row ? $$('[data-phase]', row) : [];
    st.__clock = new Clock(n * ms, (rest + .02) / n, function (cyc) {
      var x = cyc * n, k = Math.floor(x) % n, f = x - Math.floor(x);
      setStep(st, k);
      segs.forEach(function (b, j) { b.style.transform = 'scaleX(' + (j < k ? 1 : j === k ? f : 0).toFixed(3) + ')'; });
      if (k !== last) {
        last = k;
        names.forEach(function (el, j) { el.classList.toggle('is-cur', j === k); });
      }
    });
    return st.__clock;
  }
  function thumbWake(host, on) {
    var st = host && $('[data-story][data-thumb]', host);
    if (!st || REDUCED || st.hasAttribute('data-autoplay')) return;
    var c = thumbClock(st), n = +st.getAttribute('data-steps') || 1;
    c.seen = on;
    if (on) { c.hold(null); wakeClocks(); } else c.hold(((+st.getAttribute('data-rest') || 0) + .02) / n);
  }
  (function thumbs() {
    $$('[data-story][data-thumb]').forEach(function (st) {
      st.setAttribute('data-rest', st.getAttribute('data-step'));
      if (REDUCED) return;
      if (st.hasAttribute('data-autoplay')) {
        /* plays while in view; waits, and says so, while the pointer rests on it */
        var c = thumbClock(st);
        if (HAS_IO) new IntersectionObserver(function (en) { c.seen = en[0].isIntersecting; if (c.seen) wakeClocks(); }, { threshold: .25 }).observe(st);
        else { c.seen = true; wakeClocks(); }
        if (FINE) {
          st.addEventListener('pointerenter', function () { c.paused = true; st.classList.add('is-paused'); });
          st.addEventListener('pointerleave', function () { c.paused = false; st.classList.remove('is-paused'); wakeClocks(); });
        }
        return;
      }
      var host = st.closest('[data-wake]');
      if (!host || !FINE) return;
      host.addEventListener('mouseenter', function () { thumbWake(host, true); });
      host.addEventListener('mouseleave', function () { if (!host.classList.contains('is-locus')) thumbWake(host, false); });
    });
  })();

  /* ---- stories arrive once, rest when away, and lean toward the pointer ------ */
  (function storyLife() {
    var list = $$('[data-story]');
    if (!list.length || REDUCED || !HAS_IO) return;
    var vh = window.innerHeight || 800;
    list.forEach(function (st) {
      var r = st.getBoundingClientRect();
      if (!(r.width && r.top < vh && r.bottom > 0)) st.classList.add('is-wait');
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var st = en.target;
        st.classList.toggle('is-away', !en.isIntersecting);
        if (en.isIntersecting && st.classList.contains('is-wait')) {
          st.classList.remove('is-wait');
          st.classList.add('is-boot');
          setTimeout(function () { st.classList.remove('is-boot'); }, 1500);
        }
      });
    }, { threshold: .15 });
    list.forEach(function (st) { io.observe(st); });
    addEventListener('beforeprint', function () { list.forEach(function (st) { st.classList.remove('is-wait'); }); });
    if (!FINE) return;
    list.forEach(function (st) {
      var raf = 0, px = 0, py = 0;
      st.addEventListener('pointermove', function (e) {
        var b = st.getBoundingClientRect();
        px = (e.clientX - b.left) / b.width - .5;
        py = (e.clientY - b.top) / b.height - .5;
        if (raf) return;
        raf = requestAnimationFrame(function () {
          raf = 0;
          st.style.setProperty('--px', px.toFixed(3));
          st.style.setProperty('--py', py.toFixed(3));
          st.classList.add('is-tilt');
        });
      });
      st.addEventListener('pointerleave', function () { st.classList.remove('is-tilt'); });
    });
  })();

  /* ---- locus: where you are, and j / k ------------------------------------ */
  function locusList() {
    return $$(page === 'simple' ? '[data-sec]' : '[data-locus]').filter(function (el) {
      return !el.classList.contains('is-out') && el.getClientRects().length > 0;
    });
  }
  function describeLocus() {
    var el = locus.current, lab = labelOf(el), pageLab = body.getAttribute('data-label') || '';
    $$('[data-locus-label]').forEach(function (n) {
      n.textContent = lab && lab !== pageLab && lab !== 'Top' ? pageLab + ' · ' + lab : pageLab;
    });
    var wl = $('[data-work-locus]');
    if (wl && el && el.classList.contains('wrow')) {
      var rows = locusList().filter(function (r) { return r.classList.contains('wrow'); });
      wl.textContent = pad(rows.indexOf(el) + 1) + '/' + pad(rows.length) + ' · ' + lab;
    }
    var sl = $('[data-simple-locus]');
    if (sl && el) {
      var all = locusList();
      sl.textContent = pad(all.indexOf(el) + 1) + ' / ' + pad(all.length) + ' · ' + lab;
    }
  }
  function setLocus(el, byKey) {
    var prev = locus.current;
    if (prev && prev !== el) {
      prev.classList.remove('is-locus');
      if (prev.hasAttribute('data-wake')) thumbWake(prev, false);
    }
    locus.current = el;
    if (el && byKey) {
      el.classList.add('is-locus');
      if (el.hasAttribute('data-wake')) thumbWake(el, true);
    }
    if (prev !== el) describeLocus();
  }
  function clearLocus() {
    $$('.is-locus').forEach(function (el) {
      el.classList.remove('is-locus');
      if (el.hasAttribute('data-wake')) thumbWake(el, false);
    });
  }
  function spyLocus() {
    if (Date.now() < locus.until) return;
    var list = locusList();
    if (!list.length) return;
    var line = headerOffset() + 40, pick = null, pickTop = -Infinity;
    list.forEach(function (el) {
      var t = el.getBoundingClientRect().top;
      if (t - line <= 0 && t > pickTop) { pickTop = t; pick = el; }
    });
    if (window.innerHeight + (window.scrollY || 0) >= root.scrollHeight - 2) pick = list[list.length - 1];
    pick = pick || list[0];
    if (pick !== locus.current) setLocus(pick, false);
  }
  spies.push(spyLocus);

  function goTo(el, byKey) {
    if (!el) return;
    if (el.hasAttribute('data-locus') || el.hasAttribute('data-sec')) setLocus(el, byKey);
    locus.until = Date.now() + (REDUCED ? 80 : 900);
    var y = el.getBoundingClientRect().top + (window.scrollY || 0) - headerOffset();
    if (el.id === 'top' || el.id === 'dhead') y = 0;
    window.scrollTo({ top: Math.max(0, y), behavior: REDUCED ? 'auto' : 'smooth' });
    if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '-1');
    try { el.focus({ preventScroll: true }); } catch (e) { /* older engines */ }
  }
  function step(d) {
    var list = locusList();
    if (!list.length) return;
    list.sort(function (a, b) { return a.getBoundingClientRect().top - b.getBoundingClientRect().top; });
    var i = list.indexOf(locus.current);
    var n = i < 0 ? (d > 0 ? 0 : list.length - 1) : Math.max(0, Math.min(list.length - 1, i + d));
    if (i >= 0 && n === i) {
      list[n].classList.add('is-locus');
      return;
    }
    goTo(list[n], true);
  }
  function openLocus() {
    var el = locus.current;
    if (!el) return false;
    var href = el.getAttribute('data-href');
    if (!href) { var a = $('a[href]', el); href = a && a.getAttribute('href'); }
    if (!href) return false;
    if (href.charAt(0) === '#') { var t = doc.getElementById(href.slice(1)); if (t) goTo(t, true); return !!t; }
    location.href = href;
    return true;
  }
  function toTop() {
    locus.until = Date.now() + 900;
    window.scrollTo({ top: 0, behavior: REDUCED ? 'auto' : 'smooth' });
    clearLocus();
    var list = locusList();
    setLocus(list[0] || null, false);
  }

  /* in-page anchors scroll with the header accounted for, and move focus */
  doc.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a) return;
    var id = decodeURIComponent(a.getAttribute('href').slice(1)), t = id ? doc.getElementById(id) : null;
    if (!t) return;
    e.preventDefault();
    if (a.classList.contains('skip')) { t.focus(); return; }
    goTo(t, true);
    if (history.replaceState) history.replaceState(null, '', '#' + id);
  });

  /* ---- work: facets ----------------------------------------------------------- */
  facetBtns = $$('button[data-facet]');
  function applyFacet(key, fromUser) {
    if (!facetBtns.length) return;
    var known = facetBtns.some(function (b) { return b.getAttribute('data-facet') === key; });
    if (!known) key = 'all';
    var count = 0, label = 'All';
    facetBtns.forEach(function (b) {
      var on = b.getAttribute('data-facet') === key, l = $('.facet__l', b);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (on) label = l ? l.textContent : b.textContent;
    });
    $$('.wrow[data-facet]').forEach(function (r) {
      var show = key === 'all' || r.getAttribute('data-facet') === key;
      r.classList.toggle('is-out', !show);
      if (show) count++;
    });
    var seg = facetBtns[0].closest('[data-seg]');
    if (seg) placeSeg(seg);
    var live = $('[data-facet-live]');
    if (live && fromUser) live.textContent = label + ': ' + count + ' systems';
    if (fromUser && history.replaceState) {
      history.replaceState(null, '', location.pathname + (key === 'all' ? '' : '?f=' + key) + location.hash);
    }
    if (locus.current && locus.current.classList.contains('is-out')) setLocus(null, false);
    var rows = locusList().filter(function (r) { return r.classList.contains('wrow'); });
    var wl = $('[data-work-locus]');
    if (wl && rows.length) wl.textContent = '01/' + pad(rows.length) + ' · ' + labelOf(rows[0]);
  }
  if (facetBtns.length) {
    facetBtns.forEach(function (b) {
      b.addEventListener('click', function () { applyFacet(b.getAttribute('data-facet'), true); });
    });
    var initialFacet = 'all';
    try { initialFacet = new URLSearchParams(location.search).get('f') || 'all'; } catch (e) { /* no URLSearchParams */ }
    applyFacet(initialFacet, false);
  }

  /* ---- case: beats, progress, brief, embeds --------------------------------- */
  function copyBeat() {
    var b = $('[data-beat].is-on');
    copyLink(b || locus.current);
  }
  if (page === 'case') {
    var beats = $$('[data-beat]'), segsB = $$('[data-beatprog] i'), beatLinks = $$('[data-beat-link]');
    var beatNames = $$('[data-beat-name]'), beatIdx = $('[data-beat-idx]'), barNav = $('.beatbar__nav');
    var activeBeat = null;
    spies.push(function beatSpy() {
      if (!beats.length) return;
      var line = headerOffset() + 48, pick = beats[0];
      for (var i = 0; i < beats.length; i++) {
        if (beats[i].getBoundingClientRect().top - line <= 0) pick = beats[i];
      }
      if (window.innerHeight + (window.scrollY || 0) >= root.scrollHeight - 2) pick = beats[beats.length - 1];
      if (pick === activeBeat) return;
      activeBeat = pick;
      var k = beats.indexOf(pick);
      beats.forEach(function (b, j) { b.classList.toggle('is-on', j === k); });
      segsB.forEach(function (s, j) { s.classList.toggle('is-on', j === k); s.classList.toggle('is-done', j < k); });
      beatLinks.forEach(function (a) {
        if (a.getAttribute('data-beat-link') === pick.id) a.setAttribute('aria-current', 'true');
        else a.removeAttribute('aria-current');
      });
      beatNames.forEach(function (n) { n.textContent = labelOf(pick); });
      if (beatIdx) beatIdx.textContent = pad(k + 1) + '/' + pad(beats.length);
      if (barNav && barNav.scrollWidth > barNav.clientWidth) {
        var cur = $('[data-beat-link="' + pick.id + '"]', barNav);
        if (cur) {
          var delta = cur.getBoundingClientRect().left - barNav.getBoundingClientRect().left;
          barNav.scrollTo({ left: Math.max(0, barNav.scrollLeft + delta - 24), behavior: REDUCED ? 'auto' : 'smooth' });
        }
      }
    });
    $$('[data-jump]').forEach(function (b) {
      b.addEventListener('click', function () { var t = doc.getElementById(b.getAttribute('data-jump')); if (t) goTo(t, true); });
    });
    $$('[data-embed]').forEach(function (fig) {
      var f = $('iframe', fig);
      if (f) f.addEventListener('load', function () { fig.classList.add('is-loaded'); });
    });
  }

  /* ---- approach: the autonomy ladder ---------------------------------------- */
  rungs = $$('.rung');
  function setRung(i, focus) {
    if (!rungs.length) return;
    i = Math.max(0, Math.min(rungs.length - 1, i));
    ladderIdx = i;
    rungs.forEach(function (r, j) {
      r.setAttribute('aria-pressed', j === i ? 'true' : 'false');
      r.classList.toggle('is-below', j < i);
    });
    var r = rungs[i], name = $('b', r), desc = $('.rung__d', r);
    var locusEl = $('[data-ladder-locus]'), read = $('[data-ladder-read]');
    if (locusEl) locusEl.textContent = pad(i + 1) + ' / ' + pad(rungs.length) + ' · ' + (name ? name.textContent : '');
    if (read) {
      read.textContent = '';
      var b = doc.createElement('b');
      b.textContent = name ? name.textContent : '';
      read.appendChild(b);
      read.appendChild(doc.createTextNode(' ' + (desc ? desc.textContent : '')));
    }
    if (focus) r.focus();
  }
  if (rungs.length) {
    var startRung = 0;
    rungs.forEach(function (r, i) {
      if (r.getAttribute('aria-pressed') === 'true') startRung = i;
      r.addEventListener('click', function () { setRung(i, false); });
    });
    setRung(startRung, false);
  }
  function ladderKey(d) {
    if (page !== 'approach' || !rungs.length) return false;
    var L = $('#ladder');
    if (!L) return false;
    var r = L.getBoundingClientRect(), vis = Math.min(r.bottom, window.innerHeight) - Math.max(r.top, 0);
    if (vis < Math.min(r.height, window.innerHeight) * .5) return false;
    var n = ladderIdx + d;
    if (n < 0 || n >= rungs.length) return false;
    setRung(n, true);
    return true;
  }

  /* ---- simple page ------------------------------------------------------------- */
  if (page === 'simple') {
    var emailBox = $('[data-demail]'), emailBtn = $('[data-email-toggle]');
    emailOpen = function () { return !!(emailBox && !emailBox.hidden); };
    toggleEmail = function (force) {
      if (!emailBox || !emailBtn) return;
      var open = typeof force === 'boolean' ? force : emailBox.hidden;
      emailBox.hidden = !open;
      emailBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) copyEmail();
    };
  }

  /* ---- first-visit key hint ------------------------------------------------------ */
  var GRAMMAR = {
    home: ['j / k', 'sections & systems', 'Enter', 'opens', MOD, 'jump'],
    labs: ['j / k', 'builds', '1-4', 'phases', MOD, 'jump'],
    work: ['1-4', 'facets', 'j / k', 'ledger', MOD, 'jump'],
    'case': ['j / k', 'beats', '← →', 'systems', 'b', 'brief'],
    approach: ['1-5', 'layers', 'j / k', 'ladder', MOD, 'jump'],
    about: ['j / k', 'experience', MOD, 'jump'],
    writing: ['j / k', 'theses', MOD, 'jump']
  };
  (function hintChip() {
    var chip = $('[data-gchip]'), txt = $('[data-gchip-text]'), g = GRAMMAR[page];
    if (!chip || !txt || !g || !FINE) return;
    if (store.get('jj:keys-learned', false) || store.get('jj:gchip', false)) return;
    for (var i = 0; i < g.length; i += 2) {
      if (i) txt.appendChild(doc.createTextNode(' · '));
      var b = doc.createElement('b');
      b.textContent = g[i];
      txt.appendChild(b);
      txt.appendChild(doc.createTextNode(' ' + g[i + 1]));
    }
    chipEl = chip;
    setTimeout(function () { if (chipEl) chipEl.hidden = false; }, 3200);
    /* shown once per visitor: it steps aside on its own and does not come back */
    setTimeout(function () { if (chipEl) { chipEl.hidden = true; store.set('jj:gchip', true); chipEl = null; } }, 15000);
  })();
  function dismissChip(learned) {
    if (learned) { store.set('jj:keys-learned', true); root.classList.add('keys-on'); }
    if (!chipEl) return;
    chipEl.hidden = true;
    store.set('jj:gchip', true);
    chipEl = null;
  }

  /* ---- command palette ------------------------------------------------------------ */
  var pal = $('[data-cmdk-root]'), palInput = $('[data-cmdk-input]'), palList = $('[data-cmdk-list]');
  var palItems = [], palShown = [], palSel = 0, palReturn = null;

  function keyHelp() {
    var k = [
      ['Open this palette', MOD, null],
      ['Move through the page', 'j / k', function () { step(1); }],
      ['Open what is highlighted', 'Enter', openLocus],
      ['Copy a link to where you are', 'y', function () { copyLink(); }],
      ['Copy the email address', 'e', function () { copyEmail(); }],
      ['Back to top', 't · g g', toTop],
      ['Clear the highlight', 'Esc', clearLocus],
      [store.get('jj:keys-off', false) ? 'Turn single-key shortcuts back on' : 'Turn off single-key shortcuts', '', function () {
        var off = !store.get('jj:keys-off', false);
        store.set('jj:keys-off', off);
        toast(off ? 'Single-key shortcuts off. ' + MOD + ' still opens the palette.' : 'Single-key shortcuts on.');
      }]
    ];
    if (page === 'case') k.push(['Previous or next system', '← →', null], ['Copy the case brief', 'b', copyBrief], ['Diagram phase, or jump to a beat', '1-9', null]);
    if (page === 'work') k.push(['Filter: all, agents, markets, labs', '1-4', null]);
    if (page === 'home' || page === 'labs') k.push(['Phase of the diagram in view', JJ.builds ? '1-4' : '1-5', null]);
    if (page === 'approach') k.push(['Control layer', '1-5', null], ['Autonomy ladder, when in view', 'j / k', null]);
    if (page === 'simple') k.push(['Full site', 'f', function () { location.href = '/'; }], ['Show and copy the email', 'e', function () { toggleEmail(true); }]);
    return k;
  }
  function paletteItems() {
    var out = [], pageLab = body.getAttribute('data-label') || '';
    $$(page === 'simple' ? '[data-sec]' : '[data-locus]').forEach(function (el) {
      if (!el.id || el.classList.contains('wrow') || el.classList.contains('is-out')) return;
      var lab = labelOf(el);
      if (!lab) return;
      out.push({ group: page === 'case' ? 'On this case' : 'On this page', label: lab, hint: 'Jump',
                 words: 'section ' + pageLab, run: function () { goTo(el, true); } });
    });
    (JJ.builds || []).forEach(function (b) {
      out.push({ group: 'Builds', label: b.name, sub: b.n + ' · ' + b.tag + ' · ' + b.line, hint: b.n,
                 words: [b.slug, b.cat, b.tag, 'build product open live'].join(' '), href: b.route });
    });
    (JJ.builds || []).forEach(function (b) {
      if (b.case) out.push({ group: 'Case studies', label: b.name + ' case study', sub: 'On the portfolio', hint: '↗',
                             words: 'case study portfolio ' + b.slug, href: b.case, ext: true });
    });
    (JJ.systems || []).forEach(function (s) {
      out.push({ group: s.facet === 'independent' ? 'Labs' : 'Systems', label: s.name, sub: s.title + ' · ' + s.metric[0] + ' ' + s.metric[1],
                 hint: s.id.replace('JJ-SYS-', 'SYS '), words: [s.slug, s.short, s.kind, s.org, s.facet].join(' '),
                 href: '/work/' + s.slug });
    });
    (JJ.pages || []).forEach(function (p) {
      out.push({ group: 'Pages', label: p[0], hint: 'Page', words: p[1], href: p[1] });
    });
    (JJ.notes || []).forEach(function (n) {
      out.push({ group: 'Writing', label: n.title, sub: n.tag + ' · ' + n.dek, hint: 'Note', words: 'thesis note', href: n.href });
    });
    out.push({ group: 'Actions', label: 'Copy email address', sub: EMAIL, hint: 'e', words: 'contact mail', run: function () { copyEmail(); } });
    out.push({ group: 'Actions', label: 'Email John', sub: EMAIL, hint: 'Mail', words: 'contact hire message', href: 'mailto:' + EMAIL });
    out.push({ group: 'Actions', label: 'Copy link to this page', hint: 'y', words: 'share url permalink', run: function () { copyLink(); } });
    if ($('#brief')) out.push({ group: 'Actions', label: 'Copy case brief', hint: 'b', words: 'brief summary clipboard', run: copyBrief });
    if (LINKS.resume) out.push({ group: 'Actions', label: 'Résumé (PDF)', hint: '↗', words: 'resume cv pdf', href: LINKS.resume, ext: true });
    if (LINKS.portfolio) out.push({ group: 'Actions', label: 'Portfolio', sub: LINKS.portfolio.replace(/^https?:\/\//, '').replace(/\/$/, ''), hint: '↗', words: 'portfolio work case studies about john', href: LINKS.portfolio, ext: true });
    if (LINKS.linkedin) out.push({ group: 'Actions', label: 'LinkedIn', hint: '↗', words: 'profile', href: LINKS.linkedin, ext: true });
    if (LINKS.substack) out.push({ group: 'Actions', label: 'Substack', hint: '↗', words: 'writing follow newsletter', href: LINKS.substack, ext: true });
    if (LINKS.labs) out.push({ group: 'Live products', label: 'Labs site', sub: LINKS.labs.replace(/^https?:\/\//, '').replace(/\/$/, ''), hint: '↗', words: 'labs independent products bench', href: LINKS.labs, ext: true });
    (LINKS.products || []).forEach(function (p) {
      out.push({ group: 'Live products', label: p[0], sub: p[1].replace(/^https?:\/\//, '').replace(/\/$/, ''),
                 hint: '↗', words: 'live app product', href: p[1], ext: true });
    });
    keyHelp().forEach(function (k) {
      out.push({ group: 'Keys', label: k[0], hint: k[1], words: 'keys help shortcut keyboard', run: k[2] });
    });
    return out;
  }
  function palScore(it, q) {
    var lab = it.label.toLowerCase(), at = lab.indexOf(q);
    if (at === 0) return 0;
    if (at > 0) return 1 + at / 100;
    var hay = (lab + ' ' + (it.sub || '') + ' ' + (it.words || '') + ' ' + it.group).toLowerCase();
    at = hay.indexOf(q);
    if (at >= 0) return 3 + at / 1000;
    /* loose matching forgives typos in names, so it reads the label alone and
       gives up once the letters are too scattered to mean anything */
    if (it.group === 'Keys' || q.length < 3) return -1;
    var pos = 0, gaps = 0;
    for (var i = 0; i < q.length; i++) {
      if (q.charAt(i) === ' ') continue;
      var j = lab.indexOf(q.charAt(i), pos);
      if (j < 0) return -1;
      gaps += j - pos;
      pos = j + 1;
    }
    return gaps > q.length * 2 ? -1 : 6 + gaps / 50;
  }
  function palMark() {
    $$('.cmdk__item', palList).forEach(function (li, i) { li.setAttribute('aria-selected', i === palSel ? 'true' : 'false'); });
    var cur = doc.getElementById('cmdk-opt-' + palSel);
    if (cur) {
      palInput.setAttribute('aria-activedescendant', cur.id);
      cur.scrollIntoView({ block: 'nearest' });
    }
  }
  function palDraw() {
    var q = palInput.value.trim().toLowerCase();
    var keysOnly = q === '?' || q === 'keys';
    var ranked = [];
    palItems.forEach(function (it, i) {
      if (keysOnly) { if (it.group === 'Keys') ranked.push({ it: it, s: i }); return; }
      if (!q) { if (it.group !== 'Keys') ranked.push({ it: it, s: i }); return; }
      var s = palScore(it, q);
      if (s >= 0) ranked.push({ it: it, s: s * 1000 + i });
    });
    ranked.sort(function (a, b) { return a.s - b.s; });
    palShown = ranked.slice(0, 60).map(function (r) { return r.it; });
    if (palSel >= palShown.length) palSel = 0;
    palList.textContent = '';
    if (!palShown.length) {
      var e = doc.createElement('li');
      e.className = 'cmdk__empty';
      e.setAttribute('role', 'presentation');
      e.textContent = JJ.builds ? 'No match. Try a build, a section, or ? for keys' : 'No match. Try a system, a page, or ? for keys';
      palList.appendChild(e);
      palInput.removeAttribute('aria-activedescendant');
      return;
    }
    var grouped = !q || keysOnly, last = '';
    palShown.forEach(function (it, i) {
      if (grouped && it.group !== last) {
        last = it.group;
        var g = doc.createElement('li');
        g.className = 'cmdk__group';
        g.setAttribute('role', 'presentation');
        g.textContent = it.group;
        palList.appendChild(g);
      }
      var li = doc.createElement('li'), main = doc.createElement('span'), lab = doc.createElement('span'), hint = doc.createElement('span');
      li.className = 'cmdk__item';
      li.id = 'cmdk-opt-' + i;
      li.setAttribute('role', 'option');
      lab.className = 'cmdk__label';
      lab.textContent = it.label;
      main.appendChild(lab);
      if (it.sub) {
        var sub = doc.createElement('span');
        sub.className = 'cmdk__sub';
        sub.textContent = it.sub;
        main.appendChild(sub);
      }
      hint.className = 'cmdk__hint';
      hint.textContent = grouped ? (it.hint || '') : (it.hint || it.group);
      li.appendChild(main);
      li.appendChild(hint);
      li.addEventListener('mousemove', function () { if (palSel !== i) { palSel = i; palMark(); } });
      li.addEventListener('click', function () { palRun(it); });
      palList.appendChild(li);
    });
    palMark();
  }
  function palRun(it) {
    if (it.group === 'Keys' && !it.run) { closePal(); return; }
    closePal(true);
    if (it.run) { setTimeout(it.run, 30); return; }
    if (!it.href) return;
    if (it.ext) window.open(it.href, '_blank', 'noopener');
    else location.href = it.href;
  }
  function openPal(q) {
    if (!pal || !palInput || !palList) return;
    palReturn = doc.activeElement;
    palItems = paletteItems();
    pal.hidden = false;
    body.classList.add('is-locked');
    palInput.value = q || '';
    palSel = 0;
    palDraw();
    requestAnimationFrame(function () { pal.classList.add('is-in'); palInput.focus(); });
    dismissChip(false);
  }
  function closePal(skipFocus) {
    if (!pal || pal.hidden) return;
    pal.classList.remove('is-in');
    body.classList.remove('is-locked');
    setTimeout(function () { if (!pal.classList.contains('is-in')) pal.hidden = true; }, REDUCED ? 0 : 180);
    if (!skipFocus && palReturn && palReturn.focus) palReturn.focus();
  }
  if (palInput) {
    palInput.addEventListener('input', function () { palSel = 0; palDraw(); });
    palInput.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); if (palShown.length) { palSel = (palSel + 1) % palShown.length; palMark(); } }
      else if (e.key === 'ArrowUp') { e.preventDefault(); if (palShown.length) { palSel = (palSel - 1 + palShown.length) % palShown.length; palMark(); } }
      else if (e.key === 'Enter') { e.preventDefault(); if (palShown[palSel]) palRun(palShown[palSel]); }
      else if (e.key === 'Escape') { e.preventDefault(); closePal(); }
      else if (e.key === 'Tab') { e.preventDefault(); }
    });
  }

  /* ---- clicks ------------------------------------------------------------------------ */
  doc.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[data-copy-email],[data-copy-link],[data-copy-brief],[data-copy-beat],[data-cmdk],[data-cmdk-close],[data-totop],[data-email-toggle],[data-gchip-close]') : null;
    if (!t) return;
    if (t.hasAttribute('data-copy-email')) { e.preventDefault(); copyEmail(t); }
    else if (t.hasAttribute('data-copy-link')) { copyLink(); }
    else if (t.hasAttribute('data-copy-brief')) { copyBrief(); }
    else if (t.hasAttribute('data-copy-beat')) { copyBeat(); }
    else if (t.hasAttribute('data-cmdk')) { e.preventDefault(); setDrawer(false); openPal(''); }
    else if (t.hasAttribute('data-cmdk-close')) { closePal(); }
    else if (t.hasAttribute('data-totop')) { toTop(); }
    else if (t.hasAttribute('data-email-toggle')) { toggleEmail(); }
    else if (t.hasAttribute('data-gchip-close')) { dismissChip(true); }
  });

  /* ---- keys ------------------------------------------------------------------------- */
  var gAt = 0;
  function digit(n) {
    var b = bayInView();
    if (b && n <= b.tabs.length) { b.select(n - 1, true); return true; }
    if (page === 'work' && n <= facetBtns.length) { applyFacet(facetBtns[n - 1].getAttribute('data-facet'), true); return true; }
    if (page === 'case') {
      var list = $$('[data-beat]');
      if (n <= list.length) { goTo(list[n - 1], true); return true; }
    }
    return false;
  }
  doc.addEventListener('keydown', function (e) {
    var k = e.key || '';
    if ((e.metaKey || e.ctrlKey) && !e.altKey && (k === 'k' || k === 'K')) {
      e.preventDefault();
      if (pal && !pal.hidden) closePal(); else openPal('');
      return;
    }
    if (pal && !pal.hidden) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var t = e.target || body;
    if (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName || '')) return;
    var onControl = /^(A|BUTTON|SUMMARY|IFRAME)$/.test(t.tagName || '');

    if (k === 'Escape') {
      if (closeMega()) return;
      if (drawer && !drawer.hidden) { setDrawer(false); if (menuBtn) menuBtn.focus(); return; }
      if (emailOpen()) { toggleEmail(false); return; }
      clearLocus();
      return;
    }
    if (k === 'Enter') { if (!onControl && openLocus()) e.preventDefault(); return; }
    /* single-character shortcuts can be switched off from the palette (WCAG 2.1.4) */
    if (k.length === 1 && store.get('jj:keys-off', false)) return;
    if (k === '/') { e.preventDefault(); openPal(''); return; }
    if (k === '?') { e.preventDefault(); openPal('?'); return; }
    if (page === 'case' && (k === '[' || k === ']' || ((k === 'ArrowLeft' || k === 'ArrowRight') && !onControl))) {
      var adj = $('[data-adj="' + (k === '[' || k === 'ArrowLeft' ? 'prev' : 'next') + '"]');
      if (adj) { e.preventDefault(); location.href = adj.getAttribute('href'); }
      return;
    }
    if (/^[1-9]$/.test(k)) {
      if (digit(parseInt(k, 10))) { e.preventDefault(); dismissChip(true); }
      return;
    }
    switch (k.toLowerCase()) {
      case 'j': e.preventDefault(); dismissChip(true); if (!ladderKey(1)) step(1); break;
      case 'k': e.preventDefault(); dismissChip(true); if (!ladderKey(-1)) step(-1); break;
      case 'y': e.preventDefault(); copyLink(); break;
      case 'e': e.preventDefault(); if (page === 'simple') toggleEmail(); else copyEmail(); break;
      case 't': e.preventDefault(); toTop(); break;
      case 'g': e.preventDefault(); if (Date.now() - gAt < 450) { gAt = 0; toTop(); } else gAt = Date.now(); break;
      case 'b': if (page === 'case') { e.preventDefault(); copyBrief(); } break;
      case 'f': if (page === 'simple') { e.preventDefault(); location.href = '/'; } break;
      default: break;
    }
  });

  /* ---- arriving on a hash ---------------------------------------------------------- */
  if (location.hash) {
    var hashTarget = null;
    try { hashTarget = doc.getElementById(decodeURIComponent(location.hash.slice(1))); } catch (e) { hashTarget = null; }
    if (hashTarget) {
      hashTarget.classList.add('is-target');
      if (hashTarget.hasAttribute('data-locus') || hashTarget.hasAttribute('data-sec')) setLocus(hashTarget, false);
    }
  }

  onScroll();
})();
