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
- `scripts/export_prompt_history_to_cases.py`: converts prompt-to-motion-graphics history exports into training cases
- `scripts/build_codex_synthetic_dataset.py`: builds the Codex-authored synthetic JSONL dataset from readable TSX templates
- `data/generation_prompts/`: first-party prompt bank for remote candidate generation
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

Regenerate the current synthetic dataset:

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
uv run python -m remotion_pipeline.cli generate-candidates \
  --config configs/qwen25coder_3b_remotion.json \
  --prompts data/generation_prompts/remotion_learning_app_prompts.jsonl \
  --output-dir artifacts/candidates/learning-app-v1 \
  --model "<openrouter-model-id>" \
  --samples-per-prompt 1 \
  --max-tokens 12000
```

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

The default config now uses `data/remotion_codex_synthetic_cases.jsonl`, generated from readable templates in `data/synthetic/templates/`. The row metadata marks the source as `codex-synthetic-v1` so exported datasets can disclose that they are synthetic.

See `docs/dataset-strategy.md`, `docs/eval-and-rendering.md`, and `docs/rating-workflow.md` for the current plan.
