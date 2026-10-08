import type { ReactNode } from "react";

// Rich-text handlers for the learn pages' "Sources" boxes. A figure quoted in the
// page body gets its primary source linked here, by tag name in the message
// (e.g. <hashibe>...</hashibe>), so the link survives translation.
const SOURCE_URLS = {
  // Pooled INHANCE analysis, 17 studies. Oral cavity, >20 cigarettes and
  // >=3 drinks a day vs neither: OR 15.49 (Table 3).
  hashibe: "https://pubmed.ncbi.nlm.nih.gov/19190158/",
  // MeSH scope note for aphthous stomatitis: lesions last 7 to 14 days.
  mesh: "https://meshb.nlm.nih.gov/record/ui?ui=D013281",
  // NHS: mouth ulcers "should clear up on their own within a week or 2".
  nhs: "https://www.nhs.uk/conditions/mouth-ulcers/",
} as const;

export const sourceLinks = Object.fromEntries(
  Object.entries(SOURCE_URLS).map(([tag, href]) => [
    tag,
    (chunks: ReactNode) => (
      <a href={href} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:text-ink">
        {chunks}
      </a>
    ),
  ]),
) as Record<keyof typeof SOURCE_URLS, (chunks: ReactNode) => ReactNode>;
