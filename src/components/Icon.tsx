/**
 * Single place that maps a semantic icon name to a drawn icon.
 *
 * Data files (questions, learn articles, risk factors) store the *name* rather
 * than a component, so they stay plain serializable data and can cross the
 * server/client boundary and be read by the email route.
 *
 * Imported from Phosphor's `/ssr` entry, which renders plain SVG and therefore
 * works in both server and client components.
 */
import {
  Cake, Cigarette, Wine, Dna, Sun, Warning, UsersThree, Carrot, Tooth, Leaf,
  Lightning, BookOpen, MagnifyingGlass, ChartBar, Virus, ShieldCheck, Microscope,
  Lock, Check, WifiSlash, Star, Timer, Moon, SunDim, Printer, Bandaids,
  FirstAidKit, CalendarCheck, Prohibit, HandHeart, X, EnvelopeSimple,
  LinkedinLogo, InstagramLogo, DownloadSimple, Newspaper, ChatCircleText,
} from "@phosphor-icons/react/dist/ssr";
import type { Icon as PhosphorIcon } from "@phosphor-icons/react";

export const ICONS = {
  // screener questions
  age: Cake,
  tobacco: Cigarette,
  alcohol: Wine,
  hpv: Dna,
  sun: Sun,
  symptom: Warning,
  family: UsersThree,
  diet: Carrot,
  dental: Tooth,
  betel: Leaf,
  interaction: Lightning,

  // learn / results categories
  riskFactors: Lightning,
  overview: BookOpen,
  signs: Warning,
  selfExam: MagnifyingGlass,
  facts: ChartBar,
  virus: Virus,
  prevention: ShieldCheck,
  compare: Microscope,

  // UI
  private: Lock,
  check: Check,
  offline: WifiSlash,
  star: Star,
  timer: Timer,
  moon: Moon,
  sunDim: SunDim,
  printer: Printer,
  sore: Bandaids,
  clinic: FirstAidKit,
  appointment: CalendarCheck,
  noCost: Prohibit,
  care: HandHeart,
  close: X,
  email: EnvelopeSimple,
  linkedin: LinkedinLogo,
  instagram: InstagramLogo,
  review: ChatCircleText,
  download: DownloadSimple,
  press: Newspaper,
} as const;

export type IconName = keyof typeof ICONS;

export default function Icon({
  name,
  size = 24,
  weight = "regular",
  className,
}: {
  name: IconName;
  size?: number;
  weight?: "thin" | "light" | "regular" | "bold" | "fill" | "duotone";
  className?: string;
}) {
  const Cmp: PhosphorIcon = ICONS[name] ?? Warning;
  return <Cmp size={size} weight={weight} className={className} aria-hidden />;
}
