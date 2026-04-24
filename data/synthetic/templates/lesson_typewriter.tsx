import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

const TITLE = "Gradient descent turns error into direction.";
const SUBTITLE = "Each frame reveals a little more of the idea.";

export const LessonTypewriter = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const shownTitle = Math.floor(
    interpolate(frame, [0, 2.4 * fps], [0, TITLE.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  );
  const subtitleOpacity = interpolate(frame, [2.5 * fps, 3.4 * fps], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cursorVisible = Math.floor(frame / 10) % 2 === 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#101828", justifyContent: "center", padding: 96, color: "#f9fafb", fontFamily: "Georgia, serif" }}>
      <div style={{ fontSize: 72, lineHeight: 1.05, maxWidth: 980, fontWeight: 700 }}>
        {TITLE.slice(0, shownTitle)}
        <span style={{ opacity: cursorVisible ? 1 : 0, color: "#84cc16" }}>|</span>
      </div>
      <div style={{ marginTop: 34, fontSize: 32, opacity: subtitleOpacity, color: "#cbd5e1", fontFamily: "Avenir, sans-serif" }}>
        {SUBTITLE}
      </div>
    </AbsoluteFill>
  );
};
