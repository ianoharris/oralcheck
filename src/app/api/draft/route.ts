import { NextRequest, NextResponse } from "next/server";
import { getDraftArticle } from "@/lib/articles";

export async function GET(req: NextRequest) {
  const slug = req.nextUrl.searchParams.get("slug");
  if (!slug) return NextResponse.json({ error: "slug required" }, { status: 400 });

  const article = getDraftArticle(slug);
  if (!article) return NextResponse.json({ error: "Draft not found" }, { status: 404 });

  return NextResponse.json({ article });
}
