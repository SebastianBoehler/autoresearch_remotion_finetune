import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";

const PANELS = [
  { title: "Hook", note: "Question opens loop", color: "#fde68a" },
  { title: "Demo", note: "Show the product", color: "#bfdbfe" },
  { title: "Proof", note: "Metric lands", color: "#bbf7d0" },
  { title: "CTA", note: "One next action", color: "#fecdd3" },
];

export const CreatorStoryboardGrid = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#fafafa", padding: 70, fontFamily: "Avenir, sans-serif", color: "#18181b" }}>
      <div style={{ fontSize: 56, fontWeight: 900 }}>Creator storyboard</div>
      <div style={{ marginTop: 42, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, flex: 1 }}>
        {PANELS.map((panel, index) => {
          const pop = spring({ frame: frame - index * 10, fps, config: { damping: 17, stiffness: 140 } });
          return (
            <div key={panel.title} style={{ borderRadius: 28, padding: 34, backgroundColor: panel.color, transform: `scale(${0.9 + pop * 0.1})`, boxShadow: "0 20px 44px rgba(24,24,27,0.12)" }}>
              <div style={{ fontSize: 24, fontWeight: 900, color: "#52525b" }}>0{index + 1}</div>
              <div style={{ marginTop: 18, fontSize: 46, fontWeight: 900 }}>{panel.title}</div>
              <div style={{ marginTop: 14, fontSize: 28, lineHeight: 1.25 }}>{panel.note}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
