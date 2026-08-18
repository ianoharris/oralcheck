import { NextRequest, NextResponse } from "next/server";
import { getDraftArticle } from "@/lib/articles";
import { requireAdmin } from "@/lib/adminAuth";

export async function GET(req: NextRequest) {
  // Drafts are unreviewed medical content. Serving them to anyone who guesses a
  // slug published them in practice, just without the git commit.
  const auth = requireAdmin(req);
  if (!auth.ok) {
    return NextResponse.json({ error: auth.error }, { status: auth.status });
  }

  const slug = req.nextUrl.searchParams.get("slug");
  if (!slug) return NextResponse.json({ error: "slug required" }, { status: 400 });
  if (!/^[a-z0-9][a-z0-9-]{0,80}$/.test(slug)) {
    return NextResponse.json({ error: "invalid slug" }, { status: 400 });
  }

  const article = getDraftArticle(slug);
  if (!article) return NextResponse.json({ error: "Draft not found" }, { status: 404 });

  return NextResponse.json({ article });
}
