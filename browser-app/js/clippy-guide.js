/**
 * ClippyGuide — A Clippy-inspired helper avatar for QA Pilot capstones
 * ===================================================================
 * Provides a guided intro sequence and contextual tips during capstone
 * assessments via a friendly paperclip avatar with speech bubbles.
 * No external images — everything is drawn with inline SVG and CSS
 * (injected automatically on first init).
 *
 * ── QUICK START ────────────────────────────────────────────────────
 *
 *   <script src="js/clippy-guide.js"></script>
 *   <script>
 *     ClippyGuide.init({
 *       tips: [...],
 *       expectedBugs: 4,          // warn before submit if under this count
 *       onSubmit: function() { ... },
 *       events: {
 *         'BUG_LOGGED': function(msg) { return "Nice find! 🐛"; }
 *       }
 *     });
 *
 *     // When the OS iframe loads, kick off the guided intro:
 *     ClippyGuide.runIntro({
 *       steps: [
 *         { text: "Welcome, Alex! I'm Clip — your guide.", position: 'center' },
 *         { text: "Step 1 — Open Teams for your briefing.", position: 'taskbar-mid' },
 *         // ...
 *       ],
 *       onComplete: function() { ClippyGuide.enableSubmit(true); }
 *     });
 *   </script>
 *
 * ── PUBLIC API ─────────────────────────────────────────────────────
 *
 *   ClippyGuide.init(opts)          — Initialise (call once on page load)
 *   ClippyGuide.runIntro(opts)      — Play guided intro sequence
 *   ClippyGuide.start()             — Show guide + first tip (skip intro)
 *   ClippyGuide.show()              — Show guide if hidden
 *   ClippyGuide.hideBubble()        — Hide bubble only (avatar stays)
 *   ClippyGuide.nextTip()           — Advance to next tip (or intro step)
 *   ClippyGuide.goToTip(n)          — Jump to specific tip index
 *   ClippyGuide.say(text, opts)     — One-off announcement message
 *   ClippyGuide.dismiss()           — Permanently hide and persist to localStorage
 *   ClippyGuide.reset()             — Clear dismissal state
 *   ClippyGuide.setTips(arr)        — Update tip sequence dynamically
 *   ClippyGuide.enableSubmit(bool)  — Show/hide submit button at end of tips
 *   ClippyGuide.moveTo(position)    — Animate Clip to a named screen position
 *   ClippyGuide.goHome()            — Animate back to home (bottom-right)
 *   ClippyGuide.getBugCount()       — Returns how many bugs have been logged
 *   ClippyGuide.resetBugCount()     — Resets the bug counter to 0
 *   ClippyGuide.resetOS()           — Clear localStorage + IndexedDB, reload page
 *
 *   ClippyGuide.currentIndex        — (getter) current tip index
 *   ClippyGuide.totalTips           — (getter) total number of tips
 *
 * ── NAMED POSITIONS (for moveTo / intro steps) ─────────────────────
 *
 *   'home'          — bottom-right corner (default)
 *   'center'        — centre of the viewport
 *   'top-left'      — near top-left desktop icons
 *   'top-right'     — near top-right
 *   'taskbar-left'  — bottom-left (near first taskbar app)
 *   'taskbar-mid'   — bottom-centre (middle of taskbar)
 *   'taskbar-right' — bottom-right area of taskbar
 */
(function () {
  'use strict';

  // ── Configuration ──────────────────────────────────────────────────────
  var AUTO_ADVANCE_MS  = 45000;   // ms between auto-tip advances
  var TYPING_SPEED_MS  = 35;      // ms per character in typewriter effect
  var STORAGE_KEY      = 'clippy-guide-dismissed-v1';
  var MOVE_DURATION_MS = 650;     // ms for moveTo animation

  // ── Named screen positions ─────────────────────────────────────────────
  // Each position is a CSS property map applied to the guide element.
  // 'home' is the default fixed position. Others reposition Clip
  // to approximate landmarks in the OS desktop iframe below.
  var POSITIONS = {
    'home':          { bottom: '78px',  right: '24px' },
    'center':        { top: '50%',      left: '50%',   transform: 'translate(-50%, -60%)' },
    'top-left':      { top: '130px',    left: '70px' },
    'top-right':     { top: '130px',    right: '70px' },
    'taskbar-left':  { bottom: '90px',  left: '160px' },
    'taskbar-mid':   { bottom: '90px',  left: '50%',   transform: 'translateX(-50%)' },
    'taskbar-right': { bottom: '90px',  right: '160px' }
  };

  // ── State ──────────────────────────────────────────────────────────────
  var tips            = [];
  var currentIndex    = 0;
  var autoTimer       = null;
  var typingTimer     = null;
  var isTyping        = false;
  var onSubmitCb      = null;
  var submitEnabled   = false;
  var isDismissed     = false;
  var expectedBugs    = 0;    // set via init({ expectedBugs: N })
  var bugCount        = 0;    // auto-incremented on BUG_LOGGED events

  // Intro state
  var introSteps      = [];
  var introIndex      = 0;
  var introOnComplete = null;
  var isIntroActive   = false;
  var introOverlayEl  = null;

  // ── DOM refs ───────────────────────────────────────────────────────────
  var guideEl    = null;
  var bubbleEl   = null;
  var textEl     = null;
  var counterEl  = null;
  var avatarEl   = null;
  var submitBtn  = null;
  var prevBtn    = null;
  var nextBtn    = null;
  var closeBtn   = null;

  // ═══════════════════════════════════════════════════════════════════════
  //  PUBLIC API
  // ═══════════════════════════════════════════════════════════════════════

  window.ClippyGuide = {

    /**
     * Initialise the guide. Call once when the capstone page loads.
     * The intro sequence and tip display are triggered separately.
     *
     * @param {Object}   opts
     * @param {string[]} opts.tips          — Regular tip messages (shown after intro)
     * @param {number}   [opts.expectedBugs]— Warn before submit if bugs found < this
     * @param {Function} [opts.onSubmit]    — Called when user clicks Submit in Clip
     * @param {Object}   [opts.events]      — Map of OS event type → message or fn(msg)
     * @param {boolean}  [opts.autoStart]   — If true, show first tip immediately (default false)
     */
    init: function (opts) {
      opts           = opts || {};
      tips           = opts.tips || [];
      expectedBugs   = opts.expectedBugs || 0;
      onSubmitCb     = opts.onSubmit || null;

      _injectStyles();
      _ensureDOM();
      _listenForOSEvents(opts.events || null);

      try { isDismissed = localStorage.getItem(STORAGE_KEY) === '1'; } catch (e) {}
      if (isDismissed) { _hideGuide(); return; }

      if (opts.autoStart === true && tips.length) {
        setTimeout(function () { _showGuide(); _showTip(0); }, 2500);
      }
    },

    /**
     * Run the guided intro sequence. Call this after the OS iframe loads.
     * Clip moves to centre, plays through each step, then calls onComplete.
     *
     * @param {Object}     opts
     * @param {Array}      opts.steps         — Array of { text, position? } objects
     * @param {Function}   [opts.onComplete]  — Called when intro finishes
     */
    runIntro: function (opts) {
      opts            = opts || {};
      introSteps      = opts.steps || [];
      introOnComplete = opts.onComplete || null;

      if (!introSteps.length) {
        // Nothing to show — just start tips
        if (introOnComplete) introOnComplete();
        return;
      }

      isDismissed  = false;
      isIntroActive = true;
      introIndex   = 0;

      _showGuide();
      _buildIntroOverlay();

      // Small delay so the overlay fades in before Clip appears
      setTimeout(function () {
        _moveTo('center');
        setTimeout(function () { _showIntroStep(0); }, 300);
      }, 150);
    },

    /** Show guide and first tip (skips intro — for simple init) */
    start: function () {
      if (isDismissed) return;
      _showGuide();
      if (tips.length) _showTip(0);
    },

    /** Show the guide if it was hidden */
    show: function () { _showGuide(); _showBubble(); },

    /** Hide the speech bubble; avatar stays visible */
    hideBubble: function () { _hideBubble(); _clearAutoTimer(); },

    /**
     * Advance to the next tip. If intro is active, advance the intro step.
     * If a typewriter animation is in progress, finish it instead of advancing.
     */
    nextTip: function () {
      if (isIntroActive) {
        _showIntroStep(introIndex + 1);
        return;
      }
      if (isTyping) { _finishTyping(); return; }
      _clearAutoTimer();
      var next = currentIndex + 1;
      if (next >= tips.length) {
        if (submitEnabled && onSubmitCb) { _showSubmitPrompt(); return; }
        next = 0;
      }
      _showTip(next);
    },

    /** Jump to a specific tip index */
    goToTip: function (index) {
      if (isIntroActive) return; // blocked during intro
      if (index < 0 || index >= tips.length) return;
      _clearAutoTimer();
      _showTip(index);
    },

    /** Show a one-off message (for OS event reactions) */
    say: function (text, opts) {
      opts = opts || {};
      if (!textEl || !bubbleEl) return;
      if (isIntroActive) return;  // don't interrupt intro
      _clearAutoTimer();
      textEl.textContent = text;
      if (counterEl) counterEl.textContent = '';
      if (submitBtn) submitBtn.style.display = 'none';
      _showBubble();
      _showGuide();
      if (opts.persist !== false) _restartAutoTimer();
    },

    /** Permanently dismiss the guide and persist to localStorage */
    dismiss: function () {
      isDismissed = true;
      _hideGuide();
      try { localStorage.setItem(STORAGE_KEY, '1'); } catch (e) {}
    },

    /** Clear the dismissal state */
    reset: function () {
      isDismissed = false;
      try { localStorage.removeItem(STORAGE_KEY); } catch (e) {}
    },

    /** Replace the tip array and reset to first tip */
    setTips: function (newTips) {
      tips         = newTips || [];
      currentIndex = 0;
    },

    /**
     * Enable or disable the Submit button shown at the end of all tips.
     * Note: this only sets the flag. The button only appears when the last
     * tip has been displayed and the user advances past it.
     */
    enableSubmit: function (enabled) {
      submitEnabled = !!enabled;
    },

    /**
     * Animate Clip to a named screen position.
     * See POSITIONS map at the top of this file for available names.
     * @param {string} positionName
     */
    moveTo: function (positionName) {
      _moveTo(positionName || 'home');
    },

    /** Animate Clip back to the default home position (bottom-right) */
    goHome: function () {
      _moveTo('home');
    },

    /** How many BUG_LOGGED events have been received this session */
    getBugCount: function () { return bugCount; },

    /** Reset the bug counter (e.g. if the student retries the capstone) */
    resetBugCount: function () { bugCount = 0; },

    // Read-only getters
    get currentIndex() { return currentIndex; },
    get totalTips()    { return tips.length; }
  };

  // ═══════════════════════════════════════════════════════════════════════
  //  CSS — injected on first init (no separate stylesheet needed)
  // ═══════════════════════════════════════════════════════════════════════

  function _injectStyles() {
    if (document.getElementById('clippy-guide-styles')) return;
    var s = document.createElement('style');
    s.id = 'clippy-guide-styles';
    s.textContent = [
      /* ── Guide wrapper ── */
      '.clippy-guide{position:fixed;bottom:78px;right:24px;z-index:99999;display:flex;flex-direction:column;align-items:flex-end;gap:10px;font-family:"Segoe UI",system-ui,-apple-system,sans-serif;transition:bottom ' + MOVE_DURATION_MS + 'ms cubic-bezier(.34,1.56,.64,1),right ' + MOVE_DURATION_MS + 'ms cubic-bezier(.34,1.56,.64,1),left ' + MOVE_DURATION_MS + 'ms cubic-bezier(.34,1.56,.64,1),top ' + MOVE_DURATION_MS + 'ms cubic-bezier(.34,1.56,.64,1),transform ' + MOVE_DURATION_MS + 'ms cubic-bezier(.34,1.56,.64,1)}',
      '.clippy-guide.clippy-hidden{opacity:0;pointer-events:none}',

      /* ── Speech bubble ── */
      '.clippy-bubble{position:relative;background:#fff;border:1px solid #e2e8f0;border-radius:16px;box-shadow:0 8px 30px rgba(0,0,0,.12),0 2px 8px rgba(0,0,0,.06);max-width:400px;min-width:240px;animation:clippy-pop .35s cubic-bezier(.34,1.56,.64,1)}',
      '@keyframes clippy-pop{from{opacity:0;transform:translateY(12px) scale(.92)}to{opacity:1;transform:translateY(0) scale(1)}}',
      '.clippy-bubble-inner{padding:16px 18px 12px}',
      '.clippy-bubble-tail{position:absolute;bottom:-7px;right:30px;width:14px;height:14px;background:#fff;border-right:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;transform:rotate(45deg)}',

      /* ── Bubble text & footer ── */
      '.clippy-text{font-size:14px;line-height:1.55;color:#1e293b;min-height:22px}',
      '.clippy-bubble-footer{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;margin-top:12px;padding-top:10px;border-top:1px solid #f1f5f9}',
      '.clippy-counter{font-size:11px;color:#94a3b8;font-weight:500}',
      '.clippy-bubble-actions{display:flex;gap:4px;align-items:center}',

      /* ── Buttons ── */
      '.clippy-btn{border:none;border-radius:6px;font-size:12px;font-weight:600;font-family:inherit;cursor:pointer;padding:5px 12px;transition:all .15s ease;line-height:1}',
      '.clippy-btn-primary{background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff}',
      '.clippy-btn-primary:hover{filter:brightness(1.1);transform:translateY(-1px)}',
      '.clippy-btn-primary:active{transform:translateY(0)}',
      /* Intro "Next" button is slightly larger */
      '.clippy-intro-active .clippy-btn-primary{padding:7px 18px;font-size:13px}',
      '.clippy-btn-submit{background:linear-gradient(135deg,#10b981,#059669);color:#fff;padding:7px 20px;font-size:13px;font-weight:700;border-radius:8px;animation:clippy-glow 2s ease-in-out infinite;width:100%;margin-top:6px}',
      '.clippy-btn-submit:hover{filter:brightness(1.15);transform:translateY(-1px)}',
      '.clippy-btn-submit:active{transform:translateY(0)}',
      '@keyframes clippy-glow{0%,100%{box-shadow:0 0 4px rgba(16,185,129,.3)}50%{box-shadow:0 0 14px rgba(16,185,129,.6)}}',
      '.clippy-btn-ghost{background:transparent;color:#64748b}',
      '.clippy-btn-ghost:hover{background:#f1f5f9;color:#334155}',

      /* ── Avatar ── */
      '.clippy-avatar{width:100px;height:100px;cursor:pointer;filter:drop-shadow(0 3px 10px rgba(0,0,0,.18));transition:transform .2s cubic-bezier(.34,1.56,.64,1);animation:clippy-bob 3.5s ease-in-out infinite}',
      '.clippy-avatar:hover{transform:scale(1.12);animation-play-state:paused}',
      '.clippy-avatar:active{transform:scale(.95)}',
      '@keyframes clippy-bob{0%,100%{transform:translateY(0) rotate(0deg)}15%{transform:translateY(-3px) rotate(-.6deg)}35%{transform:translateY(-6px) rotate(.6deg)}55%{transform:translateY(-5px) rotate(-.3deg)}75%{transform:translateY(-2px) rotate(.3deg)}}',
      '.clippy-avatar svg{width:100%;height:100%;overflow:visible}',

      /* ── Pointing arm ── */
      '.clip-point-arm{transition:opacity .3s ease;transform-origin:88px 68px}',
      '.clippy-avatar.pointing .clip-point-arm{opacity:1;animation:clip-point-arm .6s cubic-bezier(.34,1.56,.64,1) forwards}',
      '@keyframes clip-point-arm{0%{opacity:0;transform:scale(0)}60%{opacity:1;transform:scale(1.2)}100%{opacity:1;transform:scale(1)}}',

      /* ── Eye blink ── */
      '.clippy-eye{transform-origin:center;animation:clippy-blink 4.2s infinite}',
      '@keyframes clippy-blink{0%,96%,100%{transform:scaleY(1)}98%{transform:scaleY(.15)}}',

      /* ── Intro overlay backdrop ── */
      '.clippy-intro-overlay{position:fixed;inset:0;background:rgba(15,23,42,0.72);z-index:99998;pointer-events:all}',
      '@keyframes clippy-intro-in{from{opacity:0}to{opacity:1}}',
      '@keyframes clippy-intro-out{from{opacity:1}to{opacity:0}}',

      /* ── Intro step counter style ── */
      '.clippy-intro-active .clippy-counter{color:#3b82f6;font-weight:700;font-size:12px}',

      /* ── Responsive ── */
      '@media(max-width:640px){.clippy-guide{bottom:66px;right:12px}.clippy-bubble{max-width:320px}.clippy-avatar{width:80px;height:80px}}'
    ].join('\n');
    document.head.appendChild(s);
  }

  // ═══════════════════════════════════════════════════════════════════════
  //  DOM SETUP
  // ═══════════════════════════════════════════════════════════════════════

  function _ensureDOM() {
    if (document.getElementById('clippy-guide')) return;

    var c = document.createElement('div');
    c.id        = 'clippy-guide';
    c.className = 'clippy-guide clippy-hidden';
    c.innerHTML =
      '<div class="clippy-bubble" id="clippy-bubble" style="display:none">' +
        '<div class="clippy-bubble-inner">' +
          '<div class="clippy-text" id="clippy-text"></div>' +
          '<div class="clippy-bubble-footer">' +
            '<span class="clippy-counter" id="clippy-counter"></span>' +
            '<div class="clippy-bubble-actions">' +
              '<button class="clippy-btn clippy-btn-ghost" id="clippy-prev" title="Previous">←</button>' +
              '<button class="clippy-btn clippy-btn-primary" id="clippy-next">Next →</button>' +
              '<button class="clippy-btn clippy-btn-ghost" id="clippy-close" title="Dismiss">×</button>' +
              '<button class="clippy-btn clippy-btn-ghost" id="clippy-startover" title="Start Over" style="color:#dc2626;font-size:11px;padding:5px 6px;">↺</button>' +
            '</div>' +
          '</div>' +
        '</div>' +
        '<div class="clippy-bubble-tail"></div>' +
      '</div>' +
      '<div class="clippy-avatar" id="clippy-avatar" title="Click me!">' +
        '<svg viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">' +
          '<defs>' +
            '<linearGradient id="clipGrad" x1="0%" y1="0%" x2="100%" y2="100%">' +
              '<stop offset="0%" style="stop-color:#f7dc6f"/>' +
              '<stop offset="100%" style="stop-color:#f4d03f"/>' +
            '</linearGradient>' +
          '</defs>' +
          '<ellipse cx="60" cy="130" rx="28" ry="6" fill="rgba(0,0,0,0.12)"/>' +
          '<path d="M45,25 L45,95 Q45,112 58,112 L68,112 Q82,112 82,95 L82,48 Q82,35 68,35 L55,35 Q42,35 42,48 L42,85 Q42,95 52,95 L65,95 Q75,95 75,85 L75,52"' +
          ' fill="none" stroke="url(#clipGrad)" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>' +
          '<ellipse cx="52" cy="48" rx="7" ry="9" fill="white"/>' +
          '<ellipse cx="72" cy="48" rx="7" ry="9" fill="white"/>' +
          '<circle cx="52" cy="48" r="3.5" fill="#333" class="clippy-eye"/>' +
          '<circle cx="72" cy="48" r="3.5" fill="#333" class="clippy-eye"/>' +
          '<path d="M46,38 Q52,35 58,38" fill="none" stroke="#d4ac0d" stroke-width="2" stroke-linecap="round"/>' +
          '<path d="M66,38 Q72,35 78,38" fill="none" stroke="#d4ac0d" stroke-width="2" stroke-linecap="round"/>' +
          '<g class="clip-point-arm" opacity="0" transform="translate(88,68)">' +
            '<line x1="0" y1="0" x2="28" y2="-32" stroke="url(#clipGrad)" stroke-width="6" stroke-linecap="round"/>' +
            '<polygon points="28,-32 20,-44 35,-38" fill="#f4d03f"/>' +
          '</g>' +
        '</svg>' +
      '</div>';

    document.body.appendChild(c);

    // Cache refs
    guideEl   = c;
    bubbleEl  = document.getElementById('clippy-bubble');
    textEl    = document.getElementById('clippy-text');
    counterEl = document.getElementById('clippy-counter');
    avatarEl  = document.getElementById('clippy-avatar');
    prevBtn   = document.getElementById('clippy-prev');
    nextBtn   = document.getElementById('clippy-next');
    closeBtn  = document.getElementById('clippy-close');

    // Submit button — created separately, appended to bubble footer
    submitBtn = document.createElement('button');
    submitBtn.className  = 'clippy-btn clippy-btn-submit';
    submitBtn.textContent = '✓ Submit Assessment';
    submitBtn.style.display = 'none';
    submitBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      _handleSubmitClick();
    });
    var footer = c.querySelector('.clippy-bubble-footer');
    if (footer) footer.appendChild(submitBtn);

    // ── Event bindings ──────────────────────────────────────────────────

    avatarEl.addEventListener('click', function () {
      if (isIntroActive) return; // avatar click inactive during intro
      if (bubbleEl.style.display !== 'none') {
        window.ClippyGuide.nextTip();
      } else {
        _showBubble();
        _restartAutoTimer();
      }
    });

    nextBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      window.ClippyGuide.nextTip();
    });

    prevBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (isIntroActive) return; // no going back during intro
      _clearAutoTimer();
      var prev = currentIndex - 1;
      if (prev < 0) prev = tips.length - 1;
      _showTip(prev);
    });

    closeBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (isIntroActive) return; // can't close during intro
      _hideBubble();
      _clearAutoTimer();
    });

    // F15: Start Over button — confirm then hard-reset
    var startOverBtn = document.getElementById('clippy-startover');
    if (startOverBtn) {
      startOverBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        if (isIntroActive) return;
        if (window.ClippyGuide) {
          window.ClippyGuide.say('Start over? This will clear all your progress and reset the scenario. Click the ↺ button again to confirm.', { persist: false });
          // On second click within 5s, perform reset
          if (this._resetPending) {
            clearTimeout(this._resetTimer);
            this._resetPending = false;
            if (textEl) textEl.textContent = 'Resetting... one moment! 🔄';
            setTimeout(function () { window.ClippyGuide.resetOS(); }, 600);
          } else {
            this._resetPending = true;
            var btn = this;
            btn._resetTimer = setTimeout(function () { btn._resetPending = false; }, 5000);
          }
        }
      });
    }

    // Close bubble on outside click (but not during intro — overlay blocks it)
    document.addEventListener('click', function (e) {
      if (!guideEl || isDismissed || isIntroActive) return;
      if (!guideEl.contains(e.target)) {
        _hideBubble();
        _clearAutoTimer();
      }
    });
  }

  // ═══════════════════════════════════════════════════════════════════════
  //  INTRO SEQUENCE
  // ═══════════════════════════════════════════════════════════════════════

  /**
   * Build and inject the semi-transparent intro overlay backdrop.
   * Sits below Clip (z-index 99998) to darken the OS desktop while
   * the guided intro plays. Removed automatically when intro finishes.
   */
  function _buildIntroOverlay() {
    if (document.getElementById('clippy-intro-overlay')) return;
    introOverlayEl = document.createElement('div');
    introOverlayEl.id        = 'clippy-intro-overlay';
    introOverlayEl.className = 'clippy-intro-overlay';
    introOverlayEl.style.animation = 'clippy-intro-in 0.4s ease forwards';
    // Clicking the overlay does nothing during the intro
    introOverlayEl.addEventListener('click', function (e) { e.stopPropagation(); });
    document.body.insertBefore(introOverlayEl, document.body.firstChild);
  }

  /**
   * Display a single intro step.
   * @param {number} index — step index into introSteps array
   */
  function _showIntroStep(index) {
    // Past the last step → finish intro
    if (index >= introSteps.length) {
      _finishIntro();
      return;
    }

    introIndex = index;
    var step   = introSteps[index];
    var isLast = (index === introSteps.length - 1);

    // Move Clip to the step's target position (if specified)
    if (step.position) {
      _moveTo(step.position);
    }

    // ── Update bubble content ──
    if (textEl)    textEl.textContent = step.text || '';
    if (counterEl) counterEl.textContent = 'Step ' + (index + 1) + ' of ' + introSteps.length;
    if (submitBtn) submitBtn.style.display = 'none';

    // During intro: hide Prev and Close; change Next label on last step
    if (prevBtn)  prevBtn.style.display  = 'none';
    if (closeBtn) closeBtn.style.display = 'none';
    if (nextBtn)  nextBtn.textContent    = isLast ? "Let's go! 🚀" : 'Next →';

    // Mark guide with intro class so CSS can target intro-specific styles
    if (guideEl) guideEl.classList.add('clippy-intro-active');

    _showBubble();
    _doPoint();
  }

  /**
   * Complete the intro: remove overlay, restore buttons, move home,
   * then start the regular tip sequence.
   */
  function _finishIntro() {
    isIntroActive = false;
    if (guideEl) guideEl.classList.remove('clippy-intro-active');

    // Restore nav buttons
    if (prevBtn)  prevBtn.style.display  = '';
    if (closeBtn) closeBtn.style.display = '';
    if (nextBtn)  nextBtn.textContent    = 'Next';

    // Fade out and remove the backdrop overlay
    if (introOverlayEl) {
      introOverlayEl.style.animation = 'clippy-intro-out 0.5s ease forwards';
      var _overlay = introOverlayEl;
      setTimeout(function () {
        if (_overlay && _overlay.parentNode) _overlay.parentNode.removeChild(_overlay);
        introOverlayEl = null;
      }, 500);
    }

    // Hide the bubble briefly while Clip flies home, then show first tip
    _hideBubble();
    _moveTo('home');

    // Call the caller's onComplete callback (e.g. enableSubmit(true))
    if (introOnComplete) {
      setTimeout(introOnComplete, MOVE_DURATION_MS);
    }

    // Start the regular tip carousel after Clip has settled home
    if (tips.length) {
      setTimeout(function () { _showTip(0); }, MOVE_DURATION_MS + 200);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════
  //  POSITION / MOVEMENT
  // ═══════════════════════════════════════════════════════════════════════

  /**
   * Animate Clip to a named screen position.
   * Resets all four position properties before applying the new ones
   * so there's no conflict between e.g. 'bottom' and 'top'.
   * @param {string} posName — key in POSITIONS map
   */
  function _moveTo(posName) {
    if (!guideEl) return;
    var coords = POSITIONS[posName] || POSITIONS['home'];

    // Clear all position props then apply the target set
    guideEl.style.bottom    = '';
    guideEl.style.right     = '';
    guideEl.style.left      = '';
    guideEl.style.top       = '';
    guideEl.style.transform = '';

    Object.keys(coords).forEach(function (prop) {
      guideEl.style[prop] = coords[prop];
    });
  }

  // ═══════════════════════════════════════════════════════════════════════
  //  OS EVENT LISTENER
  // ═══════════════════════════════════════════════════════════════════════

  /**
   * Listen for postMessage events from the OS iframe.
   * Automatically counts BUG_LOGGED events for the pre-submit check.
   * Calls caller-provided handlers for other event types.
   * @param {Object|null} handlers — map of eventType → string | fn(msg)
   */
  function _listenForOSEvents(handlers) {
    window.addEventListener('message', function (event) {
      var msg = event.data;
      if (!msg || !msg.type) return;

      // ── Auto-count bugs ─────────────────────────────────────────────
      // BUG_LOGGED fires from ADO app whenever the student saves a report
      if (msg.type === 'BUG_LOGGED') {
        bugCount++;
        console.log('[ClippyGuide] Bug logged — total count: ' + bugCount);
      }

      // F11: Clip reacts to BUG_FOUND from Dynamics with per-bugId encouragement
      if (msg.type === 'BUG_FOUND' && !isIntroActive) {
        var encouragements = {
          'default': [
            "You spotted something! Add it to ADO to log it properly. 🐛",
            "Good eye! That doesn't look right — file it in ADO! 🔍",
            "Nice catch! Make sure you document what you found. 📝",
            "Another one! Keep digging — you're doing great! 💪",
          ],
        };
        var messages = encouragements[msg.bugId] || encouragements['default'];
        var reply = messages[Math.floor(Math.random() * messages.length)];
        if (msg.acRef) {
          reply += " (See " + msg.acRef + ")";
        }
        if (window.ClippyGuide && !isIntroActive) {
          window.ClippyGuide.say(reply);
        }
      }

      // ── Caller-provided event reactions ─────────────────────────────
      if (!handlers || !handlers[msg.type]) return;
      var reaction = handlers[msg.type];
      var text = typeof reaction === 'function' ? reaction(msg) : reaction;
      if (text && window.ClippyGuide && !isIntroActive) {
        window.ClippyGuide.say(text);
      }
    });
  }

  // ═══════════════════════════════════════════════════════════════════════
  //  SUBMIT HANDLING
  // ═══════════════════════════════════════════════════════════════════════

  /**
   * Called when the student clicks Clip's Submit button.
   * Checks whether the expected number of bugs have been found.
   * If under the threshold, shows a warning and re-enables the submit
   * button after a short delay so the student can still proceed.
   */
  function _handleSubmitClick() {
    if (!onSubmitCb) return;

    // If expectedBugs is set and student is under the threshold — warn first
    if (expectedBugs > 0 && bugCount < expectedBugs) {
      var missing = expectedBugs - bugCount;
      var warnMsg = bugCount === 0
        ? "Hmm, it looks like no bugs have been filed yet! There are " + expectedBugs + " bugs to find. Keep investigating — then come back to submit! 🔍"
        : "You've filed " + bugCount + " bug" + (bugCount === 1 ? '' : 's') + " — but there " + (missing === 1 ? 'is' : 'are') + " still " + missing + " more to find! Are you sure you're ready to submit? Click Submit again to confirm. 🤔";

      // Show warning in bubble with a re-enabled submit button after 3 s
      if (textEl)    textEl.textContent = warnMsg;
      if (counterEl) counterEl.textContent = bugCount + ' / ' + expectedBugs + ' bugs filed';
      if (submitBtn) submitBtn.style.display = 'none';
      _showBubble();

      // Re-enable submit after delay — student can override the warning
      setTimeout(function () {
        if (submitBtn) {
          submitBtn.textContent  = '⚠️ Submit Anyway';
          submitBtn.style.display = '';
          // Override: next click goes straight through
          submitBtn.onclick = function (e) {
            e.stopPropagation();
            _hideBubble();
            onSubmitCb();
            // Restore button text for next time
            submitBtn.textContent = '✓ Submit Assessment';
            submitBtn.onclick = null;
          };
        }
      }, 3000);
      return;
    }

    // All (or enough) bugs found — proceed immediately
    _hideBubble();
    onSubmitCb();
  }

  // ═══════════════════════════════════════════════════════════════════════
  //  TIPS
  // ═══════════════════════════════════════════════════════════════════════

  function _showSubmitPrompt() {
    if (!textEl || !bubbleEl) return;
    var msgs = [
      'Ready to submit your findings? You\'ve done a thorough investigation! 🎯',
      'All done investigating? Hit submit and let\'s see your results! 🏆',
      'Think you found everything? Time to submit and get your score! ✨',
      'The QA Lead is waiting for your report — ready to submit? 📋',
      'You\'ve been working hard! Ready to see how you did? 💪'
    ];
    textEl.textContent = msgs[Math.floor(Math.random() * msgs.length)];
    if (counterEl) counterEl.textContent = '';
    if (submitBtn) submitBtn.style.display = '';
    _showBubble();
    _doPoint();
  }

  function _showTip(index) {
    if (!textEl || !tips.length) return;
    currentIndex = index;

    if (submitBtn) submitBtn.style.display = 'none';

    _showBubble();
    _typewriter(tips[currentIndex]);
    _updateCounter();
    _restartAutoTimer();
    _doPoint();
  }

  function _updateCounter() {
    if (counterEl) counterEl.textContent = (currentIndex + 1) + ' / ' + tips.length;
  }

  // ═══════════════════════════════════════════════════════════════════════
  //  HELPERS
  // ═══════════════════════════════════════════════════════════════════════

  function _showGuide()  { if (guideEl) guideEl.classList.remove('clippy-hidden'); }
  function _hideGuide()  { if (guideEl) guideEl.classList.add('clippy-hidden'); _clearAutoTimer(); }
  function _showBubble() { if (bubbleEl) bubbleEl.style.display = ''; }
  function _hideBubble() {
    if (bubbleEl) bubbleEl.style.display = 'none';
    if (typingTimer) { clearInterval(typingTimer); typingTimer = null; }
    isTyping = false;
  }

  function _typewriter(text) {
    if (typingTimer) clearInterval(typingTimer);
    isTyping = true;
    textEl.textContent = '';
    var i = 0;
    typingTimer = setInterval(function () {
      if (i >= text.length) {
        clearInterval(typingTimer);
        typingTimer = null;
        isTyping = false;
        return;
      }
      textEl.textContent += text.charAt(i);
      i++;
    }, TYPING_SPEED_MS);
  }

  function _finishTyping() {
    if (typingTimer) { clearInterval(typingTimer); typingTimer = null; }
    if (tips[currentIndex]) textEl.textContent = tips[currentIndex];
    isTyping = false;
  }

  function _restartAutoTimer() {
    _clearAutoTimer();
    autoTimer = setTimeout(function () {
      if (isIntroActive) return; // never auto-advance during intro
      var next = currentIndex + 1;
      if (next >= tips.length) next = 0;
      _showTip(next);
    }, AUTO_ADVANCE_MS);
  }

  function _clearAutoTimer() {
    if (autoTimer) { clearTimeout(autoTimer); autoTimer = null; }
  }

  /** Trigger the pointing arm animation on Clip's avatar */
  function _doPoint() {
    if (!avatarEl) return;
    avatarEl.classList.remove('pointing');
    void avatarEl.offsetWidth; // force reflow so animation re-triggers
    avatarEl.classList.add('pointing');
    setTimeout(function () {
      if (avatarEl) avatarEl.classList.remove('pointing');
    }, 1200);
  }

  // ═══════════════════════════════════════════════════════════════════════
  //  UTILITY — OS STATE RESET
  // ═══════════════════════════════════════════════════════════════════════

  /**
   * Hard-reset the QA Pilot OS state: clears localStorage and deletes
   * the qa_onboarding_db IndexedDB, then reloads the page.
   * Useful for testing and for students who want a clean start.
   * Call from browser console: ClippyGuide.resetOS()
   */
  window.ClippyGuide.resetOS = function () {
    try { localStorage.clear(); } catch (e) {}
    try {
      var req = indexedDB.deleteDatabase('qa_onboarding_db');
      req.onsuccess = function () { window.location.reload(); };
      req.onerror   = function () { window.location.reload(); };
      setTimeout(function () { window.location.reload(); }, 2000);
    } catch (e) {
      window.location.reload();
    }
  };

})();
