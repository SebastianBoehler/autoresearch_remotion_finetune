import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";

const FEATURES = [
  { title: "Smart Queue", body: "Prioritizes cards by forgetting risk.", color: "#e0f2fe" },
  { title: "Micro Review", body: "Keeps sessions under five minutes.", color: "#dcfce7" },
  { title: "Proof Trail", body: "Shows why each topic is scheduled.", color: "#fae8ff" },
];

export const FeatureStack = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#fafaf9", padding: 74, fontFamily: "Avenir, sans-serif", color: "#18181b" }}>
      <div style={{ fontSize: 54, fontWeight: 900, letterSpacing: -2 }}>Learning app primitives</div>
      <div style={{ position: "relative", flex: 1, marginTop: 42 }}>
        {FEATURES.map((feature, index) => {
          const reveal = spring({ frame: frame - index * 14, fps, config: { damping: 18, stiffness: 120 } });
          return (
            <div key={feature.title} style={{ position: "absolute", top: index * 118, left: index * 52, right: index * 24, padding: 34, borderRadius: 32, backgroundColor: feature.color, border: "3px solid #18181b", transform: `translateY(${(1 - reveal) * 36}px) rotate(${-2 + index * 2}deg)`, opacity: reveal }}>
              <div style={{ fontSize: 38, fontWeight: 900 }}>{feature.title}</div>
              <div style={{ marginTop: 12, fontSize: 27 }}>{feature.body}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
