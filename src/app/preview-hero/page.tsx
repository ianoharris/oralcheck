import HeroMockupA from "@/components/HeroMockupA";
import HeroMockupB from "@/components/HeroMockupB";
import HeroSection from "@/components/HeroSection";
import AnimatedStats from "@/components/AnimatedStats";

function Label({ text }: { text: string }) {
  return (
    <div
      style={{
        backgroundColor: "#2d2d2d",
        color: "#faf9f6",
        textAlign: "center",
        fontSize: "10px",
        fontFamily: "monospace",
        letterSpacing: "0.18em",
        textTransform: "uppercase",
        padding: "10px 20px",
      }}
    >
      {text}
    </div>
  );
}

export default function PreviewHeroPage() {
  return (
    <div>
      <Label text="Direction A — Geometric / Dark Teal" />
      <HeroMockupA />

      <Label text="Direction B — Editorial / Warm Portrait" />
      <HeroMockupB />

      <Label text="Current (reference)" />
      <HeroSection />
      <AnimatedStats />
    </div>
  );
}
