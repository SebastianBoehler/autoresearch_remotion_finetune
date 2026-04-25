import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const STEPS = [
  { label: "Plan", detail: "Split request", color: "#a7f3d0" },
  { label: "Search", detail: "Pull docs", color: "#bfdbfe" },
  { label: "Patch", detail: "Edit files", color: "#ddd6fe" },
  { label: "Verify", detail: "Run tests", color: "#fde68a" },
];

export const AiAgentTrace = () => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, 120], [0, STEPS.length - 0.25], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#101623", padding: 78, color: "#f8fafc", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 56, fontWeight: 900 }}>Agent execution trace</div>
      <div style={{ marginTop: 52, display: "grid", gridTemplateColumns: "220px 1fr", gap: 28 }}>
        {STEPS.map((step, index) => {
          const active = progress >= index;
          return (
            <div key={step.label} style={{ display: "contents" }}>
              <div style={{ opacity: active ? 1 : 0.35, fontSize: 28, fontWeight: 900 }}>{String(index + 1).padStart(2, "0")} / {step.label}</div>
              <div style={{ height: 82, borderRadius: 22, backgroundColor: active ? step.color : "rgba(255,255,255,0.08)", color: active ? "#111827" : "#cbd5e1", padding: "22px 28px", transform: `translateX(${active ? 0 : 24}px)`, fontSize: 28, fontWeight: 800 }}>
                {step.detail}
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", right: 82, bottom: 66, width: 340, height: 22, borderRadius: 99, backgroundColor: "rgba(255,255,255,0.16)" }}>
        <div style={{ width: `${Math.round((progress / (STEPS.length - 0.25)) * 100)}%`, height: "100%", borderRadius: 99, backgroundColor: "#38bdf8" }} />
      </div>
    </AbsoluteFill>
  );
};
