export default function HeroToothIllustration() {
  return (
    <div className="flex items-center justify-center h-full py-4">
      <svg
        width="300"
        height="auto"
        viewBox="0 0 200 245"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden
        className="w-[300px] max-w-full"
      >
        <g fill="#0d7377" opacity="0.15">
          {/* Crown — smooth, gently domed, no internal detail */}
          <path d="
            M 28 112
            C 18 92, 16 62, 24 40
            C 32 18, 52 5, 75 5
            C 84 3, 93 3, 100 3
            C 107 3, 116 3, 125 5
            C 148 5, 168 18, 176 40
            C 184 62, 182 92, 172 112
            C 160 128, 138 135, 100 135
            C 62 135, 40 128, 28 112
            Z
          " />

          {/* Left root — tapers to a rounded tip */}
          <path d="
            M 52 133
            C 46 144, 40 170, 40 194
            C 40 212, 46 226, 56 228
            C 66 230, 74 218, 75 202
            C 76 185, 74 158, 67 145
            L 62 133
            Z
          " />

          {/* Right root — tapers to a rounded tip */}
          <path d="
            M 148 133
            C 154 144, 160 170, 160 194
            C 160 212, 154 226, 144 228
            C 134 230, 126 218, 125 202
            C 124 185, 126 158, 133 145
            L 138 133
            Z
          " />
        </g>
      </svg>
    </div>
  );
}
