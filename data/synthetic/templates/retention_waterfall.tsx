import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";

const STAGES = [
  { label: "Open", value: 92, color: "#134e4a" },
  { label: "Practice", value: 74, color: "#0f766e" },
  { label: "Recall", value: 61, color: "#14b8a6" },
  { label: "Mastery", value: 43, color: "#5eead4" },
];

export const RetentionWaterfall = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: "#f8f3e7", padding: 84, fontFamily: "Avenir, sans-serif", color: "#17201b" }}>
      <div style={{ fontSize: 56, fontWeight: 800, letterSpacing: -2 }}>Learning funnel retention</div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 28, flex: 1, marginTop: 54 }}>
        {STAGES.map((stage, index) => {
          const progress = interpolate(frame, [index * 10, index * 10 + 38], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          });
          return (
            <div key={stage.label} style={{ flex: 1 }}>
              <div style={{ fontSize: 30, fontWeight: 800, marginBottom: 14 }}>{Math.round(stage.value * progress)}%</div>
              <div style={{ height: 380, display: "flex", alignItems: "flex-end" }}>
                <div style={{ width: "100%", height: Math.max(12, stage.value * 4 * progress), borderRadius: 28, backgroundColor: stage.color }} />
              </div>
              <div style={{ marginTop: 18, fontSize: 26 }}>{stage.label}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
