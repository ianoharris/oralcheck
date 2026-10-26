// OralCheck house animation style: the frame around the stage, shared by
// every animated reel. anim.py serves a scene page with window.PLAN set; the
// scene draws the stage and calls House.frame(t) for everything else.
//
// PLAN = {shots: [{key, t0, len, words: [{text, start}]}], cta_t0, credit, foot, foot_on: [keys]}
// Everything is a pure function of t, so frames line up with the narration.

export const ease = x => x <= 0 ? 0 : x >= 1 ? 1 : 1 - Math.pow(1 - x, 4);       // ease-out quart
export const smooth = x => x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x);
export const span = (t, a, b) => smooth((t - a) / (b - a));
export const lerp = (a, b, k) => a + (b - a) * k;
const $ = id => document.getElementById(id);

const UI = `
<div id="ui">
  <div class="brand"><span class="dot"></span>OralCheck</div>
  <div id="eyebrow"></div>
  <svg id="lead"><line id="ln" stroke="#0d7377" stroke-width="2" stroke-linecap="round"/><circle id="lc" r="7" fill="#0d7377"/></svg>
  <div id="label"><div class="k" id="lk"></div><div class="t" id="lt"></div><div class="d" id="ld"></div></div>
  <div id="tap"></div>
  <div id="readout"><div class="v" id="rv"></div><div class="u" id="ru"></div><div class="bar" id="rb"></div></div>
  <div id="cap"></div>
  <div class="scrub"><i id="scrub"></i></div>
  <div id="foot"></div>
  <div id="credit"></div>
  <div id="cta"><div class="k">Free, private, no account</div><div class="h">Check your risk in two minutes.</div>
    <div class="u">oralcheck.org</div><div class="s">A risk check, not a diagnosis. A sore that lasts two weeks still means a dentist.</div></div>
</div>`;

export const PLAN = window.PLAN;
document.body.insertAdjacentHTML("beforeend", UI);
$("credit").textContent = PLAN.credit || "";
$("foot").textContent = PLAN.foot || "";

/** The shot at time t: {i, sh, prev, local, k} where k runs 0..1 through the shot. */
export function at(t) {
  const shots = PLAN.shots;
  let i = shots.length - 1; while (i > 0 && t < shots[i].t0) i--;
  const sh = shots[i];
  return {i, sh, prev: shots[i - 1], local: t - sh.t0, k: (t - sh.t0) / sh.len};
}
/** Time at which shot `key` starts (Infinity if absent): scenes key their motion to it. */
export const startOf = key => (PLAN.shots.find(s => s.key === key) || {t0: Infinity}).t0;

/** A label with a leader line from (x, y) on screen; side "left" or "right". `local` is seconds into the shot. */
export function label(text, x, y, side, local, top = 300) {
  const lab = $("label");
  if (!text) { lab.style.opacity = $("ln").style.opacity = $("lc").style.opacity = $("tap").style.opacity = 0; return; }
  $("lk").textContent = text.k || ""; $("lt").textContent = text.t || ""; $("ld").textContent = text.d || "";
  const lw = lab.offsetWidth, lx = side === "left" ? 60 : 1080 - 60 - lw;
  lab.style.left = lx + "px"; lab.style.top = top + "px"; lab.style.opacity = span(local, 0.75, 1.25);
  const ax = side === "left" ? lx + lw : lx, ay = top + lab.offsetHeight / 2, draw = span(local, 0.55, 1.05);
  $("ln").setAttribute("x1", x); $("ln").setAttribute("y1", y);
  $("ln").setAttribute("x2", lerp(x, ax, draw)); $("ln").setAttribute("y2", lerp(y, ay, draw));
  $("ln").style.opacity = $("lc").style.opacity = draw > 0 ? 1 : 0;
  $("lc").setAttribute("cx", x); $("lc").setAttribute("cy", y);
  const rk = span(local, 0.3, 1.0);
  $("tap").style.left = x + "px"; $("tap").style.top = y + "px";
  $("tap").style.opacity = local > 0.3 ? 1 - rk : 0; $("tap").style.transform = `scale(${1 + rk * 2.2})`;
}

/** The readout: a value, its unit, and a bar `bar` pixels long (0 hides it). */
export function readout(value, unit, bar, opacity) {
  $("rv").textContent = value; $("ru").textContent = unit;
  $("rb").style.width = (bar || 0) + "px"; $("rb").style.display = bar ? "block" : "none";
  $("readout").style.opacity = opacity;
}

/** Chrome, captions, progress, footers and the end card. Call last in render(t). */
export function frame(t) {
  const {sh} = at(t);
  $("eyebrow").textContent = sh.eyebrow || "";
  $("cap").innerHTML = (sh.words || []).map(w => `<span class="${t >= w.start ? "on" : ""}">${w.text}</span>`).join(" ");
  $("scrub").style.width = Math.min(100, t / PLAN.cta_t0 * 100).toFixed(2) + "%";
  $("foot").style.opacity = (PLAN.foot_on || []).includes(sh.key) ? span(t - sh.t0, 0.3, 0.8) : 0;
  const ck = span(t, PLAN.cta_t0, PLAN.cta_t0 + 0.7);
  $("cta").style.opacity = ck; $("cta").style.transform = `translateY(${(1 - ck) * 24}px)`;
  $("cap").style.opacity = 1 - ck;
  for (const id of ["cap", "scrub", "eyebrow", "readout"]) $(id).style.visibility = ck > 0.6 ? "hidden" : "visible";
  return true;
}
