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
