from remotion_pipeline.generation_quality import analyze_generation_quality


def test_generation_quality_flags_known_mechanical_failures() -> None:
    signals = analyze_generation_quality(
        code=(
            "const BADGES_ANIMATION = interpolate(useCurrentFrame(), [0, 30], [0, 1]);\n"
            "<animated.div />\n"
            "const KpiStrip = () => <div />;\n"
            "export default Kpi\n"
        ),
        render_log_tail="ReferenceError: Kpi is not defined",
    )

    assert signals.top_level_hook_call
    assert signals.animated_namespace
    assert signals.undefined_export_name


def test_generation_quality_flags_runtime_interpolate_and_object_errors() -> None:
    signals = analyze_generation_quality(
        code='const value = interpolate(frame, [0, item.label], [0, 1]);\n',
        render_log_tail="inputRange must contain only numbers\nReact error #31",
    )

    assert signals.non_numeric_interpolate_range
    assert signals.object_render_error


def test_generation_quality_flags_missing_spring_fps() -> None:
    signals = analyze_generation_quality(
        code='const value = spring({frame, from: 0, to: 1});',
        render_log_tail='Error: "fps" must be a number',
    )

    assert signals.spring_missing_fps


def test_generation_quality_allows_late_default_exported_component_hooks() -> None:
    signals = analyze_generation_quality(
        code="""import { useCurrentFrame } from "remotion";

const Demo = () => {
  const frame = useCurrentFrame();
  return <div>{frame}</div>;
};

export default Demo;
""",
    )

    assert not signals.top_level_hook_call


def test_generation_quality_allows_lowercase_default_exported_component_hooks() -> None:
    signals = analyze_generation_quality(
        code="""import { useCurrentFrame } from "remotion";

const radar = () => {
  const frame = useCurrentFrame();
  return <div>{frame}</div>;
};

export default radar;
""",
    )

    assert not signals.top_level_hook_call
