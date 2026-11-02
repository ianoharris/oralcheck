"use client";

import { motion } from "framer-motion";

interface Props {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}

// One tree on the server and the client. This used to return a plain <div>
// when useReducedMotion() was true, but that hook is null during server
// rendering, so the HTML shipped with opacity:0 and hydration never repaired
// it: with "Reduce motion" on, /learn and half the home page stayed blank.
// MotionProvider (in the layout) now honours the setting by dropping the
// movement and keeping the fade.
export default function FadeUp({ children, delay = 0, className }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 28 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "0px 0px -10% 0px" }}
      transition={{ duration: 0.55, delay, ease: "easeOut" as const }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
