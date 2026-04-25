import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const METRICS = [
  { label: "Availability", value: 0.89, color: "#22c55e" },
  { label: "Performance", value: 0.81, color: "#38bdf8" },
  { label: "Quality", value: 0.94, color: "#facc15" },
];
const DOWNTIME = [18, 11, 24, 8, 15, 6];

export const ManufacturingOeeDashboard = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 88], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#10140f", padding: 68, color: "#f7fee7", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 24, color: "#bef264", textTransform: "uppercase", letterSpacing: 4 }}>Line 4 operations</div>
      <div style={{ fontSize: 56, fontWeight: 900, marginTop: 10 }}>Manufacturing OEE pulse</div>
      <div style={{ display: "grid", gridTemplateColumns: "1.25fr 1fr", gap: 34, marginTop: 38 }}>
        <div style={{ display: "flex", gap: 22 }}>
          {METRICS.map((metric) => {
            const radius = 72;
            const circumference = 2 * Math.PI * radius;
            return (
              <div key={metric.label} style={{ flex: 1, borderRadius: 26, padding: 26, backgroundColor: "rgba(255,255,255,0.07)", border: "1px solid rgba(190,242,100,0.22)" }}>
                <svg width="190" height="190" viewBox="0 0 190 190">
                  <circle cx="95" cy="95" r={radius} fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="18" />
                  <circle cx="95" cy="95" r={radius} fill="none" stroke={metric.color} strokeWidth="18" strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={circumference * (1 - metric.value * reveal)} transform="rotate(-90 95 95)" />
                  <text x="95" y="104" textAnchor="middle" fill="#f7fee7" fontSize="34" fontWeight="900">{Math.round(metric.value * reveal * 100)}%</text>
                </svg>
                <div style={{ fontSize: 24, fontWeight: 900, textAlign: "center" }}>{metric.label}</div>
              </div>
            );
          })}
        </div>
        <div style={{ borderRadius: 26, padding: 28, backgroundColor: "rgba(255,255,255,0.07)", border: "1px solid rgba(190,242,100,0.22)" }}>
          <div style={{ fontSize: 28, fontWeight: 900 }}>Downtime minutes</div>
          <div style={{ display: "flex", alignItems: "end", gap: 14, height: 230, marginTop: 26 }}>
            {DOWNTIME.map((value, index) => <div key={index} style={{ flex: 1, height: value * 7 * reveal, borderRadius: 12, backgroundColor: value > 20 ? "#fb7185" : "#84cc16" }} />)}
          </div>
          <div style={{ marginTop: 28, padding: "18px 22px", borderRadius: 18, backgroundColor: "#1f2937", fontSize: 24, fontWeight: 800 }}>Status: stable with micro-stops</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
