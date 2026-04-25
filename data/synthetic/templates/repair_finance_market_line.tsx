import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const POINTS = [
  { month: "Jan", x: 90, y: 300 },
  { month: "Feb", x: 240, y: 260 },
  { month: "Mar", x: 390, y: 284 },
  { month: "Apr", x: 540, y: 210 },
  { month: "May", x: 690, y: 180 },
  { month: "Jun", x: 840, y: 126 },
  { month: "Jul", x: 990, y: 108 },
];
const BADGES = ["ARR $2.8M", "Gross margin 72%", "Pipeline +31%"];

export const RepairFinanceMarketLine = () => {
  const frame = useCurrentFrame();
  const lineReveal = interpolate(frame, [0, 82], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const path = POINTS.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a1020", color: "#f8fafc", fontFamily: "Avenir, sans-serif", padding: 72 }}>
      <div style={{ fontSize: 25, color: "#38bdf8", fontWeight: 900, textTransform: "uppercase" }}>Finance dashboard</div>
      <div style={{ fontSize: 56, fontWeight: 900, marginTop: 10 }}>Revenue line regained momentum</div>
      <svg width="100%" height="390" viewBox="0 0 1080 390" style={{ marginTop: 28 }}>
        {[120, 210, 300].map((y) => <line key={y} x1="60" x2="1030" y1={y} y2={y} stroke="rgba(255,255,255,0.12)" />)}
        <path d={path} fill="none" stroke="#38bdf8" strokeWidth="12" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="1150" strokeDashoffset={1150 * (1 - lineReveal)} />
        {POINTS.map((point, index) => {
          const dotReveal = interpolate(frame, [index * 8 + 24, index * 8 + 34], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <g key={point.month} opacity={dotReveal}>
              <circle cx={point.x} cy={point.y} r={11} fill="#f8fafc" stroke="#38bdf8" strokeWidth="5" />
              <text x={point.x} y={350} textAnchor="middle" fill="#94a3b8" fontSize="20" fontWeight="700">{point.month}</text>
            </g>
          );
        })}
      </svg>
      <div style={{ display: "flex", gap: 18 }}>
        {BADGES.map((badge, index) => <div key={badge} style={{ padding: "18px 24px", borderRadius: 14, backgroundColor: "rgba(56,189,248,0.14)", border: "1px solid rgba(56,189,248,0.42)", fontSize: 26, fontWeight: 900, opacity: interpolate(frame, [58 + index * 8, 74 + index * 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{badge}</div>)}
      </div>
    </AbsoluteFill>
  );
};
