(function () {
  var E = {

    // Internal pub/sub
    _listeners: {},

    on: function (event, callback, ctx) {
      (this._listeners[event] = this._listeners[event] || []).push({ fn: callback, ctx: ctx || null });
    },

    off: function (event, callback) {
      var list = this._listeners[event];
      if (!list) return;
      this._listeners[event] = list.filter(function (e) { return e.fn !== callback; });
    },

    emit: function (event, data) {
      var list = this._listeners[event];
      if (!list) return;
      for (var i = 0; i < list.length; i++) {
        try { list[i].fn.call(list[i].ctx || null, data); } catch (e) { console.warn("EventBus[" + event + "]", e); }
      }
    },

    // App iframe postMessage management
    _appWindows: {},

    registerAppWindow: function (winId, iframe) {
      this._appWindows[winId] = iframe;
    },

    unregisterAppWindow: function (winId) {
      delete this._appWindows[winId];
    },

    getAppWindow: function (winId) {
      return this._appWindows[winId] || null;
    },

    postToApp: function (winId, msg) {
      var iframe = this._appWindows[winId];
      if (!iframe || !iframe.contentWindow) return false;
      try {
        iframe.contentWindow.postMessage(msg, "*");
        return true;
      } catch (e) {
        return false;
      }
    },

    postToAllApps: function (msg) {
      for (var id in this._appWindows) {
        if (this._appWindows.hasOwnProperty(id)) {
          var iframe = this._appWindows[id];
          if (iframe && iframe.contentWindow) {
            try { iframe.contentWindow.postMessage(msg, "*"); } catch (e) {}
          }
        }
      }
    },

    // App message handlers (type -> [callbacks])
    _appMsgHandlers: {},

    onAppMessage: function (type, handler) {
      (this._appMsgHandlers[type] = this._appMsgHandlers[type] || []).push(handler);
    },

    offAppMessage: function (type, handler) {
      var list = this._appMsgHandlers[type];
      if (!list) return;
      this._appMsgHandlers[type] = list.filter(function (h) { return h !== handler; });
    },

    _handleAppMessage: function (event) {
      var msg = event.data;
      if (!msg || !msg.type) return;
      var handlers = this._appMsgHandlers[msg.type];
      if (handlers) {
        for (var i = 0; i < handlers.length; i++) {
          try { handlers[i](msg, event); } catch (e) { console.warn("EventBus.appMsg[" + msg.type + "]", e); }
        }
      }
      // Also emit as a regular event
      this.emit("app:" + msg.type, msg);
    },

    initAppMessaging: function () {
      var self = this;
      window.addEventListener("message", function (event) {
        self._handleAppMessage(event);
      });
    },

    // Queue messages for iframes that haven't loaded yet
    _msgQueues: {},

    queueForApp: function (winId, msg) {
      (this._msgQueues[winId] = this._msgQueues[winId] || []).push(msg);
    },

    flushQueue: function (winId) {
      var queue = this._msgQueues[winId];
      if (!queue) return;
      var iframe = this._appWindows[winId];
      if (!iframe || !iframe.contentWindow) return;
      for (var i = 0; i < queue.length; i++) {
        try { iframe.contentWindow.postMessage(queue[i], "*"); } catch (e) {}
      }
      delete this._msgQueues[winId];
    },

  };

  window.QA_OS = window.QA_OS || {};
  window.QA_OS.EventBus = E;
})();
