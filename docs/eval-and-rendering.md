# Eval And Rendering Pipeline

The repo already has the minimum viable eval loop: generate Remotion component code, write it into the runner, bundle it, select the composition, then render a frame or video.

## Current Flow

1. Extract the generated TSX component from raw model output.
2. Detect whether a valid named or default component export exists.
3. Write the code to `runner/src/GeneratedComposition.tsx`.
4. Use the Remotion runner to bundle the project.
5. Select composition `EvalComp`.
6. Render a still frame or video, then score compile and render success.

This matches Remotion's own renderer model: `renderStill()` renders a single image frame, `renderMedia()` renders full media, and `selectComposition()` evaluates the target composition from the bundle.

## Next Evaluation Upgrade

The next practical step is not subjective visual grading. It is stronger artifact generation:

- Render three stills per sample: frame `0`, midpoint, and final safe frame.
- Store outputs under ignored `artifacts/eval-renders/<run-id>/<case-id>/`.
- Promote candidates only if all stills render and no browser console errors occur.
- Run full `renderMedia()` only for promoted samples because video rendering is slower.
- Add optional image probes later: blank-frame detection, dominant-color entropy, text visibility, and frame-to-frame motion deltas.

## G-Motion Integration Point

I did not find a clear public Remotion-compatible tool or dataset named `G-Motion`. Treat it as an external backend placeholder until the exact target is identified.

The clean adapter boundary is:

- Backend input: prompt, dimensions, duration, style tags, optional assets.
- Backend output: either Remotion TSX or a small storyboard JSON.
- Conversion: normalize output into a single exported Remotion component.
- Verification: run the same compile, select, still-render, and video-render checks.

This keeps the training repo renderer-agnostic. A future `gmotion` backend should not get special scoring rules until it produces the same canonical case shape.

## Recommended Commands

Verify the canonical source cases before training:

```bash
uv run python -m remotion_pipeline.cli verify-source \
  --config configs/qwen25coder_3b_remotion.json
```

```bash
uv run python -m remotion_pipeline.cli build-dataset \
  --config configs/qwen25coder_3b_remotion.json
```

```bash
cd runner
node scripts/render-check.mjs \
  --entry src/index.ts \
  --composition EvalComp \
  --output render-output.png \
  --mode bundle \
  --frame 5
```
