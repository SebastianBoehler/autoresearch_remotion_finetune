import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const GAUGES = [
  { label: "Availability", value: 86, color: "#22c55e" },
  { label: "Performance", value: 78, color: "#f59e0b" },
  { label: "Quality", value: 93, color: "#38bdf8" },
];
const DOWNTIME = [34, 18, 26, 12, 9];
const STATUS = ["Line 1 running", "Line 2 planned stop", "Line 3 recovered"];

export const RepairManufacturingOee = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: "#101827", color: "#f8fafc", fontFamily: "Avenir, sans-serif", padding: 70 }}>
      <div style={{ fontSize: 52, fontWeight: 900 }}>Manufacturing OEE dashboard</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 22, marginTop: 34 }}>
        {GAUGES.map((gauge, index) => {
          const reveal = interpolate(frame, [index * 10, index * 10 + 40], [0, gauge.value], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const circumference = 2 * Math.PI * 76;
          return (
            <div key={gauge.label} style={{ backgroundColor: "rgba(255,255,255,0.08)", borderRadius: 20, padding: 24, textAlign: "center" }}>
              <svg width="210" height="170" viewBox="0 0 210 170">
                <circle cx="105" cy="86" r="76" fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth="18" />
                <circle cx="105" cy="86" r="76" fill="none" stroke={gauge.color} strokeWidth="18" strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={circumference * (1 - reveal / 100)} transform="rotate(-90 105 86)" />
                <text x="105" y="96" textAnchor="middle" fill="#f8fafc" fontSize="36" fontWeight="900">{Math.round(reveal)}%</text>
              </svg>
              <div style={{ fontSize: 24, fontWeight: 900 }}>{gauge.label}</div>
            </div>
          );
        })}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 30, marginTop: 30 }}>
        <div style={{ backgroundColor: "rgba(255,255,255,0.08)", borderRadius: 20, padding: 26 }}>
          <div style={{ fontSize: 26, fontWeight: 900, marginBottom: 18 }}>Downtime bars</div>
          {DOWNTIME.map((value, index) => {
            const width = interpolate(frame, [20 + index * 8, 48 + index * 8], [0, value * 7], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return <div key={index} style={{ height: 28, width, margin: "13px 0", backgroundColor: "#f59e0b", borderRadius: 99 }} />;
          })}
        </div>
        <div style={{ backgroundColor: "rgba(255,255,255,0.08)", borderRadius: 20, padding: 26 }}>
          <div style={{ fontSize: 26, fontWeight: 900, marginBottom: 16 }}>Line status</div>
          {STATUS.map((status) => <div key={status} style={{ padding: "15px 0", borderBottom: "1px solid rgba(255,255,255,0.12)", fontSize: 24 }}>{status}</div>)}
        </div>
      </div>
    </AbsoluteFill>
  );
};
