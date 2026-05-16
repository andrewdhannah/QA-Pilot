(function () {
  var DB_NAME = "qa-workspaces";
  var DB_VERSION = 1;
  var STORE_NAME = "workspaces";
  var AUTO_SAVE_KEY = "__auto__";
  var MAX_AUTO_SAVES = 10;

  var _db = null;

  function _openDB() {
    return new Promise(function (resolve, reject) {
      if (_db) { resolve(_db); return; }
      var req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = function (e) {
        var db = e.target.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          var store = db.createObjectStore(STORE_NAME, { keyPath: "name" });
          store.createIndex("timestamp", "timestamp", { unique: false });
          store.createIndex("type", "type", { unique: false });
        }
      };
      req.onsuccess = function (e) {
        _db = e.target.result;
        resolve(_db);
      };
      req.onerror = function (e) {
        reject(e.target.error);
      };
    });
  }

  function _put(name, data, type) {
    return _openDB().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(STORE_NAME, "readwrite");
        var store = tx.objectStore(STORE_NAME);
        var record = {
          name: name,
          type: type || "manual",
          timestamp: Date.now(),
          data: data,
        };
        var req = store.put(record);
        req.onsuccess = function () { resolve(record); };
        req.onerror = function () { reject(req.error); };
      });
    });
  }

  function _get(name) {
    return _openDB().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(STORE_NAME, "readonly");
        var store = tx.objectStore(STORE_NAME);
        var req = store.get(name);
        req.onsuccess = function () { resolve(req.result ? req.result.data : null); };
        req.onerror = function () { reject(req.error); };
      });
    });
  }

  function _getAll(type) {
    return _openDB().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(STORE_NAME, "readonly");
        var store = tx.objectStore(STORE_NAME);
        var req;
        if (type) {
          var idx = store.index("type");
          req = idx.getAll(type);
        } else {
          req = store.getAll();
        }
        req.onsuccess = function () {
          var results = req.result || [];
          results.sort(function (a, b) { return b.timestamp - a.timestamp; });
          resolve(results);
        };
        req.onerror = function () { reject(req.error); };
      });
    });
  }

  function _delete(name) {
    return _openDB().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(STORE_NAME, "readwrite");
        var store = tx.objectStore(STORE_NAME);
        var req = store.delete(name);
        req.onsuccess = function () { resolve(true); };
        req.onerror = function () { reject(req.error); };
      });
    });
  }

  var W = {

    isAvailable: function () {
      return !!window.indexedDB;
    },

    save: function (name, state) {
      return _put(name, state, "manual");
    },

    restore: function (name) {
      return _get(name);
    },

    list: function () {
      return _getAll().then(function (records) {
        return records.map(function (r) {
          return { name: r.name, type: r.type, timestamp: r.timestamp };
        });
      });
    },

    delete: function (name) {
      return _delete(name);
    },

    // Auto-save snapshots
    autoSave: function (state) {
      var self = this;
      return _put(AUTO_SAVE_KEY, state, "auto").then(function () {
        return _getAll("auto").then(function (records) {
          if (records.length > MAX_AUTO_SAVES) {
            var toDelete = records.slice(MAX_AUTO_SAVES);
            return Promise.all(toDelete.map(function (r) { return _delete(r.name); }));
          }
        });
      });
    },

    restoreAutoSave: function () {
      return _get(AUTO_SAVE_KEY);
    },

    getAutoSaves: function () {
      return _getAll("auto").then(function (records) {
        return records.map(function (r) {
          return { name: r.name, type: r.type, timestamp: r.timestamp };
        });
      });
    },

  };

  window.QA_OS = window.QA_OS || {};
  window.QA_OS.Workspaces = W;
})();
