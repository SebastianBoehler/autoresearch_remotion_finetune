# Dataset Strategy

The safest path is to make the canonical Remotion SFT dataset provenance-first and mostly self-generated.

## Current Finding

I did not find a credible public, Remotion-specific prompt-to-code dataset with a clean MIT/Apache/CC0-style license that is ready to fine-tune on as-is.

Useful public material exists, but it is not a clean substitute for an owned dataset:

- [Remotion's prompt-to-motion-graphics template](https://github.com/remotion-dev/template-prompt-to-motion-graphics-saas) is useful as a product and eval architecture reference, not as a dataset to ingest blindly.
- [Linear-Next/Linear-Next-Datasets](https://huggingface.co/datasets/Linear-Next/Linear-Next-Datasets/viewer) contains at least some Remotion-like TSX snippets, but it appears to be a broad code scrape, not a curated Remotion prompt dataset with row-level provenance suitable for this project.
- [The Stack v2](https://huggingface.co/datasets/bigcode/the-stack-v2) is a serious source-code corpus, but it spans many upstream licenses and requires preserving original-license obligations and provenance. Treat it as optional auxiliary code data only after explicit license filtering.

## Canonical Dataset Sources

Use these sources first:

- `data/remotion_seed_cases.json`: small, hand-authored seed cases owned by this repo.
- `data/remotion_codex_synthetic_cases.jsonl`: current Codex-authored synthetic v1 dataset generated from readable templates.
- `data/generation_prompts/remotion_learning_app_prompts.jsonl`: first-party prompt bank for OpenRouter candidate generation.
- Prompt-history exports from your learning-app or Remotion prompt app, converted via `scripts/export_prompt_history_to_cases.py`.
- Codex-generated examples that are reviewed, rendered, deduplicated, and tagged with `license: MIT` only when they do not copy protected third-party examples.

## License Policy

Every row must carry a `license` field. The default for first-party generated records is `MIT`, but rows imported from external projects must keep their original license and source metadata.

Minimum source metadata:

- `source_name`: where the row came from.
- `source_repo_path`: local or upstream path, commit, export file, or generation batch id.
- `source_model`: generating or editing model where known.
- `source_rating`: human or product feedback where known.
- `tags`: include source, task type, aspect ratio, duration, and verification status.

Do not train on unlicensed public snippets just because they compile. A renderable sample is not automatically a legally clean sample.

## Synthetic Generation Protocol

Synthetic rows should be generated from first principles and public principles, not copied code:

- Use Remotion docs and examples only to understand APIs and common patterns.
- Author completions as original TSX templates under `data/synthetic/templates/`.
- Describe each case in `data/synthetic/codex_manifest.json`.
- Regenerate the JSONL with `scripts/build_codex_synthetic_dataset.py`.
- Keep `source_name`, `source_model`, `synthetic_generation_method`, and `inspiration_sources` in every row.
- Run render verification before promoting a batch for training.

## Scaling Plan

1. Grow seed cases across task classes: typography, charts, chat UI, abstract loops, explainers, product cards, social posts.
2. Generate candidate completions with multiple models and keep only cases passing compile plus still-render checks.
3. Promote high-quality rows after manual review and assign `source_rating: up`.
4. Add a near-duplicate pass before export so one visual trope does not dominate the adapter.
5. Keep a public dataset card strict: disclose row licenses, source types, render checks, and known limitations.

## Candidate Rating

Remote model generations should enter the repo as `pending-human-review`, not as final training data. Use `generate-candidates` to collect rendered outputs, rate them in `rating_queue.jsonl`, then use `promote-rated-cases` to produce a high-quality training source.
