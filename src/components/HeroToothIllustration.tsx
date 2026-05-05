export default function HeroToothIllustration() {
  return (
    <div className="flex items-center justify-center h-full">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 130 118"
        aria-hidden
        className="w-[340px] h-auto"
      >
        {/*
          Molar silhouette — clockwise from left cusp peak:
          1. Down left outer side through neck into left root
          2. Left root tip → up inner edge → U gap arch
          3. U gap arch → down right inner edge → right root tip
          4. Up right outer side through neck
          5. Across crown top — right cusp → centre cusp → left cusp
        */}
        <path
          fill="#0d7377"
          opacity="0.14"
          d="
            M 22 10
            C 12 12, 4 22, 4 40
            C 4 52, 10 62, 14 70
            C 12 78, 7 90, 7 102
            C 6 112, 12 118, 22 118
            C 32 118, 38 106, 40 94
            C 42 82, 46 78, 50 76
            C 54 72, 58 62, 65 62
            C 72 62, 76 72, 80 76
            C 84 78, 88 82, 90 94
            C 92 106, 98 118, 108 118
            C 118 118, 124 112, 123 102
            C 122 90, 118 78, 116 70
            C 120 62, 126 52, 126 40
            C 126 22, 118 12, 108 10
            C 100 6, 92 22, 88 26
            C 84 30, 72 20, 65 13
            C 58 20, 46 30, 42 26
            C 36 22, 28 6, 22 10
            Z
          "
        />
      </svg>
    </div>
  );
}
