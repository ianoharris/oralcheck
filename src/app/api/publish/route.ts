import { NextRequest, NextResponse } from "next/server";
import { requireAdmin } from "@/lib/adminAuth";
import { checkRateLimit, getIp } from "@/lib/rateLimit";

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
  // Auth first, before anything observable. Answering "slug required" to an
  // unauthenticated caller confirmed both that the route exists and that it was
  // ungated, which is how this was found.
  const auth = requireAdmin(req);
  if (!auth.ok) {
    return NextResponse.json({ error: auth.error }, { status: auth.status });
  }
  // Publishing writes to a git repo. Even authenticated, it should not be
  // possible to run it in a loop.
  const { allowed } = checkRateLimit(`publish:${getIp(req)}`, 10, 60 * 60 * 1000);
  if (!allowed) {
    return NextResponse.json({ error: "Too many publish attempts" }, { status: 429 });
  }

  // Validate the input before looking at server config, so a malformed request
  // is rejected the same way whether or not the deploy is fully set up.
  let slug: string;
  try {
    ({ slug } = await req.json() as { slug: string });
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }
  if (!slug) return NextResponse.json({ error: "slug required" }, { status: 400 });
  // The draft is matched against a real directory listing below, so a slug
  // cannot traverse out of content/drafts. Reject the obvious shapes anyway:
  // the check is cheap and the matching logic is not the only thing that could
  // ever consume this value.
  if (!/^[a-z0-9][a-z0-9-]{0,80}$/.test(slug)) {
    return NextResponse.json({ error: "invalid slug" }, { status: 400 });
  }

  if (!GH_TOKEN) {
    return NextResponse.json({ error: "GITHUB_ACCESS_TOKEN not configured" }, { status: 500 });
  }

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

  // Best-effort: promote the Spanish translation alongside it, if the SEO
  // pipeline generated one (content/drafts/es/<same filename>). Its absence
  // (older drafts, or a translation that failed) is not an error — the
  // English article ships regardless, and the site falls back to English
  // for /es/learn/<slug> until a translation exists.
  try {
    const esFileData = await ghGet(`content/drafts/es/${draft.name}`);
    if (esFileData && !esFileData.message && esFileData.content) {
      const esPublished = esFileData.content; // already base64, status line differs only in the copy we already translated
      const esCreateRes = await ghPut(`content/published/es/${draft.name}`, {
        message:   `publish: ${slug} (es)`,
        content:   esPublished,
        branch:    BRANCH,
        committer: { name: "OralCheck Bot", email: "bot@oralcheck.org" },
      });
      if (esCreateRes.ok) {
        await ghDelete(`content/drafts/es/${draft.name}`, esFileData.sha, `chore: remove published draft ${slug} (es)`);
      }
    }
  } catch {
    // no Spanish draft present — fine, English-only publish proceeds
  }

  return NextResponse.json({ success: true, slug, url: `/learn/${slug}` });
}
