import { createNavigation } from "next-intl/navigation";
import { routing } from "./routing";

// Locale-aware wrappers: use these instead of next/link and next/navigation
// so links automatically get the /es prefix (or none, for en) attached.
export const { Link, redirect, usePathname, useRouter, getPathname } =
  createNavigation(routing);
