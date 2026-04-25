import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const COHORTS = [
  { name: "Jan", values: [42, 24, 13] },
  { name: "Feb", values: [46, 27, 16] },
  { name: "Mar", values: [49, 31, 19] },
  { name: "Apr", values: [44, 26, 14] },
];
const HEADERS = ["D1", "D7", "D30"];

export const GamingRetentionCohorts = () => {
  const frame = useCurrentFrame();
  const highlight = interpolate(frame, [34, 82], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#090b16", padding: 72, color: "#f8fafc", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 24, color: "#f0abfc", letterSpacing: 4, textTransform: "uppercase" }}>Game analytics</div>
      <div style={{ fontSize: 56, fontWeight: 900, marginTop: 10 }}>Retention cohort view</div>
      <div style={{ display: "grid", gridTemplateColumns: "160px repeat(3, 1fr)", gap: 14, marginTop: 46 }}>
        <div />
        {HEADERS.map((header) => <div key={header} style={{ padding: 18, borderRadius: 16, backgroundColor: "#1f2937", textAlign: "center", fontSize: 24, fontWeight: 900 }}>{header}</div>)}
        {COHORTS.map((cohort, rowIndex) => (
          <div key={cohort.name} style={{ display: "contents" }}>
            <div style={{ padding: 20, borderRadius: 16, backgroundColor: "rgba(255,255,255,0.08)", fontSize: 25, fontWeight: 900 }}>{cohort.name}</div>
            {cohort.values.map((value, index) => {
              const cell = interpolate(frame, [rowIndex * 8 + index * 5, 36 + rowIndex * 8 + index * 5], [0, value], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
              return <div key={index} style={{ padding: 20, borderRadius: 16, textAlign: "center", fontSize: 28, fontWeight: 900, backgroundColor: `rgba(168,85,247,${0.15 + value / 90})`, outline: rowIndex === 2 ? `${4 * highlight}px solid #f0abfc` : "none" }}>{Math.round(cell)}%</div>;
            })}
          </div>
        ))}
      </div>
      <div style={{ position: "absolute", right: 72, bottom: 58, padding: "20px 28px", borderRadius: 22, backgroundColor: "#3b0764", border: "1px solid #f0abfc", fontSize: 26, fontWeight: 900 }}>Churn risk: watch April D30</div>
    </AbsoluteFill>
  );
};
