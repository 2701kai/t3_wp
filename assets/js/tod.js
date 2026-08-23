/* t.o.d. pink - Glitta. The t2 animation ingredients without React:
   Spores (canvas drift), SplitText (neon flicker-on), Reveal (scroll
   fade + rise), TiltCard (pointer tilt + glare), Waveform (equalizer).
   Everything rests under prefers-reduced-motion: the html never gets
   .tod-js, so the CSS keeps all content visible and still.

   No build step: this file is enqueued as-is by functions.php and copied
   verbatim into the Divi child by scripts/build-divi-zip.sh. Hence the
   IIFE rather than a module - there is nothing to bundle it. */
(function () {
  'use strict';

  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  document.documentElement.classList.add('tod-js');

  const ready = fn => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  };

  /* ---------- SplitText: characters flicker on like neon tubes ---------- */

  const initSplit = () => {
    const els = document.querySelectorAll('.tod-split');
    if (!els.length) return;

    for (const el of els) {
      if (el.dataset.todSplitDone) continue;
      el.dataset.todSplitDone = '1';

      const text = el.textContent;
      el.setAttribute('aria-label', text);
      el.textContent = '';

      /* Words first, characters only inside them. Every char is an
         inline-block, and a line may break between any two inline boxes -
         so a flat list of characters lets "See you at sunrise" break as
         "See you a / t sunrise" on a narrow screen. Wrapping each word in
         a nowrap box puts the only legal break back between words. */
      let i = 0;
      for (const chunk of text.split(/(\s+)/)) {
        if (!chunk) continue;

        if (/^\s+$/.test(chunk)) {
          el.append(chunk);
          continue;
        }

        const word = document.createElement('span');
        word.className = 'tod-word';
        word.setAttribute('aria-hidden', 'true');

        for (const ch of chunk) {
          const span = document.createElement('span');
          span.className = 'tod-char';
          span.style.setProperty('--i', i++);
          span.textContent = ch;
          word.append(span);
        }

        el.append(word);
      }
    }

    const io = new IntersectionObserver(entries => {
      for (const { target, isIntersecting } of entries) {
        if (!isIntersecting) continue;
        target.classList.add('is-on');
        io.unobserve(target);
      }
    }, { threshold: 0.6 });

    for (const el of els) io.observe(el);
  };

  /* ---------- Reveal: fade + rise when scrolled into view ---------- */

  const initReveal = () => {
    const els = document.querySelectorAll('.tod-reveal');
    if (!els.length) return;

    /* threshold 0 with a bottom margin, not a ratio: the gallery is
       taller than the viewport on a phone (4027px against 844px), so its
       intersection ratio tops out around 0.21 and a 0.15 ratio needs
       604px of it on screen before anything appears. An element cannot be
       asked for a percentage of itself when it is bigger than the window -
       fire when its top edge arrives instead. */
    const io = new IntersectionObserver(entries => {
      for (const { target, isIntersecting } of entries) {
        if (!isIntersecting) continue;
        target.classList.add('is-in');
        io.unobserve(target);
      }
    }, { threshold: 0, rootMargin: '0px 0px -10% 0px' });

    for (const el of els) io.observe(el);
  };

  /* ---------- TiltCard: 3D tilt following the pointer, with glare ---------- */

  const initTilt = () => {
    const MAX_TILT = 9;

    for (const el of document.querySelectorAll('.tod-tilt')) {
      if (!el.querySelector('.tod-glare')) {
        const glare = document.createElement('span');
        glare.className = 'tod-glare';
        glare.setAttribute('aria-hidden', 'true');
        el.append(glare);
      }

      el.addEventListener('pointermove', ({ clientX, clientY }) => {
        const { left, top, width, height } = el.getBoundingClientRect();
        const px = (clientX - left) / width;
        const py = (clientY - top) / height;
        el.style.setProperty('--rx', `${((0.5 - py) * 2 * MAX_TILT).toFixed(2)}deg`);
        el.style.setProperty('--ry', `${((px - 0.5) * 2 * MAX_TILT).toFixed(2)}deg`);
        el.style.setProperty('--gx', `${(px * 100).toFixed(1)}%`);
        el.style.setProperty('--gy', `${(py * 100).toFixed(1)}%`);
      }, { passive: true });

      el.addEventListener('pointerleave', () => {
        el.style.setProperty('--rx', '0deg');
        el.style.setProperty('--ry', '0deg');
        el.style.setProperty('--gx', '50%');
        el.style.setProperty('--gy', '50%');
      });
    }
  };

  /* ---------- Waveform: the logo's equalizer, alive ---------- */

  const initWave = () => {
    const HEIGHTS = [10, 22, 34, 16, 27, 34, 12, 30, 18, 33, 14, 24];

    for (const el of document.querySelectorAll('.tod-wave')) {
      if (el.children.length) continue;
      el.setAttribute('aria-hidden', 'true');
      el.append(...HEIGHTS.map((h, i) => {
        const bar = document.createElement('i');
        bar.style.setProperty('--h', `${h}px`);
        bar.style.setProperty('--d', `${1.1 + (i % 5) * 0.14}s`);
        bar.style.setProperty('--dl', `${i * 0.08}s`);
        return bar;
      }));
    }
  };

  /* ---------- Spores: ambient particles drifting up through the hero ----------
     Straight port of t2's Spores.jsx - canvas, sized to its host,
     paused when the tab is hidden. Default colors ARE the pink night. */

  const initSpores = () => {
    const COLORS = ['#ff3ecf', '#37f5e0', '#8a5cff', '#b8ff2e', '#f0e9ff'];

    for (const host of document.querySelectorAll('.tod-atmo')) {
      if (host.querySelector('canvas')) continue;

      const canvas = document.createElement('canvas');
      canvas.setAttribute('aria-hidden', 'true');
      host.append(canvas);

      const ctx = canvas.getContext('2d');
      const dpr = Math.min(devicePixelRatio || 1, 2);
      let W = 0;
      let H = 0;
      let spores = [];
      let raf = 0;
      let running = true;

      const makeSpore = fresh => ({
        x: Math.random() * W,
        y: fresh ? H + 10 : Math.random() * H,
        r: 0.8 + Math.random() * 2.2,
        vy: 0.15 + Math.random() * 0.45,
        sway: Math.random() * Math.PI * 2,
        swaySpeed: 0.004 + Math.random() * 0.01,
        swayAmp: 0.3 + Math.random() * 0.7,
        color: COLORS[(Math.random() * COLORS.length) | 0],
        alpha: 0.25 + Math.random() * 0.55
      });

      const resize = () => {
        W = host.clientWidth;
        H = host.clientHeight;
        canvas.width = W * dpr;
        canvas.height = H * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        const count = Math.min(90, Math.max(35, (W * H) / 22000));
        spores = Array.from({ length: count }, () => makeSpore(false));
      };

      const frame = () => {
        if (!running) return;
        ctx.clearRect(0, 0, W, H);

        for (let i = 0; i < spores.length; i++) {
          const s = spores[i];
          s.y -= s.vy;
          s.sway += s.swaySpeed;
          s.x += Math.sin(s.sway) * s.swayAmp * 0.4;
          if (s.y < -12) spores[i] = makeSpore(true);

          const { x, y, r, color, alpha } = spores[i];
          ctx.globalAlpha = alpha;
          ctx.fillStyle = color;
          ctx.shadowColor = color;
          ctx.shadowBlur = 8;
          ctx.beginPath();
          ctx.arc(x, y, r, 0, Math.PI * 2);
          ctx.fill();
        }

        ctx.globalAlpha = 1;
        ctx.shadowBlur = 0;
        raf = requestAnimationFrame(frame);
      };

      const onVisibility = () => {
        const wasRunning = running;
        running = !document.hidden;
        if (running && !wasRunning) raf = requestAnimationFrame(frame);
      };

      resize();
      raf = requestAnimationFrame(frame);
      addEventListener('resize', resize);
      document.addEventListener('visibilitychange', onVisibility);
    }
  };

  ready(() => {
    initSplit();
    initReveal();
    initTilt();
    initWave();
    initSpores();
  });
})();
