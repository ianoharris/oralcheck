import { notFound } from "next/navigation";

// [locale]/not-found.tsx only renders when a page inside [locale] calls
// notFound(). An address that matched no route at all (/es/no-existe) fell
// through to Next's bare default 404: white page, no nav, Arial. Catching
// every unmatched path here and calling notFound() routes it to the branded
// page instead, inside the site layout and in the visitor's language.
export default function CatchAll() {
  notFound();
}
