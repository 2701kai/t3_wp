/* t.o.d. pink — Glitta. The t2 animation ingredients without React:
   Spores (canvas drift), SplitText (neon flicker-on), Reveal (scroll
   fade + rise), TiltCard (pointer tilt + glare), Waveform (equalizer).
   Everything rests under prefers-reduced-motion: the html never gets
   .tod-js, so the CSS keeps all content visible and still. */
(function () {
  'use strict';

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  document.documentElement.classList.add('tod-js');

  var ready = function (fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  };

  /* ---------- SplitText: characters flicker on like neon tubes ---------- */

  function initSplit() {
    var els = document.querySelectorAll('.tod-split');
    if (!els.length) return;

    els.forEach(function (el) {
      if (el.dataset.todSplitDone) return;
      el.dataset.todSplitDone = '1';
      var text = el.textContent;
      el.setAttribute('aria-label', text);
      el.textContent = '';
      Array.from(text).forEach(function (ch, i) {
        var span = document.createElement('span');
        span.className = 'tod-char';
        span.setAttribute('aria-hidden', 'true');
        span.style.setProperty('--i', i);
        span.textContent = ch;
        el.appendChild(span);
      });
    });

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-on');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });

    els.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Reveal: fade + rise when scrolled into view ---------- */

  function initReveal() {
    var els = document.querySelectorAll('.tod-reveal');
    if (!els.length) return;

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    els.forEach(function (el) { io.observe(el); });
  }

  /* ---------- TiltCard: 3D tilt following the pointer, with glare ---------- */

  function initTilt() {
    var MAX_TILT = 9;

    document.querySelectorAll('.tod-tilt').forEach(function (el) {
      if (!el.querySelector('.tod-glare')) {
        var glare = document.createElement('span');
        glare.className = 'tod-glare';
        glare.setAttribute('aria-hidden', 'true');
        el.appendChild(glare);
      }

      el.addEventListener('pointermove', function (e) {
        var rect = el.getBoundingClientRect();
        var px = (e.clientX - rect.left) / rect.width;
        var py = (e.clientY - rect.top) / rect.height;
        el.style.setProperty('--rx', ((0.5 - py) * 2 * MAX_TILT).toFixed(2) + 'deg');
        el.style.setProperty('--ry', ((px - 0.5) * 2 * MAX_TILT).toFixed(2) + 'deg');
        el.style.setProperty('--gx', (px * 100).toFixed(1) + '%');
        el.style.setProperty('--gy', (py * 100).toFixed(1) + '%');
      });

      el.addEventListener('pointerleave', function () {
        el.style.setProperty('--rx', '0deg');
        el.style.setProperty('--ry', '0deg');
        el.style.setProperty('--gx', '50%');
        el.style.setProperty('--gy', '50%');
      });
    });
  }

  /* ---------- Waveform: the logo's equalizer, alive ---------- */

  function initWave() {
    var HEIGHTS = [10, 22, 34, 16, 27, 34, 12, 30, 18, 33, 14, 24];

    document.querySelectorAll('.tod-wave').forEach(function (el) {
      if (el.children.length) return;
      el.setAttribute('aria-hidden', 'true');
      HEIGHTS.forEach(function (h, i) {
        var bar = document.createElement('i');
        bar.style.setProperty('--h', h + 'px');
        bar.style.setProperty('--d', (1.1 + (i % 5) * 0.14) + 's');
        bar.style.setProperty('--dl', (i * 0.08) + 's');
        el.appendChild(bar);
      });
    });
  }

  /* ---------- Spores: ambient particles drifting up through the hero ----------
     Straight port of t2's Spores.jsx — canvas, sized to its host,
     paused when the tab is hidden. Default colors ARE the pink night. */

  function initSpores() {
    var COLORS = ['#ff3ecf', '#37f5e0', '#8a5cff', '#b8ff2e', '#f0e9ff'];

    document.querySelectorAll('.tod-atmo').forEach(function (host) {
      if (host.querySelector('canvas')) return;

      var canvas = document.createElement('canvas');
      canvas.setAttribute('aria-hidden', 'true');
      host.appendChild(canvas);

      var ctx = canvas.getContext('2d');
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      var W = 0, H = 0, spores = [], raf = 0, running = true;

      function makeSpore(fresh) {
        return {
          x: Math.random() * W,
          y: fresh ? H + 10 : Math.random() * H,
          r: 0.8 + Math.random() * 2.2,
          vy: 0.15 + Math.random() * 0.45,
          sway: Math.random() * Math.PI * 2,
          swaySpeed: 0.004 + Math.random() * 0.01,
          swayAmp: 0.3 + Math.random() * 0.7,
          color: COLORS[(Math.random() * COLORS.length) | 0],
          alpha: 0.25 + Math.random() * 0.55
        };
      }

      function resize() {
        W = host.clientWidth;
        H = host.clientHeight;
        canvas.width = W * dpr;
        canvas.height = H * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        var count = Math.min(90, Math.max(35, (W * H) / 22000));
        spores = [];
        for (var i = 0; i < count; i++) spores.push(makeSpore(false));
      }

      function frame() {
        if (!running) return;
        ctx.clearRect(0, 0, W, H);
        for (var i = 0; i < spores.length; i++) {
          var s = spores[i];
          s.y -= s.vy;
          s.sway += s.swaySpeed;
          s.x += Math.sin(s.sway) * s.swayAmp * 0.4;
          if (s.y < -12) spores[i] = s = makeSpore(true);

          ctx.globalAlpha = s.alpha;
          ctx.fillStyle = s.color;
          ctx.shadowColor = s.color;
          ctx.shadowBlur = 8;
          ctx.beginPath();
          ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;
        raf = requestAnimationFrame(frame);
      }

      function onVisibility() {
        var wasRunning = running;
        running = !document.hidden;
        if (running && !wasRunning) raf = requestAnimationFrame(frame);
      }

      resize();
      raf = requestAnimationFrame(frame);
      window.addEventListener('resize', resize);
      document.addEventListener('visibilitychange', onVisibility);
    });
  }

  ready(function () {
    initSplit();
    initReveal();
    initTilt();
    initWave();
    initSpores();
  });
})();
