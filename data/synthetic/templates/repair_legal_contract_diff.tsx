import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const ROWS = [
  { section: "Renewal", before: "Auto-renews for 36 months", after: "Renews only after written approval" },
  { section: "Liability", before: "Unlimited vendor indemnity", after: "Mutual cap at annual fees" },
  { section: "Data use", before: "May use customer data broadly", after: "Use limited to service delivery" },
];

export const RepairLegalContractDiff = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: "#111827", color: "#f8fafc", fontFamily: "Avenir, sans-serif", padding: 70 }}>
      <div style={{ fontSize: 24, color: "#93c5fd", fontWeight: 900, textTransform: "uppercase" }}>Contract diff review</div>
      <div style={{ fontSize: 54, fontWeight: 900, marginTop: 10 }}>Risk clauses rewritten</div>
      <div style={{ display: "grid", gridTemplateColumns: "170px 1fr 1fr", gap: 16, marginTop: 42, fontSize: 22, color: "#cbd5e1", fontWeight: 900 }}>
        <div>Clause</div>
        <div>Before</div>
        <div>Safer replacement</div>
      </div>
      <div style={{ display: "grid", gap: 18, marginTop: 18 }}>
        {ROWS.map((row, index) => {
          const reveal = interpolate(frame, [index * 16, index * 16 + 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={row.section} style={{ display: "grid", gridTemplateColumns: "170px 1fr 1fr", gap: 16, alignItems: "stretch", opacity: reveal, transform: `translateY(${22 - reveal * 22}px)` }}>
              <div style={{ backgroundColor: "#1f2937", borderRadius: 16, padding: 22, fontSize: 25, fontWeight: 900 }}>{row.section}</div>
              <div style={{ backgroundColor: "rgba(239,68,68,0.16)", border: "1px solid rgba(239,68,68,0.45)", borderRadius: 16, padding: 22, color: "#fecaca", fontSize: 25, textDecoration: "line-through" }}>{row.before}</div>
              <div style={{ backgroundColor: "rgba(34,197,94,0.15)", border: "1px solid rgba(34,197,94,0.45)", borderRadius: 16, padding: 22, color: "#bbf7d0", fontSize: 25, fontWeight: 800 }}>{row.after}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
