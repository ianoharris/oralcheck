import { NextRequest, NextResponse } from "next/server";

const GH_TOKEN = process.env.GITHUB_ACCESS_TOKEN ?? "";
const REPO     = "ianoharris/oralcheck";
const BRANCH   = "master";

async function ghGet(apiPath: string) {
  const res = await fetch(`https://api.github.com/repos/${REPO}/contents/${apiPath}`, {
    headers: {
      Authorization: `Bearer ${GH_TOKEN}`,
      Accept:        "application/vnd.github.v3+json",
    },
  });
  return res.json();
}

async function ghPut(apiPath: string, body: object) {
  return fetch(`https://api.github.com/repos/${REPO}/contents/${apiPath}`, {
    method:  "PUT",
    headers: {
      Authorization:  `Bearer ${GH_TOKEN}`,
      Accept:         "application/vnd.github.v3+json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
}

async function ghDelete(apiPath: string, sha: string, message: string) {
  return fetch(`https://api.github.com/repos/${REPO}/contents/${apiPath}`, {
    method:  "DELETE",
    headers: {
      Authorization:  `Bearer ${GH_TOKEN}`,
      Accept:         "application/vnd.github.v3+json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, sha, branch: BRANCH, committer: { name: "OralCheck Bot", email: "bot@oralcheck.org" } }),
  });
}

export async function POST(req: NextRequest) {
  if (!GH_TOKEN) {
    return NextResponse.json({ error: "GITHUB_ACCESS_TOKEN not configured" }, { status: 500 });
  }

  const { slug } = await req.json() as { slug: string };
  if (!slug) return NextResponse.json({ error: "slug required" }, { status: 400 });

  // Find the draft file by listing content/drafts
  const listRes = await fetch(`https://api.github.com/repos/${REPO}/contents/content/drafts`, {
    headers: { Authorization: `Bearer ${GH_TOKEN}`, Accept: "application/vnd.github.v3+json" },
  });
  const files = await listRes.json() as Array<{ name: string; sha: string }>;
  const draft  = files.find?.((f) => f.name.endsWith(`-${slug}.md`) || f.name === `${slug}.md`);

  if (!draft) return NextResponse.json({ error: `No draft found for slug: ${slug}` }, { status: 404 });

  // Fetch full file content
  const fileData = await ghGet(`content/drafts/${draft.name}`);
  const rawContent: string = fileData.content; // base64, may have newlines

  // Update frontmatter status to "published"
  const decoded   = Buffer.from(rawContent.replace(/\n/g, ""), "base64").toString("utf8");
  const published = decoded.replace(/^status: "draft"$/m, 'status: "published"');
  const encoded   = Buffer.from(published).toString("base64");

  // Create in content/published/
  const createRes = await ghPut(`content/published/${draft.name}`, {
    message:   `publish: ${slug}`,
    content:   encoded,
    branch:    BRANCH,
    committer: { name: "OralCheck Bot", email: "bot@oralcheck.org" },
  });
  if (!createRes.ok) {
    const err = await createRes.json();
    return NextResponse.json({ error: err.message ?? "Failed to create published file" }, { status: 500 });
  }

  // Delete from content/drafts/
  await ghDelete(`content/drafts/${draft.name}`, fileData.sha, `chore: remove published draft ${slug}`);

  return NextResponse.json({ success: true, slug, url: `/learn/${slug}` });
}
