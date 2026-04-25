import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const ITEMS = ["Beta cohort", "Docs ready", "Pricing signed", "Launch email"];

export const LaunchReadinessChecklist = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sweep = interpolate(frame, [0, 120], [0, 360], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#eef2ff", padding: 72, color: "#1e1b4b", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 54, fontWeight: 900 }}>Launch readiness</div>
      <div style={{ display: "flex", gap: 48, marginTop: 42 }}>
        <svg width="430" height="430" viewBox="0 0 430 430">
          {[82, 142, 202].map((radius) => <circle key={radius} cx="215" cy="215" r={radius} fill="none" stroke="rgba(67,56,202,0.18)" strokeWidth="5" />)}
          <line x1="215" y1="215" x2="215" y2="26" stroke="#4f46e5" strokeWidth="10" strokeLinecap="round" transform={`rotate(${sweep} 215 215)`} />
        </svg>
        <div style={{ flex: 1, display: "grid", gap: 18 }}>
          {ITEMS.map((item, index) => {
            const pop = spring({ frame: frame - index * 12, fps, config: { damping: 18, stiffness: 140 } });
            return <div key={item} style={{ padding: 24, borderRadius: 24, backgroundColor: "#fff", fontSize: 30, fontWeight: 900, transform: `translateX(${32 - pop * 32}px)`, opacity: pop }}>✓ {item}</div>;
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
