import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";

const OPTIONS = [
  { label: "A", text: "More examples", correct: false },
  { label: "B", text: "Active recall", correct: true },
  { label: "C", text: "Longer notes", correct: false },
];

export const QuizAnswerReveal = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const reveal = spring({ frame: frame - 48, fps, config: { damping: 18, stiffness: 130 } });

  return (
    <AbsoluteFill style={{ backgroundColor: "#fff7ed", padding: 82, color: "#1c1917", fontFamily: "Avenir, sans-serif" }}>
      <div style={{ fontSize: 48, fontWeight: 900, maxWidth: 980 }}>Which technique improves retrieval strength fastest?</div>
      <div style={{ display: "flex", gap: 24, marginTop: 58 }}>
        {OPTIONS.map((option) => {
          const active = option.correct ? reveal : 0;
          return (
            <div key={option.label} style={{ flex: 1, padding: 30, minHeight: 210, borderRadius: 28, backgroundColor: option.correct ? "#bbf7d0" : "#ffffff", border: `${4 + active * 4}px solid ${option.correct ? "#16a34a" : "#e7e5e4"}`, transform: `translateY(${-active * 18}px)`, boxShadow: `0 ${12 + active * 18}px 40px rgba(0,0,0,${0.08 + active * 0.08})` }}>
              <div style={{ fontSize: 30, fontWeight: 900 }}>{option.label}</div>
              <div style={{ marginTop: 28, fontSize: 34, fontWeight: 800 }}>{option.text}</div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
