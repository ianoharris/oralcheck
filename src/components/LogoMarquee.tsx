import Image from "next/image";

const logos = [
  {
    src: "/logos/wda.png",
    alt: "Wisconsin Dental Association",
    width: 160,
    height: 56,
    href: "https://www.wda.org/",
  },
  {
    src: "/logos/moresmiles.png",
    alt: "More Smiles Wisconsin",
    width: 96,
    height: 96,
    href: "https://www.moresmileswi.org/",
    blendMultiply: true,
  },
  {
    src: "/logos/harris.webp",
    alt: "Michael S. Harris DMD PA",
    width: 180,
    height: 56,
    href: "https://www.wellingtonoralsurgery.com/",
  },
  {
    src: "/logos/asbell.png",
    alt: "Dr. Karoline Asbell General Dentist",
    width: 200,
    height: 56,
    href: "https://www.drkarolineasbell.com/",
  },
];

// Repeat 3× per track so the scroll always looks full on any screen size
const repeated = [...logos, ...logos, ...logos];

function Track() {
  return (
    <>
      {repeated.map(({ src, alt, width, height, href, blendMultiply }, i) => (
        <a
          key={`${src}-${i}`}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center mx-10 flex-shrink-0 opacity-50 grayscale hover:opacity-100 hover:grayscale-0 transition-[opacity,filter] duration-300"
        >
          <Image
            src={src}
            alt={alt}
            width={width}
            height={height}
            className="object-contain"
            style={{
              height,
              width: "auto",
              maxWidth: width,
              ...(blendMultiply ? { mixBlendMode: "multiply" } : {}),
            }}
          />
        </a>
      ))}
    </>
  );
}

export default function LogoMarquee({ label }: { label: string }) {
  return (
    <section
      className="py-12 overflow-hidden border-y border-warm-dim"
      aria-labelledby="logo-strip-label"
    >
      {/* Sentence case, unlike the tracked all-caps eyebrows elsewhere: it is
          a plain statement of what the row is, not a heading. */}
      <p
        id="logo-strip-label"
        className="max-w-6xl mx-auto px-5 mb-6 text-xs font-semibold text-brand text-center"
      >
        {label}
      </p>
      <div className="relative">
        {/* Edge fades */}
        <div className="absolute inset-y-0 left-0 w-24 z-10 pointer-events-none bg-gradient-to-r from-warm to-transparent" />
        <div className="absolute inset-y-0 right-0 w-24 z-10 pointer-events-none bg-gradient-to-l from-warm to-transparent" />

        {/* Two identical tracks, translated by -50% for a seamless loop */}
        <div className="flex items-center animate-marquee">
          <Track />
          <Track />
        </div>
      </div>
    </section>
  );
}
