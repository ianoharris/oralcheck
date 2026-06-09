"use client";

import { useEffect } from "react";

export default function InstagramFeed({ widgetId }: { widgetId: string }) {
  useEffect(() => {
    if (document.querySelector('script[src="https://w.behold.so/widget.js"]')) return;
    const s = document.createElement("script");
    s.src = "https://w.behold.so/widget.js";
    s.type = "module";
    document.head.appendChild(s);
  }, []);

  return (
    // @ts-expect-error — behold-widget is a custom element, not in JSX types
    <behold-widget feed-id={widgetId} />
  );
}
