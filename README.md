# autoresearch_remotion_finetune

Mac-friendly MLX LoRA fine-tuning scaffold for **Remotion code generation**.

This repo is a clean Remotion base for training and benchmarking small code-generation adapters:

- JSON or HF dataset ingestion
- train/valid/test split building
- MLX LoRA training
- held-out loss evaluation
- local and OpenRouter benchmark comparison
- HF dataset export

The contract and verifier are Remotion-specific:

- dataset rows describe runnable Remotion TSX components
- evaluation checks component export detection
- verification uses a small Remotion runner and attempts a bundle plus optional still or video render

## Scope

This first scaffold intentionally targets a narrow Remotion task:

- one TSX snippet per sample
- one exported component
- React + Remotion packages only
- fixed duration, fps, and frame size stored per case
- inline styles and no arbitrary third-party dependencies

Keeping the first target narrow makes automated verification practical and gives the dataset a consistent shape.

## Structure

- `remotion_pipeline/`: training, dataset, inference, eval, and benchmark code
- `runner/`: small Remotion workspace used by the verifier
- `docs/dataset-strategy.md`: licensing and data-source plan
- `docs/eval-and-rendering.md`: render verification and backend integration plan
- `docs/rating-workflow.md`: OpenRouter candidate generation and human rating flow
- `docs/prompt-template.md`: style-aware prompt template for learning artifacts
- `scripts/export_prompt_history_to_cases.py`: converts prompt-to-motion-graphics history exports into training cases
- `scripts/build_codex_synthetic_dataset.py`: builds the Codex-authored synthetic JSONL dataset from readable TSX templates
- `data/generation_prompts/`: first-party prompt bank for remote candidate generation
- `data/style_profiles/`: style profiles used to expand learning-app prompts
- `data/synthetic/`: synthetic dataset manifest and template completions
- `data/remotion_codex_synthetic_cases.jsonl`: current canonical synthetic training source
- `data/remotion_seed_cases.json`: starter local seed set
- `configs/qwen25coder_3b_remotion.json`: starter MLX config

## Setup

Python:

```bash
uv sync
```

Runner dependencies:

```bash
cd runner
npm install
cd ..
```

## Quick Start

Regenerate the current synthetic dataset from all Codex manifests:

```bash
uv run python scripts/build_codex_synthetic_dataset.py
```

Build the dataset:

```bash
uv run python -m remotion_pipeline.cli build-dataset \
  --config configs/qwen25coder_3b_remotion.json
```

Verify the source cases compile and render:

```bash
uv run python -m remotion_pipeline.cli verify-source \
  --config configs/qwen25coder_3b_remotion.json
```

Generate remote model candidates for human rating:

```bash
uv run python scripts/build_style_prompt_bank.py

uv run python -m remotion_pipeline.cli generate-candidates \
  --config configs/qwen25coder_3b_remotion.json \
  --prompts data/generation_prompts/remotion_learning_app_style_prompts.jsonl \
  --output-dir artifacts/candidates/learning-app-v1 \
  --model "<openrouter-model-id>" \
  --samples-per-prompt 1 \
  --max-tokens 4000 \
  --reasoning-effort minimal \
  --exclude-reasoning
```

A smaller niche-diverse prompt bank for frontier remote candidate generation lives at:

```bash
data/generation_prompts/remotion_frontier_niche_prompts.jsonl
```

Current OpenRouter frontier benchmark config:

```bash
uv run python -m remotion_pipeline.cli benchmark \
  --config configs/openrouter_frontier_remotion.json
```

Current OpenRouter candidate checkpoint:

- Merged review queue: `artifacts/candidates/openrouter-frontier-merged-v1`
- Second merged review queue: `artifacts/candidates/openrouter-frontier-round2-merged-v1`
- Prompt banks: 20 niche-diverse Remotion prompts across two rounds
- Verification gates: compile, render, required snippets, forbidden snippets, ASCII-only source, and <=300 LOC
- Current merged sets: 20/20 pass all gates, mean source length about `235` LOC

Merge successful retries into a single review queue:

```bash
uv run python scripts/merge_verified_candidates.py \
  --prompt-bank data/generation_prompts/remotion_frontier_niche_prompts.jsonl \
  --output-dir artifacts/candidates/openrouter-frontier-merged-v1 \
  --source artifacts/candidates/openrouter-frontier-gpt54mini-compact-v1 \
  --source artifacts/candidates/openrouter-frontier-gpt53codex-retry-v1 \
  --source artifacts/candidates/openrouter-frontier-gpt53codex-retry-v2 \
  --source artifacts/candidates/openrouter-frontier-gpt54mini-ascii-retry-v1 \
  --source artifacts/candidates/openrouter-frontier-gpt53codex-healthcare-retry-v1
```

Run a local latency and stop-behavior benchmark:

```bash
uv run python -m remotion_pipeline.cli latency-benchmark \
  --config configs/local_mlx_latency_benchmark.json
```

Sweep generation caps against quality and latency:

```bash
uv run python scripts/run_quality_speed_sweep.py --cap 700 --cap 900 --cap 1200
```

Rescore an existing eval artifact without generating new model output:

```bash
uv run python scripts/rescore_generation_artifact.py \
  --config configs/qwen25coder_3b_remotion.json \
  --input artifacts/evals/qwen25coder-3b-remotion-fixed-eval-current.json \
  --output artifacts/evals/qwen25coder-3b-remotion-fixed-eval-current-quality-rescore.json
```

Run verified quality mode: generate once with the fast default decoder, render-check it, and retry failures with the alternate decoder:

```bash
uv run python scripts/run_verified_retry_eval.py \
  --config configs/qwen25coder_3b_remotion.json \
  --dataset-dir artifacts/datasets/remotion-fixed-eval
```

Run max-quality verified mode with staged fallback decoders:

```bash
uv run python scripts/run_verified_retry_eval.py \
  --config configs/qwen25coder_3b_remotion.json \
  --dataset-dir artifacts/datasets/remotion-fixed-eval \
  --retry 0.6,0.75,42 \
  --retry 0.6,0.75,123 \
  --retry 1.0,0.8,42
```

Run the current recommended adaptive quality profile, which routes known prompt families to the fallback most likely to pass and only uses staged backups when that fallback still fails:

```bash
uv run python scripts/run_verified_retry_eval.py \
  --config configs/qwen25coder_3b_remotion.json \
  --dataset-dir artifacts/datasets/remotion-fixed-eval \
  --adaptive-profile fixed-eval-v1
```

Run the faster routed-primary quality profile, which uses the prompt-family route for the first generation and keeps adaptive verified retries as a safety net:

```bash
uv run python scripts/run_verified_retry_eval.py \
  --config configs/qwen25coder_3b_remotion.json \
  --dataset-dir artifacts/datasets/remotion-fixed-eval \
  --primary-profile fixed-eval-v1 \
  --adaptive-profile fixed-eval-v1
```

Generate and verify one arbitrary prompt with the same routed-primary profile:

```bash
uv run python scripts/generate_verified_remotion.py \
  --prompt "Create a compact Remotion KPI strip with three revenue metric cards, a tiny sparkline, and a green status badge." \
  --output artifacts/generated/kpi-strip-verified.tsx \
  --eval-output artifacts/evals/verified-generation-kpi-strip.json \
  --primary-profile fixed-eval-v1 \
  --adaptive-profile fixed-eval-v1
```

This command exits nonzero and does not write the TSX output unless the selected attempt compiles and render-verifies. Use `--allow-unverified-output` only when debugging failed attempts.

Current local checkpoint and 42-case expansion status:

- Adapter: `artifacts/adapters/qwen25coder-3b-remotion`
- Dataset source: 42 synthetic cases, including 18 `codex-gpt-5.5` authored cases and 7 targeted repair cases
- Source verification: 42/42 compile and render
- Active adapter remains the recovered 35-case checkpoint, best validation checkpoint step 40, validation loss `0.602`
- Fixed 20-case behavior eval for the active adapter: 14/20 compile and render, mean score `0.7798`, token ceiling rate `0.15`
- Verified retry quality mode on the same fixed eval: 18/20 compile and render, mean score `0.8917`, retry rate `0.20`, mean attempt count `1.30`, selected token ceiling rate `0.05`
- Max-quality multi-retry mode on the same fixed eval: 20/20 compile and render, mean score `0.9492`, retry rate `0.30`, mean attempt count `1.45`, selected token ceiling rate `0.0`
- Adaptive max-quality mode on the same fixed eval: 20/20 compile and render, mean score `0.9492`, retry rate `0.30`, mean attempt count `1.30`, selected token ceiling rate `0.0`, mean total generation wall `19.07s`
- Routed-primary adaptive mode on the same fixed eval: 20/20 compile and render, mean score `0.9492`, retry rate `0.0`, mean attempt count `1.0`, selected token ceiling rate `0.0`, mean total generation wall `13.35s`
- Held-out 35-case split eval with `temperature=0.5`, `top_p=0.8`: 3/6 compile and render, mean score `0.6167`, token ceiling rate `0.1667`
- Held-out base-model eval on the same split: 0/6 compile and render, mean score `0.175`
- Local adapter latency benchmark on 5 warmed samples: mean TTFT `0.189s`, mean wall `15.51s`, about `44.8` generated tokens/sec end-to-end
- A 16-layer LoRA trial on the 30-case dataset reached lower validation loss (`0.650`) but lower held-out score, so the 12-layer adapter remains the active target
- 42-case LoRA trials were not promoted: 12-layer `lr=6e-5` reached 6/7 render on the shuffled split but fell to 11/20 render on the fixed behavior eval; 12-layer `lr=8e-5`, 8-layer `lr=6e-5`, cap `800`, and the hook-scope prompt variant also regressed quality
- Decoder sweep result: `temperature=0.6`, `top_p=0.75` repaired 4/6 known fixed-eval failures as a retry decoder, `temperature=0.6`, `top_p=0.75`, `seed=123` repaired the KPI strip, and `temperature=1.0`, `top_p=0.8` repaired manufacturing OEE. The adaptive profile skips wasted intermediate fallbacks for those prompt families, but keeps staged backups for arbitrary prompts that still fail.
- Speculative decoding with `mlx-community/Qwen2.5-Coder-0.5B-Instruct-4bit` is implemented as a benchmark target but not promoted: it improved one 4-case latency sample's wall time while dropping the fixed 20-case eval to 11/20 compile/render.

Run one end-to-end experiment:

```bash
uv run python -m remotion_pipeline.cli run \
  --config configs/qwen25coder_3b_remotion.json
```

Re-run evaluation only:

```bash
uv run python -m remotion_pipeline.cli eval \
  --config configs/qwen25coder_3b_remotion.json
```

Export a history capture from the Remotion prompt dataset app into canonical case rows:

```bash
uv run python scripts/export_prompt_history_to_cases.py \
  --input /path/to/remotion-generations.jsonl \
  --output data/remotion_history_cases.jsonl \
  --row-license MIT
```

Then point the config at that file using `--source`:

```bash
uv run python -m remotion_pipeline.cli build-dataset \
  --config configs/qwen25coder_3b_remotion.json \
  --source data/remotion_history_cases.jsonl
```

## Verification Model

The evaluator does not treat plain string matching as enough.

For each generated sample it:

1. extracts code
2. detects whether a valid component export exists
3. writes the snippet into `runner/`
4. bundles the Remotion project
5. optionally renders a still frame or video
6. combines compile and render success with required or forbidden snippet checks

This is still narrower than full Remotion generation, but it is the right first target: a render-verified adapter for self-contained Remotion components.

## Data Direction

The clean path is first-party data: owned prompt-history exports, hand-authored seed rows, and reviewed Codex-generated examples. Public code corpora can help as auxiliary data only after license filtering and provenance preservation.

The default config now uses `data/remotion_codex_synthetic_cases.jsonl`, generated from readable templates in `data/synthetic/templates/`. Dataset splits are chat-only records, so `mlx_lm` uses the model chat template and includes the assistant end-of-message token during training. The row metadata marks the source as `codex-synthetic-v1` so exported datasets can disclose that they are synthetic.

See `docs/dataset-strategy.md`, `docs/eval-and-rendering.md`, and `docs/rating-workflow.md` for the current plan.
