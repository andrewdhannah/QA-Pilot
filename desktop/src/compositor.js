(function () {
  var C = {
    _container: null,
    _windows: [],
    _nextId: 1,
    _nextZ: 1,
    _activeId: null,

    // Configuration
    cascadeStepX: 28,
    cascadeStepY: 22,
    maxCascade: 6,

    init: function (containerEl) {
      this._container = containerEl;
    },

    // ── Window CRUD ────────────────────────────────────────────

    createWindow: function (appId, opts) {
      opts = opts || {};
      var id = this._nextId++;
      var z = this._nextZ++;
      var openCount = this._windows.length;
      var step = openCount % this.maxCascade;

      var cw = this._container ? this._container.clientWidth : 0;
      var ch = this._container ? this._container.clientHeight : 0;
      var defaultW = cw > 100 ? Math.min(800, cw * 0.68) : 800;
      var defaultH = ch > 100 ? Math.min(600, ch * 0.68) : 600;

      var win = {
        id: id,
        appId: appId,
        z: z,
        layout: opts.layout || "normal",
        minimized: false,
        x: typeof opts.x === "number" ? opts.x : 160 + step * this.cascadeStepX,
        y: typeof opts.y === "number" ? opts.y : 80 + step * this.cascadeStepY,
        width: typeof opts.width === "number" ? opts.width : defaultW,
        height: typeof opts.height === "number" ? opts.height : defaultH,
        browserState: opts.browserState || null,
        isWorkBrowser: opts.isWorkBrowser || false,
        extra: opts.extra || {},
      };

      this._windows.push(win);
      this._activeId = id;

      this._emit("window-created", { win: win, appId: appId });

      return win;
    },

    destroyWindow: function (winId) {
      var idx = this._findIndex(winId);
      if (idx === -1) return false;
      var win = this._windows[idx];

      this._windows.splice(idx, 1);
      this._unregisterIframe(winId);
      if (this._activeId === winId) {
        this._activeId = this._windows.length
          ? this._windows[this._windows.length - 1].id
          : null;
      }

      this._emit("window-destroyed", { win: win, winId: winId });

      return true;
    },

    // ── Z-order / focus ────────────────────────────────────────

    focus: function (winId, opts) {
      opts = opts || {};

      // Allow null to clear active focus (all windows minimized)
      if (winId === null) {
        this._activeId = null;
        this._emit("window-focused", { win: null, winId: null, wasMinimized: false });
        return false;
      }

      var win = this._find(winId);
      if (!win) return false;

      var needsUnminimize = win.minimized;
      if (opts.unminimize !== false) {
        win.minimized = false;
      }
      win.z = this._nextZ++;
      this._activeId = winId;

      this._emit("window-focused", { win: win, winId: winId, wasMinimized: needsUnminimize });

      return needsUnminimize;
    },

    minimize: function (winId) {
      var win = this._find(winId);
      if (!win) return;
      win.minimized = true;
      if (this._activeId === winId) {
        this._activeId = null;
      }
      this._emit("window-minimized", { win: win, winId: winId });
    },

    setLayout: function (winId, layout) {
      var win = this._find(winId);
      if (!win) return;
      var valid = ["maximized", "normal", "snap-left", "snap-right", "snap-tl", "snap-tr", "snap-bl", "snap-br"];
      if (valid.indexOf(layout) !== -1) {
        if (layout === "maximized") win.minimized = false;
        win.layout = layout;
        this._emit("window-layout-changed", { win: win, winId: winId, layout: layout });
      }
    },

    toggleMaximize: function (winId) {
      var win = this._find(winId);
      if (!win) return;
      this.setLayout(winId, win.layout === "maximized" ? "normal" : "maximized");
    },

    resize: function (winId, x, y, w, h) {
      var win = this._find(winId);
      if (!win) return;
      if (typeof x === "number") win.x = x;
      if (typeof y === "number") win.y = y;
      win.width = Math.max(280, w);
      win.height = Math.max(200, h);
      this._emit("window-layout-changed", { win: win, winId: winId, layout: win.layout });
    },

    // ── State queries ──────────────────────────────────────────

    getWindow: function (winId) {
      return this._find(winId);
    },

    getWindows: function () {
      return this._windows;
    },

    getActiveId: function () {
      return this._activeId;
    },

    getWindowsByApp: function (appId) {
      return this._windows.filter(function (w) { return w.appId === appId; });
    },

    getVisibleWindows: function () {
      return this._windows.filter(function (w) { return !w.minimized; });
    },

    getWindowsGroupedByApp: function () {
      var byApp = {};
      this._windows.forEach(function (w) {
        if (!byApp[w.appId]) byApp[w.appId] = [];
        byApp[w.appId].push(w);
      });
      return byApp;
    },

    // ── Serialization (for persistence) ────────────────────────

    serialize: function () {
      return this._windows.map(function (w) {
        return {
          id: w.id,
          appId: w.appId,
          z: w.z,
          layout: w.layout,
          minimized: w.minimized,
          x: w.x,
          y: w.y,
          width: typeof w.width === "number" ? w.width : null,
          height: typeof w.height === "number" ? w.height : null,
          browserState: w.browserState || null,
          isWorkBrowser: w.isWorkBrowser || false,
          extra: w.extra || {},
        };
      });
    },

    deserialize: function (windows, opts) {
      opts = opts || {};
      this._windows = windows || [];
      // Ensure every window has numeric width/height (legacy compatibility)
      var cw = this._container ? this._container.clientWidth : 0;
      var ch = this._container ? this._container.clientHeight : 0;
      var defaultW = cw > 100 ? Math.min(800, cw * 0.68) : 800;
      var defaultH = ch > 100 ? Math.min(600, ch * 0.68) : 600;
      this._windows.forEach(function (w) {
        if (typeof w.width !== "number") w.width = defaultW;
        if (typeof w.height !== "number") w.height = defaultH;
        if (typeof w.x !== "number") w.x = 120;
        if (typeof w.y !== "number") w.y = 60;
      });
      if (this._windows.length > 0) {
        var maxId = 0;
        var maxZ = 0;
        this._windows.forEach(function (w) {
          maxId = Math.max(maxId, w.id);
          maxZ = Math.max(maxZ, w.z);
        });
        this._nextId = (opts.nextId || maxId) + 1;
        this._nextZ = maxZ + 1;
        this._activeId = opts.activeId || this._windows[this._windows.length - 1].id;
      } else {
        this._nextId = 1;
        this._nextZ = 1;
        this._activeId = null;
      }
    },

    reset: function () {
      this._windows = [];
      this._nextId = 1;
      this._nextZ = 1;
      this._activeId = null;
    },

    // ── Iframe management ──────────────────────────────────────

    _registerIframe: function (winId, iframe) {
      var bus = this._getBus();
      if (bus && bus.registerAppWindow) {
        bus.registerAppWindow(winId, iframe);
      }
    },

    _unregisterIframe: function (winId) {
      var bus = this._getBus();
      if (bus && bus.unregisterAppWindow) {
        bus.unregisterAppWindow(winId);
      }
    },

    // ── Internal helpers ───────────────────────────────────────

    _find: function (winId) {
      for (var i = 0; i < this._windows.length; i++) {
        if (this._windows[i].id === winId) return this._windows[i];
      }
      return null;
    },

    _findIndex: function (winId) {
      for (var i = 0; i < this._windows.length; i++) {
        if (this._windows[i].id === winId) return i;
      }
      return -1;
    },

    _getBus: function () {
      return (window.QA_OS && window.QA_OS.EventBus) || null;
    },

    _emit: function (event, data) {
      var bus = this._getBus();
      if (bus) bus.emit(event, data);
    },
  };

  window.QA_OS = window.QA_OS || {};
  window.QA_OS.Compositor = C;
})();
