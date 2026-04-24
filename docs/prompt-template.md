# Prompt Template

Use style-explicit prompts for learning artifacts. Generic prompts let the model fall back to low-contrast dark UI, tiny labels, or decorative motion without a clear educational final state.

## System Contract

```text
Write a single runnable Remotion TSX visual component.
Return only code.
Do not export a Remotion Composition, Root, or registerRoot wrapper.
Do not use CSS transitions, CSS animations, Math.random, external network data, or browser globals.
Drive all motion from useCurrentFrame(), interpolate(), spring(), Sequence, or frame-derived math.
All important text must be readable in a 1280x720 preview.
Essential labels must not use opacity below 0.72.
The midpoint frame must clearly show the main learning artifact.
```

## User Prompt Shape

```text
Create a Remotion learning artifact for: {learning_task}.

Content requirements:
- {concept_or_skill}
- {visual_structure}
- {educational_takeaway}

Style profile: {style_name}.
{style_profile_prompt}

Accessibility and polish constraints:
- high contrast for all important text
- large readable labels
- no gray-on-dark essential labels
- no black intro-only midpoint frames
- no crowded layout
```

## Style Profiles

The repo currently ships these profiles in `data/style_profiles/remotion_learning_styles.json`:

- `clean_light`: white/off-white learning UI, restrained accent, maximum clarity.
- `academic_editorial`: cream paper, dark ink, scholarly annotations.
- `business_dashboard`: professional dashboard and presentation look.
- `colorful_student`: friendly pastel student-facing UI.
- `premium_dark`: dark theme, but strict high contrast.
- `mobile_card`: mobile-first card layout for app artifacts.

Build the styled prompt bank with:

```bash
uv run python scripts/build_style_prompt_bank.py
```
