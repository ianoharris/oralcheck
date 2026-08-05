import { NextRequest, NextResponse } from "next/server";
import { Resend } from "resend";
import { checkRateLimit, getIp } from "@/lib/rateLimit";
import { computeRisk, type Answers, type RiskTier } from "@/lib/riskEngine";

// Lazy init so a missing key at build time doesn't break static analysis.
function getResend() {
  return new Resend(process.env.RESEND_API_KEY);
}

// Sending to arbitrary users requires a verified domain in Resend. Set
// RESEND_FROM="OralCheck <noreply@oralcheck.org>" once oralcheck.org is verified;
// until then the resend.dev sender can only deliver to your own Resend account.
const FROM = process.env.RESEND_FROM || "OralCheck <onboarding@resend.dev>";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const stepsByTier: Record<RiskTier, string[]> = {
  low: [
    "Keep your annual dental visit — the oral cancer screening is already part of a routine cleaning.",
    "Do a 2-minute self-exam once a month. You're watching for anything that hasn't gone away after 2 weeks.",
    "Re-check your risk in about 6 months, or sooner if anything changes.",
  ],
  moderate: [
    "Mention your risk factors at your next dental visit so your provider screens with them in mind.",
    "Anything in your mouth or throat lasting more than 2 weeks deserves a professional look. Don't wait it out.",
    "Several factors that raised your score are modifiable — small changes lower risk over time.",
    "Re-check your risk in about 6 months.",
  ],
  elevated: [
    "Book a dental visit and specifically ask for an oral cancer screening.",
    "Do a self-exam now, and again monthly. Report anything that persists beyond 2 weeks.",
    "Address the modifiable factors driving your score — tobacco and alcohol reduction have the largest effect.",
    "Re-check your risk in a few months as things change.",
  ],
  high: [
    "Book a dental or medical visit this week and ask directly for an oral cancer screening.",
    "If you have a sore, patch, or lump that has lasted 2+ weeks, mention it specifically when you call.",
    "Find affordable care near you at oralcheck.org/find-care if cost is a barrier.",
    "Re-check your risk after you've been seen.",
  ],
};

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function buildEmailHtml(result: ReturnType<typeof computeRisk>): string {
  const topFactors = result.factors
    .slice(0, 3)
    .map((f) => `<li style="margin:4px 0;">${esc(f.label)}</li>`)
    .join("");
  const steps = stepsByTier[result.tier]
    .map((s) => `<li style="margin:8px 0;line-height:1.5;">${esc(s)}</li>`)
    .join("");

  return `<!doctype html><html><body style="margin:0;background:#f4f1ea;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:#14201f;">
  <div style="max-width:560px;margin:0 auto;padding:32px 24px;">
    <div style="font-size:20px;font-weight:700;color:#0d7377;">● OralCheck</div>
    <h1 style="font-family:Georgia,serif;font-size:26px;line-height:1.25;margin:24px 0 8px;">${esc(result.headline)}</h1>
    <p style="font-size:15px;line-height:1.6;color:#3f5453;margin:0 0 20px;">${esc(result.summary)}</p>
    <div style="background:#fff;border:1px solid #ded7c8;border-radius:16px;padding:18px 20px;margin:0 0 20px;">
      <div style="font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:#7c8b8a;">Top factors in your result</div>
      <ul style="margin:8px 0 0;padding-left:18px;font-size:15px;color:#14201f;">${topFactors}</ul>
    </div>
    <div style="font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:#7c8b8a;margin:0 0 6px;">Your next steps</div>
    <ul style="margin:0 0 24px;padding-left:18px;font-size:15px;color:#14201f;">${steps}</ul>
    <a href="https://oralcheck.org/find-care" style="display:inline-block;background:#0d7377;color:#fff;text-decoration:none;font-weight:600;padding:12px 22px;border-radius:12px;">Find affordable care near you →</a>
    <p style="font-size:12px;color:#7c8b8a;line-height:1.6;margin:28px 0 0;border-top:1px solid #ded7c8;padding-top:16px;">
      OralCheck is an educational risk tool, not a medical diagnosis. Always consult a dental or medical provider about any oral health concern. You received this because you asked for a copy of your result at oralcheck.org. We don't store your answers or add you to any list.
    </p>
  </div></body></html>`;
}

export async function POST(req: NextRequest) {
  const { allowed } = checkRateLimit(getIp(req), 3, 60 * 60 * 1000); // 3/hr
  if (!allowed) {
    return NextResponse.json({ error: "Too many requests." }, { status: 429 });
  }

  let body: { email?: string; answers?: Answers };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid request." }, { status: 400 });
  }

  const email = (body.email || "").trim();
  if (!EMAIL_RE.test(email) || email.length > 254) {
    return NextResponse.json({ error: "Please enter a valid email." }, { status: 400 });
  }
  if (!body.answers || typeof body.answers !== "object" || Array.isArray(body.answers)) {
    return NextResponse.json({ error: "No screener result to send." }, { status: 400 });
  }

  let result: ReturnType<typeof computeRisk>;
  try {
    result = computeRisk(body.answers); // recompute server-side: authoritative, not client-tampered
  } catch {
    return NextResponse.json({ error: "Couldn't read that result." }, { status: 400 });
  }

  try {
    await getResend().emails.send({
      from: FROM,
      to: email,
      subject: "Your OralCheck result and next steps",
      html: buildEmailHtml(result),
    });
    return NextResponse.json({ ok: true });
  } catch (e) {
    console.error("[email-result] send failed:", e);
    return NextResponse.json({ error: "Couldn't send right now. Try again." }, { status: 500 });
  }
}
