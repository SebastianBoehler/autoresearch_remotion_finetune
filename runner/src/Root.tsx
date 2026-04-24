import { Composition } from "remotion";
import { GeneratedComposition } from "./GeneratedComposition";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="EvalComp"
        component={GeneratedComposition}
        durationInFrames={90}
        fps={30}
        width={1280}
        height={720}
      />
    </>
  );
};
