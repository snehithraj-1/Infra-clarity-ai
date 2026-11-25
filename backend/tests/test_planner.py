import pytest

from app.planner.planner import create_pipeline_plan
from app.schemas import (
    DegradationMetric,
    DegradationReport,
    EnhanceOptions,
    PresetName,
    Severity,
    StageConfig,
    StageName,
)


@pytest.fixture
def clean_report() -> DegradationReport:
    return DegradationReport(
        blur=DegradationMetric(score=350.0, severity=Severity.LOW, label="Sharp", hint="Sharp focus"),
        haze=DegradationMetric(score=0.08, severity=Severity.LOW, label="Clear", hint="Clear sky"),
        noise=DegradationMetric(score=1.2, severity=Severity.LOW, label="Clean", hint="Low noise"),
        contrast=DegradationMetric(score=0.32, severity=Severity.LOW, label="Good", hint="Good contrast"),
        resolution_flag=False,
        dimensions=[2000, 1500],
        hints=["Image is in good optical condition; minimal enhancement required."],
    )


def test_planner_auto_with_high_haze(clean_report: DegradationReport):
    report = clean_report.model_copy(deep=True)
    report.haze = DegradationMetric(score=0.45, severity=Severity.HIGH, label="Heavy Haze", hint="Dense haze")

    plan = create_pipeline_plan(report, EnhanceOptions(preset=PresetName.AUTO))
    stages = plan.stages

    # Verify stage ordering invariant: dehaze -> denoise -> deblur -> super_resolution
    assert [s.name for s in stages] == [
        StageName.DEHAZE,
        StageName.DENOISE,
        StageName.DEBLUR,
        StageName.SUPER_RESOLUTION,
    ]

    # Dehaze must be enabled and first
    dehaze_stage = stages[0]
    assert dehaze_stage.name == StageName.DEHAZE
    assert dehaze_stage.enabled is True
    assert dehaze_stage.strength >= 70


def test_planner_auto_denoise_before_sharpening(clean_report: DegradationReport):
    report = clean_report.model_copy(deep=True)
    report.noise = DegradationMetric(score=9.5, severity=Severity.HIGH, label="Heavy Noise", hint="Heavy noise")
    report.blur = DegradationMetric(score=40.0, severity=Severity.HIGH, label="Severe Blur", hint="Severe blur")

    plan = create_pipeline_plan(report, EnhanceOptions(preset=PresetName.AUTO))
    stages = plan.stages

    enabled_names = [s.name for s in stages if s.enabled]
    assert StageName.DENOISE in enabled_names
    assert StageName.DEBLUR in enabled_names

    # Invariant: denoise index must be strictly smaller than deblur index
    denoise_idx = next(i for i, s in enumerate(stages) if s.name == StageName.DENOISE)
    deblur_idx = next(i for i, s in enumerate(stages) if s.name == StageName.DEBLUR)
    assert denoise_idx < deblur_idx


def test_planner_auto_resolution_flag_superres_last(clean_report: DegradationReport):
    report = clean_report.model_copy(deep=True)
    report.resolution_flag = True

    plan = create_pipeline_plan(report, EnhanceOptions(preset=PresetName.AUTO))
    stages = plan.stages

    superres = stages[-1]
    assert superres.name == StageName.SUPER_RESOLUTION
    assert superres.enabled is True


def test_planner_presets(clean_report: DegradationReport):
    for preset in [
        PresetName.HAZY_RAINY,
        PresetName.DISTANT_TOWER,
        PresetName.PIPELINE_CLOSEUP,
        PresetName.LOW_LIGHT,
    ]:
        plan = create_pipeline_plan(clean_report, EnhanceOptions(preset=preset))
        assert plan.preset == preset
        assert len(plan.stages) == 4
        # Verify ordering invariant always holds
        assert [s.name for s in plan.stages] == [
            StageName.DEHAZE,
            StageName.DENOISE,
            StageName.DEBLUR,
            StageName.SUPER_RESOLUTION,
        ]


def test_planner_user_override(clean_report: DegradationReport):
    options = EnhanceOptions(
        preset=PresetName.AUTO,
        stages=[
            StageConfig(name=StageName.DEBLUR, enabled=True, strength=90),
            StageConfig(name=StageName.DEHAZE, enabled=False, strength=0),
        ],
    )
    plan = create_pipeline_plan(clean_report, options)
    deblur = next(s for s in plan.stages if s.name == StageName.DEBLUR)
    dehaze = next(s for s in plan.stages if s.name == StageName.DEHAZE)

    assert deblur.enabled is True
    assert deblur.strength == 90
    assert dehaze.enabled is False
