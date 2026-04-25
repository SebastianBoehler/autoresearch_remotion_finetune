import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const TEXT = "Gradient descent follows the slope toward lower loss.";

export const ShortTypewriterLesson = () => {
  const frame = useCurrentFrame();
  const chars = Math.floor(interpolate(frame, [0, 72], [0, TEXT.length], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const cursor = Math.floor(frame / 10) % 2 === 0;
  const chip = interpolate(frame, [58, 86], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: "#09090b", padding: 82, color: "#f8fafc", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 24, color: "#a78bfa", letterSpacing: 4, textTransform: "uppercase" }}>Micro lesson</div>
      <div style={{ marginTop: 58, fontSize: 56, fontWeight: 900, lineHeight: 1.18, minHeight: 142 }}>{TEXT.slice(0, chars)}<span style={{ opacity: cursor ? 1 : 0 }}>|</span></div>
      <div style={{ marginTop: 48, transform: `translateY(${24 * (1 - chip)}px)`, opacity: chip, display: "inline-block", padding: "22px 28px", borderRadius: 20, backgroundColor: "#18181b", border: "1px solid #a78bfa", fontSize: 34, fontWeight: 900 }}>w = w - eta * grad(loss)</div>
    </AbsoluteFill>
  );
};
