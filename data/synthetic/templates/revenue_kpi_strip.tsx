import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const METRICS = [
  { label: "ARR", value: "$1.9M", color: "#34d399" },
  { label: "Margin", value: "41%", color: "#60a5fa" },
  { label: "Forecast", value: "$2.4M", color: "#facc15" },
];
const SPARK = [24, 30, 28, 38, 44, 52];

export const RevenueKpiStrip = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 84], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const path = SPARK.map((value, index) => `${index === 0 ? "M" : "L"} ${60 + index * 92} ${220 - value * 2.4}`).join(" ");
  return (
    <AbsoluteFill style={{ backgroundColor: "#f8fafc", padding: 76, color: "#0f172a", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 52, fontWeight: 900 }}>Revenue KPI strip</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 20, marginTop: 34 }}>
        {METRICS.map((metric, index) => <div key={metric.label} style={{ padding: 28, borderRadius: 22, backgroundColor: "#fff", boxShadow: "0 16px 36px rgba(15,23,42,0.08)", opacity: interpolate(frame, [index * 8, index * 8 + 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}><div style={{ color: metric.color, fontSize: 22, fontWeight: 900 }}>{metric.label}</div><div style={{ fontSize: 46, fontWeight: 900, marginTop: 6 }}>{metric.value}</div></div>)}
      </div>
      <svg width="720" height="270" viewBox="0 0 620 270" style={{ marginTop: 42 }}>
        <path d={path} fill="none" stroke="#2563eb" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round" strokeDasharray="700" strokeDashoffset={700 * (1 - reveal)} />
        {SPARK.map((value, index) => <circle key={index} cx={60 + index * 92} cy={220 - value * 2.4} r={reveal > index / 5 ? 9 : 0} fill="#2563eb" />)}
      </svg>
      <div style={{ position: "absolute", right: 78, bottom: 74, padding: "18px 26px", borderRadius: 99, backgroundColor: "#dcfce7", color: "#166534", fontSize: 26, fontWeight: 900 }}>Status: ahead of plan</div>
    </AbsoluteFill>
  );
};
