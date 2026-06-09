import { NextRequest, NextResponse } from "next/server";
import { Resend } from "resend";
import { checkRateLimit, getIp } from "@/lib/rateLimit";

// Lazy init so missing key at build time doesn't break static analysis
function getResend() {
  return new Resend(process.env.RESEND_API_KEY);
}

export async function POST(req: NextRequest) {
  const ip = getIp(req);
  const { allowed } = checkRateLimit(ip, 3, 60 * 60 * 1000); // 3 per hour
  if (!allowed) {
    return NextResponse.json({ error: "Too many requests." }, { status: 429 });
  }

  let body: { message?: string; email?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid request." }, { status: 400 });
  }

  const { message, email } = body;

  if (!message || message.trim().length < 5) {
    return NextResponse.json({ error: "Message is too short." }, { status: 400 });
  }

  if (message.trim().length > 2000) {
    return NextResponse.json({ error: "Message is too long." }, { status: 400 });
  }

  try {
    const resend = getResend();
    await resend.emails.send({
      from: "OralCheck Feedback <onboarding@resend.dev>",
      to: "ianoharris321@gmail.com",
      subject: email ? `OralCheck feedback from ${email}` : "OralCheck anonymous feedback",
      text: [
        email ? `From: ${email}` : "From: Anonymous",
        "",
        message.trim(),
      ].join("\n"),
    });

    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ error: "Failed to send. Please try again." }, { status: 500 });
  }
}
