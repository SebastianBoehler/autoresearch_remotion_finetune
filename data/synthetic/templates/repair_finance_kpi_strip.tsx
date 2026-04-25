import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const METRICS = [
  { label: "Revenue", value: "$428k", delta: "+18%", color: "#16a34a" },
  { label: "Net retention", value: "117%", delta: "+5 pts", color: "#2563eb" },
  { label: "Bookings", value: "$612k", delta: "+23%", color: "#7c3aed" },
];
const SPARK = [32, 42, 38, 54, 61, 58, 72];

export const RepairFinanceKpiStrip = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 84], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const sparkPath = SPARK.map((value, index) => `${index === 0 ? "M" : "L"} ${54 + index * 64} ${185 - value * 1.8}`).join(" ");

  return (
    <AbsoluteFill style={{ backgroundColor: "#f8fafc", color: "#0f172a", fontFamily: "Avenir, sans-serif", padding: 74 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontSize: 52, fontWeight: 900 }}>Revenue KPI strip</div>
        <div style={{ backgroundColor: "#dcfce7", color: "#166534", borderRadius: 99, padding: "16px 24px", fontSize: 24, fontWeight: 900 }}>On plan</div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20, marginTop: 34 }}>
        {METRICS.map((metric, index) => {
          const cardReveal = interpolate(frame, [index * 10, index * 10 + 26], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={metric.label} style={{ backgroundColor: "#ffffff", borderRadius: 18, padding: 28, boxShadow: "0 16px 40px rgba(15,23,42,0.09)", opacity: cardReveal, transform: `translateY(${24 - cardReveal * 24}px)` }}>
              <div style={{ fontSize: 22, color: metric.color, fontWeight: 900 }}>{metric.label}</div>
              <div style={{ fontSize: 48, fontWeight: 900, marginTop: 10 }}>{metric.value}</div>
              <div style={{ marginTop: 12, color: "#16a34a", fontSize: 22, fontWeight: 900 }}>{metric.delta}</div>
            </div>
          );
        })}
      </div>
      <svg width="620" height="230" viewBox="0 0 520 230" style={{ marginTop: 42 }}>
        {[55, 115, 175].map((y) => <line key={y} x1="40" x2="480" y1={y} y2={y} stroke="#e2e8f0" />)}
        <path d={sparkPath} fill="none" stroke="#16a34a" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="620" strokeDashoffset={620 * (1 - reveal)} />
        {SPARK.map((value, index) => <circle key={index} cx={54 + index * 64} cy={185 - value * 1.8} r={reveal > index / 6 ? 8 : 0} fill="#16a34a" />)}
      </svg>
    </AbsoluteFill>
  );
};
