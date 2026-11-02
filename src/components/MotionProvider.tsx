"use client";

import { MotionConfig } from "framer-motion";

// Honours the visitor's "Reduce motion" setting everywhere: Motion drops
// transform animations and keeps opacity fades, so content still appears.
// Components should not branch their markup on useReducedMotion() for
// anything that starts hidden; see FadeUp.
export default function MotionProvider({ children }: { children: React.ReactNode }) {
  return <MotionConfig reducedMotion="user">{children}</MotionConfig>;
}
