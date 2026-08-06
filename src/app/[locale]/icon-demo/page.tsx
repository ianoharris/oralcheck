/**
 * Throwaway comparison page for choosing an icon set to replace the emoji.
 * Not linked from anywhere and noindex'd. Delete once a pack is picked.
 */
import type { Metadata } from "next";
import {
  Cake, Cigarette, Wine, Dna, Sun, TriangleAlert, Users, Salad,
  Stethoscope, Leaf, Zap, BookOpen, Search, ChartColumn, Bug, Shield,
  Microscope, Lock, Check,
} from "lucide-react";
import {
  Cake as PhCake, Cigarette as PhCig, Wine as PhWine, Dna as PhDna,
  Sun as PhSun, Warning as PhWarn, UsersThree as PhUsers, Carrot as PhSalad,
  Tooth as PhTooth, Leaf as PhLeaf, Lightning as PhZap, BookOpen as PhBook,
  MagnifyingGlass as PhSearch, ChartBar as PhChart, Virus as PhVirus,
  ShieldCheck as PhShield, Microscope as PhMicro, Lock as PhLock, Check as PhCheck,
} from "@phosphor-icons/react/dist/ssr";
import {
  IconCake, IconSmoking, IconGlassFull, IconDna2, IconSun,
  IconAlertTriangle, IconUsersGroup, IconSalad, IconDental, IconLeaf,
  IconBolt, IconBook, IconZoom, IconChartBar, IconVirus, IconShieldCheck,
  IconMicroscope, IconLock, IconCheck,
} from "@tabler/icons-react";

export const metadata: Metadata = { robots: { index: false, follow: false } };

const LABELS = [
  "Age", "Tobacco", "Alcohol", "HPV", "Sun", "Symptoms", "Family",
  "Diet", "Dental", "Betel", "Risk", "Overview", "Self-exam", "Facts",
  "Virus", "Prevention", "Compare", "Private", "Done",
];
const EMOJI = ["🎂","🚬","🍷","🧬","☀️","⚠️","👨‍👩‍👧","🥗","🦷","🌿","⚡","📖","🔎","📊","🦠","🛡️","🔬","🔒","✓"];

const SZ = 28;
const lucide = [Cake, Cigarette, Wine, Dna, Sun, TriangleAlert, Users, Salad, Stethoscope, Leaf, Zap, BookOpen, Search, ChartColumn, Bug, Shield, Microscope, Lock, Check];
const phosphor = [PhCake, PhCig, PhWine, PhDna, PhSun, PhWarn, PhUsers, PhSalad, PhTooth, PhLeaf, PhZap, PhBook, PhSearch, PhChart, PhVirus, PhShield, PhMicro, PhLock, PhCheck];
const tabler = [IconCake, IconSmoking, IconGlassFull, IconDna2, IconSun, IconAlertTriangle, IconUsersGroup, IconSalad, IconDental, IconLeaf, IconBolt, IconBook, IconZoom, IconChartBar, IconVirus, IconShieldCheck, IconMicroscope, IconLock, IconCheck];

function Row({
  title, note, children,
}: { title: string; note: string; children: React.ReactNode }) {
  return (
    <section className="mb-12">
      <h2 className="font-serif text-2xl text-ink mb-1">{title}</h2>
      <p className="text-sm text-ink-soft mb-5">{note}</p>
      <div className="grid grid-cols-5 sm:grid-cols-10 gap-x-3 gap-y-5">{children}</div>
    </section>
  );
}

function Cell({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-2 text-center">
      <div className="h-9 flex items-center justify-center text-brand">{children}</div>
      <span className="text-[10px] leading-tight text-ink-soft">{label}</span>
    </div>
  );
}

export default function IconDemoPage() {
  return (
    <div className="max-w-5xl mx-auto px-5 py-12">
      <h1 className="font-serif text-4xl text-ink mb-2">Icon set comparison</h1>
      <p className="text-ink-soft mb-10 max-w-2xl leading-relaxed">
        The same 19 concepts the site actually uses, drawn from each candidate pack
        in brand teal. Every set below inherits <code>currentColor</code>, so they
        adapt to light and dark automatically. Toggle the theme in the nav to check
        contrast both ways.
      </p>

      <Row title="Current: emoji" note="Renders differently on every OS, and carries its own colours that ignore the brand and the dark background.">
        {EMOJI.map((e, i) => (
          <Cell key={i} label={LABELS[i]}>
            <span className="text-2xl">{e}</span>
          </Cell>
        ))}
      </Row>

      <Row title="Option A — Lucide" note="MIT. The most common choice; light 2px stroke, very neutral. No dedicated tooth icon, so Dental falls back to a stethoscope.">
        {lucide.map((I, i) => (
          <Cell key={i} label={LABELS[i]}><I size={SZ} strokeWidth={1.75} /></Cell>
        ))}
      </Row>

      <Row title="Option B — Phosphor" note="MIT. Has real Tooth and Virus icons, which matters here. Slightly rounder and friendlier; shown at regular weight.">
        {phosphor.map((I, i) => (
          <Cell key={i} label={LABELS[i]}><I size={SZ} weight="regular" /></Cell>
        ))}
      </Row>

      <Row title="Option C — Tabler" note="MIT. Has a dedicated dental icon too. Geometric and slightly more clinical in feel.">
        {tabler.map((I, i) => (
          <Cell key={i} label={LABELS[i]}><I size={SZ} stroke={1.75} /></Cell>
        ))}
      </Row>

      <section className="mt-14 pt-10 border-t border-warm-dim">
        <h2 className="font-serif text-2xl text-ink mb-5">In context: screener question</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { name: "Lucide", node: <Cigarette size={34} strokeWidth={1.75} /> },
            { name: "Phosphor", node: <PhCig size={34} weight="regular" /> },
            { name: "Tabler", node: <IconSmoking size={34} stroke={1.75} /> },
          ].map(({ name, node }) => (
            <div key={name} className="rounded-2xl border border-warm-dim bg-warm-dim p-6">
              <div className="text-brand mb-3">{node}</div>
              <div className="font-serif text-xl text-ink leading-snug mb-1.5">Do you use tobacco?</div>
              <p className="text-xs text-ink-soft leading-relaxed">
                Tobacco is the single strongest risk factor for oral cavity cancer.
              </p>
              <div className="mt-3 text-[10px] uppercase tracking-wider text-ink-soft">{name}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-12">
        <h2 className="font-serif text-2xl text-ink mb-5">In context: risk-tone colours</h2>
        <div className="flex flex-wrap gap-3">
          {[
            { l: "brand", c: "text-brand" },
            { l: "accent", c: "text-accent" },
            { l: "low", c: "text-low" },
            { l: "high", c: "text-high" },
            { l: "ink-soft", c: "text-ink-soft" },
          ].map(({ l, c }) => (
            <div key={l} className="flex items-center gap-2 rounded-xl border border-warm-dim bg-warm-dim px-4 py-3">
              <PhWarn size={22} weight="regular" className={c} />
              <span className="text-xs text-ink-soft">{l}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
