import { bundle } from "@remotion/bundler";
import {
  ensureBrowser,
  renderMedia,
  renderStill,
  selectComposition,
} from "@remotion/renderer";
import path from "node:path";

const args = process.argv.slice(2);

const readArg = (name, fallback = null) => {
  const index = args.indexOf(name);
  if (index === -1 || index === args.length - 1) {
    return fallback;
  }
  return args[index + 1];
};

const entryPoint = readArg("--entry", "src/index.ts");
const compositionId = readArg("--composition", "EvalComp");
const output = readArg("--output", "render-output.png");
const mode = readArg("--mode", "bundle");
const frame = Number(readArg("--frame", "15"));

const main = async () => {
  await ensureBrowser();
  const serveUrl = await bundle({
    entryPoint: path.resolve(entryPoint),
  });
  const composition = await selectComposition({
    id: compositionId,
    serveUrl,
    inputProps: {},
  });
  if (mode === "still") {
    await renderStill({
      composition,
      serveUrl,
      output,
      frame,
      inputProps: {},
    });
  } else if (mode === "video") {
    await renderMedia({
      composition,
      serveUrl,
      codec: "h264",
      outputLocation: output,
      inputProps: {},
    });
  }
  process.stdout.write(
    JSON.stringify({
      ok: true,
      compositionId: composition.id,
      durationInFrames: composition.durationInFrames,
      fps: composition.fps,
      width: composition.width,
      height: composition.height,
      mode,
    }),
  );
};

main().catch((error) => {
  process.stderr.write(String(error?.stack || error));
  process.exit(1);
});
