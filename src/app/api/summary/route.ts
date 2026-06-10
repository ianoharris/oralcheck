import Anthropic from "@anthropic-ai/sdk";
import { type NextRequest } from "next/server";
import { checkRateLimit, getIp } from "@/lib/rateLimit";

export const runtime = "nodejs";

type SummaryRequest = {
  tier: string;
  tierLabel: string;
  factors: { label: string; answerLabel: string }[];
  hasUrgentSymptom: boolean;
};

export async function POST(req: NextRequest) {
  const { allowed, remaining, resetMs } = checkRateLimit(getIp(req), 10);
  if (!allowed) {
    return new Response(JSON.stringify({ error: "rate_limited" }), {
      status: 429,
      headers: {
        "Content-Type": "application/json",
        "Retry-After": String(Math.ceil(resetMs / 1000)),
        "X-RateLimit-Limit": "10",
        "X-RateLimit-Remaining": "0",
      },
    });
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    return new Response(JSON.stringify({ error: "not_configured" }), {
      status: 503,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const body: SummaryRequest = await req.json();
    const { tier, tierLabel, factors, hasUrgentSymptom } = body;

    const factorLines =
      factors.length > 0
        ? factors.map((f) => `- ${f.label}: ${f.answerLabel}`).join("\n")
        : "- No significant risk factors identified";

    const urgentNote = hasUrgentSymptom
      ? "\nIMPORTANT: The person reported a symptom lasting 2+ weeks, which requires prompt evaluation."
      : "";

    const interactionNote = factors.some(f => f.label === "Tobacco + alcohol interaction")
      ? "\nNote: This person has both tobacco and alcohol use. Their combined risk is multiplicative, not merely additive — approximately 15× baseline, far exceeding the sum of either factor alone (Bagnardi et al., 2015)."
      : "";

    const userMessage = `A person just completed an evidence-based oral cancer risk screener. Here are their results:

Risk tier: ${tierLabel} (${tier})
Contributing factors:
${factorLines}${urgentNote}${interactionNote}

Write a clinically precise, personalized 2–3 sentence summary. Reference specific risk implications for their top factors. If elevated or high tier, mention that oral cancer detected at Stage I has an 84% five-year survival rate versus 38% at Stage IV — that gap is why early action matters. If the tobacco+alcohol interaction is present, note the multiplicative risk. End with one specific, actionable next step. Do not diagnose. No markdown. Plain sentences only.`;

    const client = new Anthropic();

    const stream = await client.messages.stream({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 220,
      system:
        "You are a health educator providing evidence-based oral cancer risk summaries. Be specific and clinically direct — do not soften or vague-ify the science. Reference actual statistics when available (survival rates, odds ratios). Never diagnose or replace professional evaluation. No markdown, no bullet points. Plain sentences only. 2–3 sentences maximum.",
      messages: [{ role: "user", content: userMessage }],
    });

    const encoder = new TextEncoder();
    const readable = new ReadableStream({
      async start(controller) {
        for await (const chunk of stream) {
          if (
            chunk.type === "content_block_delta" &&
            chunk.delta.type === "text_delta"
          ) {
            controller.enqueue(encoder.encode(chunk.delta.text));
          }
        }
        controller.close();
      },
      cancel() {
        stream.abort();
      },
    });

    return new Response(readable, {
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  } catch (err) {
    console.error("[/api/summary] error:", err);
    return new Response(JSON.stringify({ error: "internal" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
