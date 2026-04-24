import { AbsoluteFill, Sequence, spring, useCurrentFrame, useVideoConfig } from "remotion";

const STEPS = [
  { title: "Capture", caption: "Turn the lecture into cards.", color: "#fde68a" },
  { title: "Practice", caption: "Answer before seeing hints.", color: "#bfdbfe" },
  { title: "Reflect", caption: "Patch the weakest concept.", color: "#fecdd3" },
];

const StepCard = ({ title, caption, color }: { title: string; caption: string; color: string }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 16, stiffness: 150 } });
  return (
    <div style={{ width: 620, padding: 42, borderRadius: 34, backgroundColor: color, color: "#111827", transform: `scale(${0.9 + pop * 0.1})`, boxShadow: "0 28px 70px rgba(0,0,0,0.22)" }}>
      <div style={{ fontSize: 58, fontWeight: 900 }}>{title}</div>
      <div style={{ marginTop: 18, fontSize: 30, lineHeight: 1.25 }}>{caption}</div>
    </div>
  );
};

export const RoadmapSequence = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#1e1b4b", justifyContent: "center", alignItems: "center", fontFamily: "Avenir, sans-serif" }}>
      {STEPS.map((step, index) => (
        <Sequence key={step.title} from={index * 32} durationInFrames={76} premountFor={30}>
          <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", transform: `translateX(${(index - 1) * 230}px)` }}>
            <StepCard title={step.title} caption={step.caption} color={step.color} />
          </AbsoluteFill>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
