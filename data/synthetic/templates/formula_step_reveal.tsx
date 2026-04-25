import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const STEPS = ["Measure loss", "Compute gradient", "Take small step"];

export const FormulaStepReveal = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: "#111827", padding: 76, color: "#f9fafb", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Gradient descent steps</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 20, marginTop: 56 }}>
        {STEPS.map((step, index) => {
          const show = interpolate(frame, [index * 16, index * 16 + 28], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return <div key={step} style={{ padding: 30, borderRadius: 24, backgroundColor: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.14)", transform: `translateY(${28 * (1 - show)}px)`, opacity: show }}><div style={{ color: "#93c5fd", fontSize: 24, fontWeight: 900 }}>0{index + 1}</div><div style={{ marginTop: 18, fontSize: 32, fontWeight: 900 }}>{step}</div></div>;
        })}
      </div>
      <div style={{ marginTop: 62, opacity: interpolate(frame, [64, 92], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }), padding: 28, borderRadius: 22, backgroundColor: "#dbeafe", color: "#0f172a", fontSize: 38, fontWeight: 900 }}>theta next = theta - alpha * gradient</div>
    </AbsoluteFill>
  );
};
