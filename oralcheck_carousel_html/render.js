const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT = path.join(__dirname, 'slides');
fs.mkdirSync(OUT, { recursive: true });

const FONT_DIR = '/Users/ianharris/Desktop/oralcheck/oralcheck-agent/fonts';
const W = 1080, H = 1080;

function base(content) {
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @font-face { font-family: 'DMSerif'; src: url('file://${FONT_DIR}/DMSerifDisplay-Regular.ttf'); }
  @font-face { font-family: 'SourceSans'; src: url('file://${FONT_DIR}/SourceSans3-Regular.ttf'); }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { width: ${W}px; height: ${H}px; overflow: hidden; }
  body { background: #0d1a1b; color: #e8e4de; font-family: 'SourceSans', sans-serif; position: relative; }
</style>
</head>
<body>${content}</body>
</html>`;
}

function pill(text) {
  return `<span style="align-self:flex-start;display:inline-block;font-family:'SourceSans';font-size:17px;letter-spacing:0.12em;text-transform:uppercase;color:#5a7476;background:#162a2c;padding:7px 16px;border-radius:100px;">${text}</span>`;
}

function footer() {
  return `<div style="position:absolute;bottom:0;left:0;right:0;padding:0 64px 36px;display:flex;align-items:center;gap:12px;">
    <div style="width:28px;height:3px;background:#14a8ae;"></div>
    <span style="font-family:'SourceSans';font-size:20px;color:#14a8ae;letter-spacing:0.02em;">oralcheck.org</span>
  </div>`;
}

// showDot=false for decorative background rings — dot only appears on the corner deco
function ringsvg(cx, cy, r1 = 260, r2 = 108, dotAngle = -46, opacity = 1, showDot = false) {
  const ax = cx + (r1 - 38) * Math.cos(dotAngle * Math.PI / 180);
  const ay = cy + (r1 - 38) * Math.sin(dotAngle * Math.PI / 180);
  return `
    <circle cx="${cx}" cy="${cy}" r="${r1}" fill="none" stroke="#162a2c" stroke-width="26" opacity="${opacity}"/>
    <circle cx="${cx}" cy="${cy}" r="${r2}" fill="none" stroke="#162a2c" stroke-width="15" opacity="${opacity}"/>
    ${showDot ? `<circle cx="${ax.toFixed(1)}" cy="${ay.toFixed(1)}" r="22" fill="#e8634a" opacity="${opacity}"/>` : ''}
  `;
}

// Corner decoration — partly off-screen, dot intentionally visible
function cornerRing() {
  return `<svg style="position:absolute;right:-90px;top:-90px;width:400px;height:400px;overflow:visible;" viewBox="0 0 400 400">
    ${ringsvg(320, 80, 220, 90, 210, 0.65, true)}
  </svg>`;
}

// ── SLIDE 1: Hook — World Cup scale comparison ───────────────────────────────
function slide1() {
  return base(`
  <div style="position:absolute;inset:0;display:flex;flex-direction:column;">

    <!-- Top: World Cup crowd — pill absolute, label+number centered -->
    <div style="flex:1;background:#061e20;display:flex;flex-direction:column;justify-content:center;padding:0 68px;position:relative;overflow:hidden;">
      <svg style="position:absolute;right:-50px;top:-30px;width:340px;height:340px;opacity:0.14;" viewBox="0 0 340 340">
        ${ringsvg(260, 90, 200, 82, -46, 1, false)}
      </svg>
      <span style="position:absolute;top:36px;left:68px;display:inline-block;font-family:'SourceSans';font-size:16px;letter-spacing:0.12em;text-transform:uppercase;color:#5a9298;background:#0b2628;padding:6px 14px;border-radius:100px;">World Cup 2026</span>
      <div style="font-family:'SourceSans';font-size:18px;letter-spacing:0.09em;text-transform:uppercase;color:#3d7e84;margin-bottom:6px;">Average stadium crowd per match</div>
      <div style="font-family:'DMSerif';font-size:188px;line-height:0.85;color:#14a8ae;letter-spacing:-0.04em;">65,000</div>
    </div>

    <!-- Divider -->
    <div style="height:3px;background:#0d1a1b;flex-shrink:0;"></div>

    <!-- Bottom: Oral cancer diagnoses — label+number centered, tagline absolute -->
    <div style="flex:1;background:#1a0b09;display:flex;flex-direction:column;justify-content:center;padding:0 68px;position:relative;overflow:hidden;">
      <div style="font-family:'SourceSans';font-size:18px;letter-spacing:0.09em;text-transform:uppercase;color:#7a4038;margin-bottom:6px;">Americans diagnosed with oral cancer this year</div>
      <div style="font-family:'DMSerif';font-size:188px;line-height:0.85;color:#e8634a;letter-spacing:-0.04em;">60,480</div>
      <div style="position:absolute;bottom:36px;left:68px;right:68px;display:flex;align-items:center;gap:12px;">
        <div style="width:28px;height:3px;background:#e8634a;flex-shrink:0;"></div>
        <span style="font-family:'DMSerif';font-size:24px;color:#b05848;">One is on every screen tonight.</span>
      </div>
    </div>

  </div>
  `);
}

// ── SLIDE 2: Not who you think ───────────────────────────────────────────────
function slide2() {
  return base(`
  <div style="position:absolute;inset:0;overflow:hidden;">
    ${cornerRing()}
    <svg style="position:absolute;left:-90px;bottom:-90px;width:400px;height:400px;overflow:visible;" viewBox="0 0 400 400">
      ${ringsvg(80, 320, 220, 90, 30, 0.3, false)}
    </svg>
  </div>

  <div style="position:relative;z-index:1;height:100%;display:flex;flex-direction:column;justify-content:center;padding:0 64px;">
    ${pill('Who It Targets')}

    <div style="margin-top:36px;">
      <div style="font-family:'DMSerif';font-size:100px;line-height:0.95;color:#5a7476;letter-spacing:-0.02em;text-decoration:line-through;text-decoration-color:#e8634a;text-decoration-thickness:5px;">Smokers.</div>
      <div style="margin-top:16px;font-family:'DMSerif';font-size:100px;line-height:0.95;color:#e8e4de;letter-spacing:-0.02em;">People like you.</div>
    </div>

    <div style="margin-top:44px;max-width:860px;">
      <p style="font-family:'SourceSans';font-size:29px;line-height:1.6;color:#8faeb0;">HPV now causes more oral cancers than tobacco. Non-smokers. Under 50. No obvious risk factors.</p>
    </div>

    <div style="margin-top:40px;display:flex;align-items:center;gap:12px;">
      <div style="width:4px;height:36px;background:#e8634a;flex-shrink:0;"></div>
      <span style="font-family:'SourceSans';font-size:19px;letter-spacing:0.06em;color:#7a4a40;">Cases in this group have tripled since the 1980s.</span>
    </div>
  </div>
  ${footer()}
  `);
}

// ── SLIDE 3: Survival Gap ────────────────────────────────────────────────────
function slide3() {
  return base(`
  <div style="position:absolute;inset:0;display:flex;flex-direction:column;">
    <div style="flex:1;background:#0a2224;display:flex;flex-direction:column;justify-content:center;padding:0 64px;position:relative;overflow:hidden;">
      <svg style="position:absolute;right:-50px;top:-40px;width:300px;height:300px;opacity:0.16;" viewBox="0 0 300 300">
        ${ringsvg(240, 70, 190, 78, -46, 1, false)}
      </svg>
      <div style="position:absolute;top:44px;left:64px;">${pill('The Catch')}</div>
      <div style="font-family:'SourceSans';font-size:21px;letter-spacing:0.07em;text-transform:uppercase;color:#3a7074;margin-bottom:4px;margin-top:28px;">Found early</div>
      <div style="font-family:'DMSerif';font-size:196px;line-height:0.85;color:#14a8ae;letter-spacing:-0.04em;">87%</div>
      <div style="font-family:'DMSerif';font-size:50px;color:#e8e4de;margin-top:4px;">survive.</div>
    </div>
    <div style="height:2px;background:#0d1a1b;flex-shrink:0;"></div>
    <div style="flex:1;background:#1c0c0a;display:flex;flex-direction:column;justify-content:center;padding:0 64px;position:relative;overflow:hidden;">
      <svg style="position:absolute;left:-50px;bottom:-40px;width:300px;height:300px;opacity:0.12;" viewBox="0 0 300 300">
        ${ringsvg(60, 230, 190, 78, 135, 1, false)}
      </svg>
      <div style="font-family:'SourceSans';font-size:21px;letter-spacing:0.07em;text-transform:uppercase;color:#6b3028;margin-bottom:4px;">Found late</div>
      <div style="font-family:'DMSerif';font-size:196px;line-height:0.85;color:#e8634a;letter-spacing:-0.04em;">38%</div>
      <div style="font-family:'DMSerif';font-size:50px;color:#e8e4de;margin-top:4px;">survive.</div>
      <div style="position:absolute;bottom:40px;left:64px;font-family:'SourceSans';font-size:22px;color:#4a2820;">Same cancer. Two very different outcomes.</div>
    </div>
  </div>
  `);
}

// ── SLIDE 4: Why It's Missed ─────────────────────────────────────────────────
function slide4() {
  return base(`
  <div style="position:absolute;inset:0;overflow:hidden;">
    <svg style="position:absolute;right:-60px;bottom:-60px;width:520px;height:520px;" viewBox="0 0 520 520">
      ${ringsvg(380, 380, 260, 106, -46, 0.7, false)}
    </svg>
    <svg style="position:absolute;left:-80px;top:-80px;width:380px;height:380px;opacity:0.08;" viewBox="0 0 380 380">
      ${ringsvg(60, 60, 230, 95, 135, 1, false)}
    </svg>
  </div>

  <div style="height:100%;display:flex;flex-direction:column;justify-content:center;padding:0 64px;position:relative;z-index:1;">
    ${pill("Why It's Missed")}
    <div style="margin-top:44px;">
      <div style="font-family:'DMSerif';font-size:112px;line-height:0.95;color:#e8e4de;letter-spacing:-0.02em;">It rarely</div>
      <div style="font-family:'DMSerif';font-size:112px;line-height:0.95;color:#e8634a;letter-spacing:-0.02em;">hurts.</div>
    </div>
    <!-- Flatline: suggests no pain signal until it's too late -->
    <div style="margin-top:28px;">
      <svg width="700" height="38" viewBox="0 0 700 38">
        <polyline points="0,19 100,19 128,4 150,34 172,19 700,19" fill="none" stroke="#1d3a3e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <div style="margin-top:16px;max-width:860px;">
      <p style="font-family:'SourceSans';font-size:30px;line-height:1.6;color:#8faeb0;">Early-stage oral cancer usually has no pain. By the time something feels wrong, it's often Stage III or IV.</p>
    </div>
  </div>
  ${footer()}
  `);
}

// ── SLIDE 5: Solution ────────────────────────────────────────────────────────
function slide5() {
  return base(`
  <div style="position:absolute;inset:0;overflow:hidden;">
    <svg style="position:absolute;right:-60px;bottom:-60px;width:520px;height:520px;" viewBox="0 0 520 520">
      ${ringsvg(380, 380, 240, 98, -46, 0.6, false)}
    </svg>
  </div>

  <div style="height:100%;display:flex;flex-direction:column;justify-content:center;padding:0 64px;position:relative;z-index:1;">
    ${pill("What You Can Do")}

    <div style="margin-top:32px;display:flex;align-items:baseline;gap:16px;">
      <span style="font-family:'DMSerif';font-size:180px;color:#14a8ae;letter-spacing:-0.05em;line-height:0.85;">2</span>
      <span style="font-family:'DMSerif';font-size:64px;color:#e8e4de;letter-spacing:-0.01em;">minutes.</span>
    </div>

    <div style="width:44px;height:3px;background:#14a8ae;margin:28px 0 32px;"></div>

    <div style="display:flex;flex-direction:column;gap:20px;">
      <div style="display:flex;align-items:flex-start;gap:16px;">
        <svg width="34" height="34" viewBox="0 0 34 34" style="flex-shrink:0;margin-top:3px;">
          <circle cx="17" cy="17" r="13" fill="none" stroke="#14a8ae" stroke-width="2"/>
          <polyline points="10,17 15,22 24,11" fill="none" stroke="#14a8ae" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <p style="font-family:'SourceSans';font-size:29px;color:#e8e4de;line-height:1.4;">10 questions about your habits and risk factors.</p>
      </div>
      <div style="display:flex;align-items:flex-start;gap:16px;">
        <svg width="34" height="34" viewBox="0 0 34 34" style="flex-shrink:0;margin-top:3px;">
          <circle cx="17" cy="17" r="13" fill="none" stroke="#1e3e42" stroke-width="1.5"/>
          <polyline points="10,17 15,22 24,11" fill="none" stroke="#1e3e42" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <p style="font-family:'SourceSans';font-size:29px;color:#8faeb0;line-height:1.4;">No account needed.</p>
      </div>
      <div style="display:flex;align-items:flex-start;gap:16px;">
        <svg width="34" height="34" viewBox="0 0 34 34" style="flex-shrink:0;margin-top:3px;">
          <circle cx="17" cy="17" r="13" fill="none" stroke="#1e3e42" stroke-width="1.5"/>
          <polyline points="10,17 15,22 24,11" fill="none" stroke="#1e3e42" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <p style="font-family:'SourceSans';font-size:29px;color:#8faeb0;line-height:1.4;">Nothing stored. Just your result.</p>
      </div>
    </div>
  </div>
  ${footer()}
  `);
}

// ── SLIDE 6: CTA ─────────────────────────────────────────────────────────────
function slide6() {
  return base(`
  <div style="position:absolute;inset:0;overflow:hidden;">
    <svg style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:920px;height:920px;" viewBox="0 0 920 920">
      ${ringsvg(460, 460, 320, 132, -46, 0.85, false)}
      <circle cx="460" cy="460" r="390" fill="none" stroke="#0f2224" stroke-width="1.5"/>
      <circle cx="460" cy="460" r="430" fill="none" stroke="#0c1c1e" stroke-width="1"/>
    </svg>
    <!-- OralCheck logo mark — top-right corner -->
    <svg style="position:absolute;right:44px;top:44px;width:88px;height:88px;" viewBox="0 0 88 88">
      <rect x="0" y="0" width="88" height="88" rx="19" fill="#0d7377"/>
      <circle cx="44" cy="44" r="22" fill="none" stroke="#faf9f6" stroke-width="5.5"/>
      <circle cx="68.8" cy="19.3" r="12" fill="#e8634a"/>
    </svg>
  </div>

  <div style="position:relative;z-index:1;height:100%;display:flex;flex-direction:column;justify-content:center;padding:0 64px;">
    <div style="font-family:'DMSerif';font-size:124px;line-height:0.95;letter-spacing:-0.03em;color:#e8e4de;">Free.</div>
    <div style="font-family:'DMSerif';font-size:124px;line-height:0.95;letter-spacing:-0.03em;color:#14a8ae;">Private.</div>
    <div style="font-family:'DMSerif';font-size:96px;line-height:0.95;letter-spacing:-0.03em;color:#e8e4de;margin-bottom:52px;">2 minutes.</div>

    <p style="font-family:'SourceSans';font-size:28px;color:#8faeb0;margin-bottom:36px;">Take the free oral cancer risk screener.</p>

    <div style="display:flex;align-items:center;">
      <div style="width:4px;height:50px;background:#e8634a;margin-right:16px;"></div>
      <span style="font-family:'SourceSans';font-size:42px;color:#14a8ae;letter-spacing:0.01em;">oralcheck.org</span>
    </div>
  </div>
  `);
}

const slides = [
  { id: '01_hook',     html: slide1() },
  { id: '02_numbers',  html: slide2() },
  { id: '03_survival', html: slide3() },
  { id: '04_silent',   html: slide4() },
  { id: '05_solution', html: slide5() },
  { id: '06_cta',      html: slide6() },
];

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: W, height: H },
    deviceScaleFactor: 2,
  });
  const page = await context.newPage();

  for (const { id, html } of slides) {
    const tmpPath = path.join(__dirname, `_tmp_${id}.html`);
    fs.writeFileSync(tmpPath, html, 'utf8');
    await page.goto(`file://${tmpPath}`);
    await page.waitForTimeout(400);
    const out = path.join(OUT, `${id}.jpg`);
    await page.screenshot({ path: out, type: 'jpeg', quality: 97 });
    fs.unlinkSync(tmpPath);
    console.log(`✓ ${out}`);
  }

  await browser.close();
  console.log(`\nAll ${slides.length} slides → ${OUT}/`);
})();
