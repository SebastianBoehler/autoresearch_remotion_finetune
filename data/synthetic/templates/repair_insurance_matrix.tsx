import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const CLAIMS = [
  { label: "Property", severity: 4, frequency: 3, reserve: "$1.2M" },
  { label: "Liability", severity: 5, frequency: 2, reserve: "$980k" },
  { label: "Medical", severity: 2, frequency: 5, reserve: "$640k" },
  { label: "Workers comp", severity: 3, frequency: 4, reserve: "$720k" },
];

export const RepairInsuranceMatrix = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: "#f8fafc", color: "#0f172a", fontFamily: "Avenir, sans-serif", padding: 68 }}>
      <div style={{ fontSize: 52, fontWeight: 900 }}>Insurance claims risk matrix</div>
      <div style={{ display: "grid", gridTemplateColumns: "820px 1fr", gap: 36, marginTop: 30 }}>
        <div style={{ position: "relative", height: 470, backgroundColor: "#ffffff", borderRadius: 22, boxShadow: "0 18px 42px rgba(15,23,42,0.08)", padding: 38 }}>
          <div style={{ position: "absolute", left: 38, bottom: 34, width: 720, height: 360, borderLeft: "4px solid #94a3b8", borderBottom: "4px solid #94a3b8" }} />
          <div style={{ position: "absolute", left: 28, top: 28, fontSize: 20, fontWeight: 900, color: "#64748b" }}>Severity</div>
          <div style={{ position: "absolute", right: 56, bottom: 12, fontSize: 20, fontWeight: 900, color: "#64748b" }}>Frequency</div>
          {CLAIMS.map((claim, index) => {
            const reveal = interpolate(frame, [index * 12, index * 12 + 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            const left = 70 + claim.frequency * 128;
            const top = 400 - claim.severity * 62;
            return (
              <div key={claim.label} style={{ position: "absolute", left, top, opacity: reveal, transform: `scale(${0.72 + reveal * 0.28})` }}>
                <div style={{ width: 108, height: 108, borderRadius: 54, backgroundColor: "#2563eb", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, fontWeight: 900, textAlign: "center" }}>{claim.label}</div>
              </div>
            );
          })}
        </div>
        <div style={{ backgroundColor: "#0f172a", color: "#f8fafc", borderRadius: 22, padding: 32 }}>
          <div style={{ fontSize: 26, fontWeight: 900, color: "#93c5fd" }}>Reserve-risk badge</div>
          {CLAIMS.map((claim) => <div key={claim.label} style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid rgba(255,255,255,0.12)", padding: "18px 0", fontSize: 24 }}><span>{claim.label}</span><strong>{claim.reserve}</strong></div>)}
        </div>
      </div>
    </AbsoluteFill>
  );
};
