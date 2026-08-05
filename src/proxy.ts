import createMiddleware from "next-intl/middleware";
import { routing } from "./i18n/routing";

// Next.js 16 renamed the `middleware.ts` convention to `proxy.ts`. The
// handler next-intl builds is just a (request) => response function, so
// re-exporting it as `proxy` here is all that's needed — nothing about
// next-intl itself changes.
export const proxy = createMiddleware(routing);

export const config = {
  // Run on everything except API routes, static assets, and metadata files.
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
