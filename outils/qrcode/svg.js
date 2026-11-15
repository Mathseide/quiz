// Usage : node svg.js URL  → écrit un SVG du QR code sur la sortie standard
// Bibliothèque QRCode : (c) 2009 Kazuhiko Arase, licence MIT (voir index.js).
const QRCode = require("./index.js");
const QRErrorCorrectLevel = require("./QRErrorCorrectLevel.js");
const q = new QRCode(-1, QRErrorCorrectLevel.M);
q.addData(process.argv[2]); q.make();
const n = q.getModuleCount(), m = 4, t = n + 2 * m;
let d = "";
for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) if (q.isDark(r, c)) d += `M${c + m} ${r + m}h1v1h-1z`;
process.stdout.write(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${t} ${t}" shape-rendering="crispEdges"><rect width="${t}" height="${t}" fill="#fff"/><path d="${d}" fill="#000"/></svg>`);
