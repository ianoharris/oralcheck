import Link from "next/link";

const steps = [
  {
    area: "Face & neck",
    instruction:
      "Look in the mirror at your face. Check that both sides look symmetrical. Feel the sides of your neck for lumps or swelling.",
  },
  {
    area: "Lips",
    instruction:
      "Pull your upper lip up and lower lip down. Look and feel for sores, color changes, or lumps on the inside and outside.",
  },
  {
    area: "Cheeks",
    instruction:
      "Use your fingers to gently pull each cheek outward. Look for red, white, or dark patches. Press gently to feel for lumps.",
  },
  {
    area: "Gums",
    instruction:
      "Examine your gums — top and bottom, front and back. Look for color changes, swelling, or sores.",
  },
  {
    area: "Tongue (top & sides)",
    instruction:
      "Stick out your tongue and look at the top. Then lift it to check underneath and the sides. The sides of the tongue are the most common site for oral cancer.",
  },
  {
    area: "Floor of mouth",
    instruction:
      "Lift your tongue to the roof of your mouth. Look at the floor underneath and feel it gently with a clean finger.",
  },
  {
    area: "Roof of mouth",
    instruction:
      "Tilt your head back and open wide. Look at the hard and soft palate for any color changes, bumps, or sores.",
  },
  {
    area: "Throat",
    instruction:
      "Say &quot;ahh&quot; and check the back of your throat. Look for asymmetry, patches, or sores.",
  },
];

export default function SelfExamPage() {
  return (
    <article className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
      <Link
        href="/learn"
        className="text-sm font-medium text-ink-soft hover:text-ink mb-6 inline-block"
      >
        ← Back to Learn
      </Link>
      <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full mb-4">
        How-to
      </span>
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        How to Do a 2-Minute Self-Exam
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10">
        Do this once a month. All you need is a mirror, good lighting, and
        clean hands. If you notice something that lasts 2+ weeks, see a
        dentist.
      </p>

      <ol className="space-y-3">
        {steps.map((s, i) => (
          <li
            key={s.area}
            className="bg-white rounded-2xl border border-warm-dim p-5 flex gap-4"
          >
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-brand text-white flex items-center justify-center font-semibold font-mono">
              {i + 1}
            </div>
            <div>
              <h2 className="font-semibold text-ink mb-1">{s.area}</h2>
              <p className="text-ink-soft leading-relaxed">{s.instruction}</p>
            </div>
          </li>
        ))}
      </ol>

      <div className="mt-10 p-6 rounded-2xl bg-low/10 border border-low/20">
        <h2 className="font-serif text-2xl text-ink mb-2">
          What&apos;s normal vs. what&apos;s not
        </h2>
        <p className="text-ink leading-relaxed mb-2">
          Most mouths have asymmetries, small bumps, and occasional canker
          sores — these heal in 1–2 weeks and aren&apos;t a concern.
        </p>
        <p className="text-ink leading-relaxed">
          What should prompt a visit: anything new, persistent (2+ weeks),
          painless but unusual, or that bleeds easily.
        </p>
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <Link
          href="/find-care"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          Find a dentist →
        </Link>
        <Link
          href="/learn/signs"
          className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          What signs to look for
        </Link>
      </div>
    </article>
  );
}
