import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const CLAIMS = [
  { name: "Auto", sev: 0.62, freq: 0.78, color: "#38bdf8" },
  { name: "Property", sev: 0.84, freq: 0.46, color: "#f97316" },
  { name: "Health", sev: 0.58, freq: 0.64, color: "#a78bfa" },
  { name: "Liability", sev: 0.91, freq: 0.32, color: "#fb7185" },
];

export const InsuranceClaimsRiskMatrix = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: "#08111f", padding: 70, color: "#f8fafc", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 22, letterSpacing: 4, color: "#93c5fd", textTransform: "uppercase" }}>Claims risk desk</div>
      <div style={{ fontSize: 54, fontWeight: 900, marginTop: 10 }}>Severity by frequency matrix</div>
      <div style={{ position: "relative", marginTop: 42, height: 430, borderRadius: 28, border: "1px solid rgba(147,197,253,0.28)", backgroundColor: "rgba(15,23,42,0.8)" }}>
        {[0, 1, 2, 3].map((line) => <div key={line} style={{ position: "absolute", left: 74 + line * 260, top: 40, bottom: 62, width: 1, backgroundColor: "rgba(255,255,255,0.08)" }} />)}
        {[0, 1, 2].map((line) => <div key={line} style={{ position: "absolute", left: 58, right: 60, top: 82 + line * 92, height: 1, backgroundColor: "rgba(255,255,255,0.08)" }} />)}
        {CLAIMS.map((claim, index) => {
          const pop = interpolate(frame, [index * 10, index * 10 + 28], [0.35, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={claim.name} style={{ position: "absolute", left: `${10 + claim.freq * 76}%`, bottom: `${14 + claim.sev * 65}%`, transform: `translate(-50%, 50%) scale(${pop})`, width: 142, padding: 14, borderRadius: 20, backgroundColor: claim.color, color: "#08111f", boxShadow: `0 0 ${28 * pop}px ${claim.color}` }}>
              <div style={{ fontSize: 24, fontWeight: 900 }}>{claim.name}</div>
              <div style={{ marginTop: 4, fontSize: 16, fontWeight: 800 }}>Risk {Math.round((claim.sev + claim.freq) * 50)}</div>
            </div>
          );
        })}
        <div style={{ position: "absolute", left: 56, bottom: 20, color: "#cbd5e1", fontSize: 22 }}>Frequency</div>
        <div style={{ position: "absolute", right: 44, top: 34, padding: "16px 22px", borderRadius: 18, backgroundColor: "#fef3c7", color: "#111827", fontSize: 24, fontWeight: 900 }}>Reserve risk: elevated</div>
      </div>
    </AbsoluteFill>
  );
};
