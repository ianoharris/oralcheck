import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import ContactForm from "@/components/ContactForm";

export const metadata: Metadata = {
  title: { absolute: "About OralCheck | Free Oral Cancer Risk Screener" },
  description:
    "OralCheck is a free, private oral cancer risk screener built by a UW-Madison predental student. Learn about the mission, how it works, and the sources behind the tool.",
  alternates: { canonical: "https://oralcheck.org/about" },
};

export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        About OralCheck
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10">
        A free, private tool to help anyone understand their oral cancer risk
        — and take the next step toward care.
      </p>

      <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-5">Who built this</h2>
        <div className="flex items-center gap-4 mb-6">
          <Image
            src="/ian-harris.jpg"
            alt="Ian Harris, founder of OralCheck"
            width={200}
            height={200}
            className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl object-cover object-[center_25%] border border-warm-dim shrink-0"
          />
          <div>
            <div className="font-serif text-xl text-ink">Ian Harris</div>
            <div className="text-sm text-ink-soft">
              Founder · Predental student, UW&#8211;Madison
            </div>
          </div>
        </div>
        <p className="text-ink-soft leading-relaxed mb-3">
          OralCheck was built by Ian Harris, a predental student at the University of
          Wisconsin-Madison. I care a lot about community health and finding
          ways to actually make a difference with the knowledge I&apos;m
          gaining in school.
        </p>
        <p className="text-ink-soft leading-relaxed mb-3">
          A few years ago I was diagnosed with a chronic health condition that
          has significantly affected my day to day life. Going through that
          taught me how much your health can sneak up on you if you&apos;re not
          paying attention. It also showed me how important it is to have
          access to good information and to not brush things off. That
          experience is a big reason I want to go into dentistry and why I
          built this.
        </p>
        <p className="text-ink-soft leading-relaxed">
          I really believe that keeping your community healthier and more
          informed, even just one person at a time, is worth something. Oral
          cancer is one of those things that a lot of people have never even
          thought about, and it&apos;s so much more treatable when it&apos;s
          caught early. I wanted to build something that could help with that.
        </p>
      </section>

      <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-3">How it works</h2>
        <ul className="space-y-3 text-ink-soft leading-relaxed">
          <li>
            <strong className="text-ink">Your answers stay on your device.</strong>{" "}
            Nothing is saved to a server. No accounts. No tracking of responses.
          </li>
          <li>
            <strong className="text-ink">Scoring is educational, not clinical.</strong>{" "}
            Each answer contributes a weight derived from published risk data.
            The total maps to a risk tier — Low, Moderate, Elevated, or
            See-a-Dentist-Soon.
          </li>
          <li>
            <strong className="text-ink">It is not a diagnosis.</strong>{" "}
            OralCheck can suggest you should talk to a clinician. It cannot
            tell you whether you have cancer.
          </li>
        </ul>
      </section>

      <section className="bg-accent/10 border border-accent/20 rounded-2xl p-6 sm:p-8 mb-10">
        <h2 className="font-serif text-2xl text-ink mb-3">Medical disclaimer</h2>
        <p className="text-ink leading-relaxed">
          OralCheck provides general health information only. It does not
          constitute medical advice, diagnosis, or treatment. Always seek the
          advice of a qualified health provider with any questions about a
          medical condition. Do not delay seeking care because of information
          on this site.
        </p>
      </section>

      <div className="flex flex-wrap gap-3">
        <Link
          href="/screener"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          Start the screener →
        </Link>
        <Link
          href="/find-care"
          className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          Find care
        </Link>
      </div>

      <section id="feedback" className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mt-6">
        <h2 className="font-serif text-2xl text-ink mb-1">Get in touch</h2>
        <p className="text-ink-soft leading-relaxed mb-5 text-sm">
          Found a bug, have a suggestion, or just want to say something? I read
          everything. Email is optional — leave it blank if you&apos;d rather stay
          anonymous.
        </p>
        <ContactForm />
      </section>
    </div>
  );
}
