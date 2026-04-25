# Manim Transfer Notes For Remotion Finetune

Logged: 2026-04-25

This note compares the speed and quality work already tried in `autoresearch_remotion_finetune` with the proven improvements from `autoresearch_manim_finetune`. The goal is to avoid repeating rejected experiments and identify the next Remotion improvements that are still worth applying.

## Current Remotion State

The Remotion repo already has several optimizations that were also valuable in the Manim repo:

- In-process MLX inference with model cache and latency telemetry is implemented.
- Tokenizer-native chat/EOS training records are already used; `case_to_chat_record()` emits only `messages`, not a top-level completion column.
- Dynamic Remotion stop is implemented and enabled for the active local config.
- Fixed broad eval exists: `data/eval/remotion_fixed_eval_cases.jsonl`.
- Decoder sweeps and verified retries are already stronger than the current Manim flow.
- Speculative decoding with `mlx-community/Qwen2.5-Coder-0.5B-Instruct-4bit` was tested and rejected for the active adapter.

Best recorded Remotion checkpoints:

- Single-pass fixed eval: `14/20` compile/render, mean score `0.7798`, token ceiling `0.15`, mean generation `664.35` tokens.
- Routed-primary adaptive eval: `20/20` compile/render, mean score `0.9492`, retry rate `0.0`, mean attempt count `1.0`, mean wall `13.35s`, token ceiling `0.0`.
- Local latency benchmark: LoRA mean wall `23.10s`; speculative 0.5B draft mean wall `18.60s` but lower quality on fixed eval.
- Speculative fixed eval: `11/20` compile/render, mean score `0.6713`, token ceiling `0.30`; do not promote this profile.

## Manim Results Worth Transferring

The latest Manim profile is:

- Qwen2.5-Coder 3B LoRA with in-process MLX.
- 0.5B Qwen 4-bit draft model, `num_draft_tokens=3`.
- High `max_tokens=2560` plus semantic dynamic stop, not a short hard cap.
- Focused 4-case learning-app benchmark: `4/4` syntax/render/quality/production, mean wall `8.018s`, p95 `9.282s`, mean generation `51.63 tok/s`.
- Broad 23-case artifact after deterministic repair/rescore: syntax `20/23`, render `20/20` on syntax-valid cases, production `20/23`, mean score `0.8318`.

The most important Manim improvement was the deterministic repair layer:

- Before repair/rescore: `10/23` production-ready, mean score `0.6911`.
- After runtime repair, syntax repair, and pacing repair: `20/23` production-ready, mean score `0.8318`.
- This was achieved without retraining and without changing the fast inference profile.

## Applied Direction In This Repo

After review, Remotion should not silently repair generated TSX during normal eval or verified generation. The evaluator should score the model output as-is so quality numbers remain attributable to the model and decoder profile. Deterministic repair can be useful as an offline analysis idea, but it is not part of the active eval path.

Transferred now:

- Added a cheap artifact rescore path that re-evaluates stored outputs without paying MLX generation time again.
- Added generation-quality diagnostics for known failure modes without changing the generated code.
- Confirmed no-repair rescore of `qwen25coder-3b-remotion-fixed-eval-current.json` exactly preserves the original fixed-eval metrics: `14/20` compile/render, mean score `0.7798`.

## High-Priority Open Work For Remotion

1. Add deterministic compile/render repair analysis, not automatic repair.

Remotion currently normalizes generated code but does not perform a repair loop like Manim's `render_repair.py`, `syntax_repair.py`, and `pacing_repair.py`. For this repo, keep that as diagnostic analysis unless explicitly requested. The current single-pass fixed eval failures show mechanically classifiable patterns:

- `useCurrentFrame` or other hooks used outside the component body.
- Undefined component/helper names such as `Kpi`.
- `interpolate()` input/output ranges containing non-numeric values.
- React rendering plain objects, e.g. error #31 with `{label, value}`.
- Unterminated strings from generated label text.
- Expected `}` / unexpected EOF from incomplete JSX.

Recommended implementation:

- Keep normal eval and verified generation as output-only scoring.
- Use diagnostics to label failure classes and route future generation or training data.
- Keep every file under 300 LOC by splitting parsing helpers if needed.
- Rescore existing artifacts first, before regenerating.

Expected value:

- This preserves honest model metrics while still capturing which failures are mechanical.
- The labels can drive targeted samples and routing without mutating outputs after generation.

2. Add a cheap rescore-existing-artifact script.

Manim used `scripts/rescore_generation_artifact.py` to evaluate old generations without paying MLX generation time again. Remotion should keep this workflow raw by default: no code mutation before scoring unless an explicitly named experiment asks for it.

Recommended command shape:

```bash
uv run python scripts/rescore_generation_artifact.py \
  --config configs/qwen25coder_3b_remotion.json \
  --input artifacts/evals/qwen25coder-3b-remotion-fixed-eval-current.json \
  --output artifacts/evals/qwen25coder-3b-remotion-fixed-eval-current-rescore.json
```

Expected value:

- Makes scorer and diagnostic iteration fast and measurable.
- Separates inference quality from deterministic verifier changes.

3. Add Remotion generation-quality analysis.

Manim has a generation quality layer for syntax validity, estimated duration, repeated plays, and pacing. Remotion should add an equivalent focused on TSX quality:

- compile/export presence
- approximate animation duration coverage
- token-ceiling and EOF likelihood
- repeated JSX/data blocks
- repeated `interpolate()`/array patterns
- LOC and ASCII gates
- hook scope mistakes

Expected value:

- Better telemetry for why a generation failed.
- Better routing decisions for verified retry profiles.
- Useful training labels for future targeted repair samples.

4. Consider prompt-prefix / cache work later.

Both repos use repeated system prompts and similar Remotion contracts. If MLX prompt-cache support can be reused safely across requests, it could reduce prompt prefill latency. This is lower priority than failure diagnostics because current Remotion latency is dominated by long/failed generations and verification retries, not TTFT.

## Low-Priority Or Rejected For Now

- Do not promote speculative decoding in Remotion yet. It improved a small latency sample but dropped fixed eval to `11/20` render and score `0.6713`.
- Do not globally lower caps. Remotion already rejected cap `700`, and cap `800` regressed fixed eval. Current cap `900` plus routed profiles is safer.
- Do not blindly raise caps either. Cap `1200` did not improve tested outputs. Use targeted long retries only for prompt families that need them.
- Do not repeat broad system-prompt hardening. A hook-scope/plain-array prompt experiment collapsed fixed eval to `0/6` and was reverted.
- Do not promote the Manim repetition/frequency penalty setting. In Manim, `repetition_penalty=1.08` and `frequency_penalty=0.02` regressed latency from `8.018s` to `9.342s` mean and increased output tokens.

## Suggested Next Sequence

1. Implement Remotion compile/render failure analysis with unit tests around the known fixed-eval failure patterns.
2. Keep the rescore-existing-artifact script raw by default and use it on `qwen25coder-3b-remotion-fixed-eval-current.json`.
3. Use the diagnostics to add targeted training samples or routed decoder profiles.
4. Only after raw single-pass quality improves, re-test speculative decoding; it may become viable if the model stops producing the currently fragile patterns.
5. Keep collecting targeted samples for failures the model should learn to avoid.
