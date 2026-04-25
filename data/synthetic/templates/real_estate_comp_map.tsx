import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const COMPS = [
  { name: "Oak", price: "$612", x: 170, y: 118, best: false },
  { name: "Pine", price: "$588", x: 292, y: 206, best: true },
  { name: "Lake", price: "$641", x: 422, y: 132, best: false },
  { name: "Hill", price: "$599", x: 358, y: 292, best: false },
];

export const RealEstateCompMap = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: "#111827", padding: 70, color: "#f9fafb", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Neighborhood comp map</div>
      <div style={{ marginTop: 10, fontSize: 25, color: "#cbd5e1" }}>Price per square foot and best-value comparison.</div>
      <div style={{ display: "grid", gridTemplateColumns: "570px 1fr", gap: 34, marginTop: 36 }}>
        <svg width="570" height="420" viewBox="0 0 570 420" style={{ borderRadius: 28, backgroundColor: "#172033", border: "1px solid rgba(255,255,255,0.12)" }}>
          <path d="M60 260 C150 190 210 300 292 206 C350 130 430 180 512 88" fill="none" stroke="#334155" strokeWidth="24" strokeLinecap="round" />
          <path d="M86 94 H498 M112 330 H500 M70 74 V350 M520 80 V346" stroke="#273449" strokeWidth="2" />
          {COMPS.map((comp, index) => {
            const scale = interpolate(frame, [index * 8, index * 8 + 22], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <g key={comp.name} transform={`translate(${comp.x} ${comp.y}) scale(${scale})`}>
                <circle r="24" fill={comp.best ? "#22c55e" : "#60a5fa"} />
                <text y="7" textAnchor="middle" fill="#08111f" fontSize="18" fontWeight="900">{comp.name}</text>
              </g>
            );
          })}
        </svg>
        <div style={{ display: "grid", gap: 16 }}>
          {COMPS.map((comp, index) => (
            <div key={comp.name} style={{ padding: 22, borderRadius: 22, backgroundColor: comp.best ? "rgba(34,197,94,0.2)" : "rgba(255,255,255,0.08)", border: `1px solid ${comp.best ? "#22c55e" : "rgba(255,255,255,0.14)"}`, opacity: interpolate(frame, [24 + index * 6, 42 + index * 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
              <div style={{ fontSize: 30, fontWeight: 900 }}>{comp.name} comp</div>
              <div style={{ marginTop: 5, fontSize: 24, color: "#cbd5e1" }}>{comp.price} per sq ft {comp.best ? "- best value" : ""}</div>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};
