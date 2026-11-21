// The mouth's lining in section, shared by the cell-scale Mouth Notes episodes
// (lifecell, microscope, tobaccodna). An illustration in the house colours,
// not a histology slide: round cells at the bottom (basal layer) on a wavy
// floor (the basement membrane), flattening towards the surface.
//
// makeLining(parent, {cols, rows, x0, x1, floor, top}) draws a fixed sheet and
// returns {cells: [{el, nuc, row, col, x, y, w, h}], floorPath}. Scenes recolour
// cells by row and column as a pure function of t.
const NS = "http://www.w3.org/2000/svg";
export const el = (tag, attrs, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; };
export const lerp = (a, b, k) => a + (b - a) * k;
export const PINK = "#f1c9cf", PINK_D = "#b86a78", NUC = "#c98593", TEAL = "#0d7377", CORAL = "#e8634a";
export const mix = (a, b, k) => { const h = s => [1, 3, 5].map(i => parseInt(s.slice(i, i + 2), 16));
  const A = h(a), B = h(b); return `rgb(${A.map((v, j) => Math.round(lerp(v, B[j], k))).join(",")})`; };

export function floorY(x, floor) { return floor + 22 * Math.sin(x / 48); }

export function makeLining(parent, {cols = 14, rows = 9, x0 = -40, x1 = 1120, floor = 800, top = 300, seed = 3} = {}) {
  let s = seed; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const g = el("g", {}, parent);
  el("rect", {x: x0 - 200, y: floor, width: x1 - x0 + 400, height: 700, fill: "#f7e6e3"}, g);   // tissue beneath
  const pts = []; for (let x = x0 - 200; x <= x1 + 200; x += 12) pts.push(`${x},${floorY(x, floor).toFixed(1)}`);
  const floorPath = el("path", {d: "M" + pts.join(" L"), fill: "none", stroke: PINK_D, "stroke-width": 5}, g);
  const cells = [];
  const rowH = (floor - top) / rows;
  for (let r = 0; r < rows; r++) {
    const k = r / (rows - 1);                          // 0 at the floor, 1 at the surface
    const w = lerp((x1 - x0) / cols, (x1 - x0) / cols * 1.9, k), h = lerp(rowH * 0.95, rowH * 0.42, k);
    for (let x = x0 + (r % 2) * w / 2; x < x1; x += w) {
      const cx = x + w / 2 + (rnd() - .5) * 6;
      const cy = (r === 0 ? floorY(cx, floor) - h / 2 - 4 : floor - rowH * (r + 0.5)) + (rnd() - .5) * 5;
      const e = el("ellipse", {cx, cy, rx: w / 2 - 2, ry: h / 2, fill: PINK, stroke: PINK_D, "stroke-width": 2}, g);
      const n = el("ellipse", {cx, cy, rx: lerp(10, 6, k), ry: lerp(10, 3.5, k), fill: NUC}, g);
      cells.push({el: e, nuc: n, row: r, k, x: cx, y: cy, w, h});
    }
  }
  return {g, cells, floorPath, rowH};
}
