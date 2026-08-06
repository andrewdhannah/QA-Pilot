/**
 * serve.js — minimal local HTTP server for QA Pilot
 *
 * Uses only Node.js built-in modules (http, fs, path, url).
 * No npm install needed. Run via build.bat or the Mac launcher.
 *
 * Serves the QA Pilot root folder on http://127.0.0.1:PORT
 * MIME types cover everything the project uses.
 */

const http = require("http");
const fs   = require("fs");
const path = require("path");
const url  = require("url");

// ── Config ───────────────────────────────────────────────────
const PORT    = process.env.PORT || 8000;
const ROOT    = __dirname;   // folder containing serve.js = QA Pilot root

// ── MIME type map ────────────────────────────────────────────
const MIME = {
    ".html": "text/html; charset=utf-8",
    ".css":  "text/css; charset=utf-8",
    ".js":   "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif":  "image/gif",
    ".svg":  "image/svg+xml",
    ".ico":  "image/x-icon",
    ".woff": "font/woff",
    ".woff2":"font/woff2",
    ".ttf":  "font/ttf",
    ".txt":  "text/plain; charset=utf-8",
    ".pdf":  "application/pdf",
};

// ── Request handler ──────────────────────────────────────────
const server = http.createServer((req, res) => {
    // Parse the URL and decode percent-encoding (spaces in filenames etc.)
    let pathname = url.parse(req.url).pathname;
    pathname = decodeURIComponent(pathname);

    // Default to index.html for directory requests
    if (pathname === "/" || pathname.endsWith("/")) {
        pathname += "index.html";
    }

    // Resolve to an absolute path and make sure it stays inside ROOT
    // (prevents directory traversal attacks — good habit even locally)
    const filePath = path.normalize(path.join(ROOT, pathname));
    if (!filePath.startsWith(ROOT)) {
        res.writeHead(403);
        res.end("Forbidden");
        return;
    }

    fs.readFile(filePath, (err, data) => {
        if (err) {
            if (err.code === "ENOENT") {
                res.writeHead(404, { "Content-Type": "text/plain" });
                res.end(`404 Not Found: ${pathname}`);
            } else {
                res.writeHead(500, { "Content-Type": "text/plain" });
                res.end("500 Internal Server Error");
            }
            return;
        }

        const ext      = path.extname(filePath).toLowerCase();
        const mimeType = MIME[ext] || "application/octet-stream";
        res.writeHead(200, { "Content-Type": mimeType });
        res.end(data);
    });
});

// ── Start ────────────────────────────────────────────────────
server.listen(PORT, "127.0.0.1", () => {
    console.log(`QA Pilot server running at http://127.0.0.1:${PORT}/`);
});

server.on("error", (err) => {
    if (err.code === "EADDRINUSE") {
        console.error(`Port ${PORT} is already in use. Close the other server and try again.`);
    } else {
        console.error("Server error:", err.message);
    }
    process.exit(1);
});
