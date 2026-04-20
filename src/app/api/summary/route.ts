import Anthropic from "@anthropic-ai/sdk";
import { type NextRequest } from "next/server";

export const runtime = "nodejs";

type SummaryRequest = {
  tier: string;
  tierLabel: string;
  factors: { label: string; answerLabel: string }[];
  hasUrgentSymptom: boolean;
};

export async function POST(req: NextRequest) {
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

    const userMessage = `A person just completed an oral cancer risk screener. Here are their results:

Risk tier: ${tierLabel} (${tier})
Contributing factors:
${factorLines}${urgentNote}

Write a warm, personalized 2–3 sentence summary of their results. Be specific about their factors. End with one clear, actionable next step. Do not diagnose. Do not use markdown. Plain sentences only.`;

    const client = new Anthropic();

    const stream = await client.messages.stream({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 200,
      system:
        "You are a health educator helping people understand their oral cancer risk. Write in plain, warm, human language. Never diagnose or replace medical advice. Always encourage consulting a health professional. Keep responses to 2–3 sentences maximum.",
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
