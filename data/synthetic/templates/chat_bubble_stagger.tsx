import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";

const MESSAGES = [
  { side: "left", text: "What should I review first?", color: "#eef2ff" },
  { side: "right", text: "Start with the two cards you missed yesterday.", color: "#dcfce7" },
  { side: "left", text: "Then one quick quiz?", color: "#eef2ff" },
  { side: "right", text: "Exactly. Short loop, high focus.", color: "#dcfce7" },
];

export const ChatBubbleStagger = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: "#0b1220", padding: 84, fontFamily: "Avenir, sans-serif" }}>
      <div style={{ color: "#f8fafc", fontSize: 48, fontWeight: 800, marginBottom: 42 }}>Study coach thread</div>
      {MESSAGES.map((message, index) => {
        const reveal = spring({ frame: frame - index * 12, fps, config: { damping: 18, stiffness: 130 } });
        const fromRight = message.side === "right";
        return (
          <div key={message.text} style={{ display: "flex", justifyContent: fromRight ? "flex-end" : "flex-start", marginBottom: 22 }}>
            <div style={{ maxWidth: 620, padding: "22px 28px", borderRadius: 30, backgroundColor: message.color, color: "#111827", fontSize: 31, transform: `translateY(${(1 - reveal) * 24}px) scale(${0.96 + reveal * 0.04})`, opacity: reveal }}>
              {message.text}
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
