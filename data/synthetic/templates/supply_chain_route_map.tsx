import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const STOPS = [
  { name: "Factory", x: 140, y: 390 },
  { name: "Port", x: 420, y: 250 },
  { name: "Hub", x: 720, y: 340 },
  { name: "Store", x: 1040, y: 220 },
];

export const SupplyChainRouteMap = () => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, 120], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#f1f5f9", padding: 72, fontFamily: "Avenir, sans-serif", color: "#0f172a" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Supply route confidence</div>
      <svg width="100%" height="500" viewBox="0 0 1280 540" style={{ marginTop: 32 }}>
        <path d="M140 390 C280 160 510 160 720 340 S930 360 1040 220" fill="none" stroke="#94a3b8" strokeWidth="16" strokeLinecap="round" />
        <path d="M140 390 C280 160 510 160 720 340 S930 360 1040 220" fill="none" stroke="#0f766e" strokeWidth="16" strokeLinecap="round" strokeDasharray="1200" strokeDashoffset={1200 * (1 - progress)} />
        {STOPS.map((stop, index) => (
          <g key={stop.name}>
            <circle cx={stop.x} cy={stop.y} r={progress > index / 3 ? 40 : 28} fill="#ccfbf1" stroke="#0f766e" strokeWidth="8" />
            <text x={stop.x} y={stop.y + 78} textAnchor="middle" fill="#0f172a" fontSize="26" fontWeight="900">{stop.name}</text>
          </g>
        ))}
      </svg>
      <div style={{ display: "flex", gap: 18 }}>
        {["ETA stable", "Cold chain ok", "Customs low risk"].map((label) => <div key={label} style={{ padding: "16px 22px", borderRadius: 18, backgroundColor: "#fff", fontSize: 26, fontWeight: 800 }}>{label}</div>)}
      </div>
    </AbsoluteFill>
  );
};
