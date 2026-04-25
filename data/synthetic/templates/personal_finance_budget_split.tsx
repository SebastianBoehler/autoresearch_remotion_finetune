import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const SEGMENTS = [
  { label: "Housing", value: 34, color: "#60a5fa" },
  { label: "Food", value: 16, color: "#34d399" },
  { label: "Travel", value: 12, color: "#fbbf24" },
  { label: "Invest", value: 24, color: "#a78bfa" },
  { label: "Buffer", value: 14, color: "#fb7185" },
];

export const PersonalFinanceBudgetSplit = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 90], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const radius = 122;
  const circumference = 2 * Math.PI * radius;
  return (
    <AbsoluteFill style={{ backgroundColor: "#f7f7fb", padding: 74, color: "#111827", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 22, letterSpacing: 4, color: "#4f46e5", textTransform: "uppercase" }}>Personal finance</div>
      <div style={{ fontSize: 56, fontWeight: 900, marginTop: 10 }}>Monthly budget split</div>
      <div style={{ display: "grid", gridTemplateColumns: "430px 1fr", gap: 70, marginTop: 38, alignItems: "center" }}>
        <svg width="420" height="420" viewBox="0 0 420 420">
          <circle cx="210" cy="210" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="46" />
          {SEGMENTS.map((segment, index) => {
            const before = SEGMENTS.slice(0, index).reduce((sum, item) => sum + item.value, 0);
            return <circle key={segment.label} cx="210" cy="210" r={radius} fill="none" stroke={segment.color} strokeWidth="46" strokeDasharray={`${(segment.value / 100) * circumference * reveal} ${circumference}`} strokeDashoffset={-(before / 100) * circumference} transform="rotate(-90 210 210)" />;
          })}
          <text x="210" y="202" textAnchor="middle" fontSize="52" fontWeight="900" fill="#111827">24%</text>
          <text x="210" y="242" textAnchor="middle" fontSize="22" fill="#6b7280">savings rate</text>
        </svg>
        <div style={{ display: "grid", gap: 16 }}>
          {SEGMENTS.map((segment, index) => (
            <div key={segment.label} style={{ display: "grid", gridTemplateColumns: "22px 1fr 80px", gap: 16, alignItems: "center", padding: 18, borderRadius: 18, backgroundColor: "#fff", boxShadow: "0 14px 34px rgba(15,23,42,0.08)", opacity: interpolate(frame, [20 + index * 6, 38 + index * 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
              <div style={{ width: 22, height: 22, borderRadius: 99, backgroundColor: segment.color }} />
              <div style={{ fontSize: 25, fontWeight: 850 }}>{segment.label}</div>
              <div style={{ fontSize: 25, fontWeight: 900 }}>{segment.value}%</div>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
