# Human Rating Workflow

The training set should not include every generated candidate. The intended loop is generate, render, rate, then promote.

## Generate Candidates

Use any OpenRouter model IDs you want to compare. Keep model names explicit in the command so provenance is attached to every row.

```bash
uv run python -m remotion_pipeline.cli generate-candidates \
  --config configs/qwen25coder_3b_remotion.json \
  --prompts data/generation_prompts/remotion_learning_app_prompts.jsonl \
  --output-dir artifacts/candidates/learning-app-v1 \
  --model "<xiaomi-pro-openrouter-model-id>" \
  --model "<gpt-5.5-openrouter-model-id>" \
  --samples-per-prompt 1 \
  --max-tokens 12000
```

The command writes:

- `candidates.jsonl`: every generated code sample.
- `rating_queue.jsonl`: editable copy for human ratings.
- `verification.json`: compile/render results.
- `renders/*.png`: preview stills for rating.
- `review.md`: quick index of prompts, models, and preview paths.

## Rate

Edit `rating_queue.jsonl` after looking at the rendered previews.

Use this scale:

- `5`: excellent, visually strong, useful as training data.
- `4`: good, minor taste issues only.
- `3`: acceptable render, but not strong enough for training by default.
- `2`: weak visual result or misses the prompt.
- `1`: broken, ugly, or should not be learned.

Set `human_rating` and optionally `human_notes`. You can also set `rating_decision` to `accept` or `reject`.

## Promote

Promote only high-rated rows into a trainable dataset:

```bash
uv run python -m remotion_pipeline.cli promote-rated-cases \
  --input artifacts/candidates/learning-app-v1/rating_queue.jsonl \
  --output data/remotion_human_approved_cases.jsonl \
  --min-rating 4 \
  --accepted-license MIT
```

Rows that failed compile or render verification are skipped during promotion even if they are rated highly by mistake.

Then train from the approved file:

```bash
uv run python -m remotion_pipeline.cli build-dataset \
  --config configs/qwen25coder_3b_remotion.json \
  --source data/remotion_human_approved_cases.jsonl
```

## Metrics

Candidate rows keep generation latency and token usage from OpenRouter where available. First-token latency is currently recorded as `null` because the generator uses non-streaming requests; streaming telemetry can be added when optimizing serving latency.
