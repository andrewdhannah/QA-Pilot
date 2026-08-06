// gen-sprites.js — generates placeholder sprite strip PNGs
// Run: node tools/gen-sprites.js
// Replace the output PNGs with real cropped sprites when available.

const fs = require("fs");
const zlib = require("zlib");
const path = require("path");

const OUT_DIR = path.join(__dirname, "..", "videos");
fs.mkdirSync(OUT_DIR, { recursive: true });

const SPRITES = [
  { name: "ai_influencer_strip.png",    r: 220, g: 40,  b: 40,  label: "AI" },
  { name: "tutorial_guy_strip.png",     r: 30,  g: 120, b: 210, label: "TUT" },
  { name: "corporate_ai_demo_strip.png", r: 200, g: 160, b: 20,  label: "DEMO" },
  { name: "infinite_buffering_strip.png", r: 100, g: 40, b: 140, label: "BUF" },
];

// PNG helpers — write raw PNG with zlib-compressed IDAT
function crc32(buf) {
  var crc = 0xffffffff;
  for (var i = 0; i < buf.length; i++) {
    crc ^= buf[i];
    for (var j = 0; j < 8; j++) {
      crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function pngChunk(type, data) {
  var len = Buffer.alloc(4);
  len.writeUInt32BE(data.length);
  var typeB = Buffer.from(type, "ascii");
  var crcBuf = Buffer.concat([typeB, data]);
  var crcVal = crc32(crcBuf);
  var crc = Buffer.alloc(4);
  crc.writeUInt32BE(crcVal);
  return Buffer.concat([len, typeB, data, crc]);
}

function makePNG(w, h, pixels) {
  // pixels: flat array of [R,G,B] triples (w * h * 3 values)
  var sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

  var ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8;  // bit depth
  ihdr[9] = 2;  // color type: RGB
  ihdr[10] = 0; // compression
  ihdr[11] = 0; // filter
  ihdr[12] = 0; // interlace

  // Raw data with filter byte (0 = None) per row
  var raw = Buffer.alloc(h * (1 + w * 3));
  for (var row = 0; row < h; row++) {
    raw[row * (1 + w * 3)] = 0; // filter: None
    for (var col = 0; col < w; col++) {
      var srcIdx = (row * w + col) * 3;
      var dstIdx = row * (1 + w * 3) + 1 + col * 3;
      raw[dstIdx] = pixels[srcIdx];
      raw[dstIdx + 1] = pixels[srcIdx + 1];
      raw[dstIdx + 2] = pixels[srcIdx + 2];
    }
  }

  var compressed = zlib.deflateSync(raw);
  return Buffer.concat([
    sig,
    pngChunk("IHDR", ihdr),
    pngChunk("IDAT", compressed),
    pngChunk("IEND", Buffer.alloc(0)),
  ]);
}

// Generate each sprite strip
SPRITES.forEach(function (s) {
  var W = 128, H = 72, FRAMES = 8;
  var stripH = H * FRAMES;
  var pixels = new Uint8Array(W * stripH * 3);

  for (var frame = 0; frame < FRAMES; frame++) {
    var yOff = frame * H;
    for (var y = 0; y < H; y++) {
      for (var x = 0; x < W; x++) {
        var idx = ((yOff + y) * W + x) * 3;
        // Animate across frame: shift hue bar
        var barPos = ((x + frame * 16) % W);
        var isBar = barPos < 6;
        var border = (y < 2 || y >= H - 2 || x < 2 || x >= W - 2);

        if (border) {
          pixels[idx] = 255;
          pixels[idx+1] = 255;
          pixels[idx+2] = 255;
        } else if (isBar) {
          // Scanning highlight bar
          var bright = Math.min(255, s.r + 60);
          pixels[idx] = bright;
          pixels[idx+1] = Math.min(255, s.g + 60);
          pixels[idx+2] = Math.min(255, s.b + 60);
        } else {
          // Base color with subtle gradient
          var gradient = 1 - (y / H) * 0.3;
          pixels[idx] = Math.min(255, Math.round(s.r * gradient + (s.r > 128 ? 20 : -20)));
          pixels[idx+1] = Math.min(255, Math.round(s.g * gradient + (s.g > 128 ? 20 : -20)));
          pixels[idx+2] = Math.min(255, Math.round(s.b * gradient));
        }
      }
    }
  }

  var png = makePNG(W, stripH, pixels);
  var outPath = path.join(OUT_DIR, s.name);
  fs.writeFileSync(outPath, png);
  console.log("✓", s.name, "(" + W + "x" + stripH + ", " + png.length + " bytes)");
});

console.log("\nDone. Placeholder sprites generated in", OUT_DIR);
console.log("Replace them with real cropped sprites when available.");
