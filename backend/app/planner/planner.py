from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas import (
    DegradationReport,
    EnhanceOptions,
    PresetName,
    Severity,
    StageConfig,
    StageName,
)


class PlannedStage(BaseModel):
    name: StageName
    enabled: bool
    strength: int = Field(ge=0, le=100)
    engine: str = "classical"
    reason: str


class PipelinePlan(BaseModel):
    preset: PresetName
    stages: List[PlannedStage]
    rationale: List[str]


def create_pipeline_plan(
    report: DegradationReport,
    options: Optional[EnhanceOptions] = None,
) -> PipelinePlan:
    """
    Constructs an optimal, ordered enhancement pipeline based on degradation analysis,
    selected preset, and explicit user overrides.

    Ordering Invariants:
    1. Dehaze must execute first if haze is present to restore ambient light and contrast.
    2. Denoise must precede sharpening and super-resolution to prevent amplifying sensor grain.
    3. Deblur recovers edge acuity on the clean, dehazed image.
    4. Super-resolution must execute last to upscale the restored signal.
    """
    if options is None:
        options = EnhanceOptions(preset=PresetName.AUTO)

    preset = options.preset
    stage_override_map: Dict[str, StageConfig] = {}
    if options.stages:
        for s in options.stages:
            stage_override_map[s.name.value] = s

    planned_stages: List[PlannedStage] = []
    rationale: List[str] = []

    # Preset Base Configurations
    if preset == PresetName.HAZY_RAINY:
        stages_proto = [
            (StageName.DEHAZE, True, 85, "Hazy/Rainy preset: aggressive dark channel dehazing"),
            (StageName.DENOISE, True, 50, "Hazy/Rainy preset: suppress rain particulate noise"),
            (StageName.DEBLUR, True, 55, "Hazy/Rainy preset: structural edge re-acuity"),
            (StageName.SUPER_RESOLUTION, report.resolution_flag, 60, "Hazy/Rainy preset: optional upscale"),
        ]
        rationale.append("Applied 'Hazy / Rainy Weather' inspection preset.")

    elif preset == PresetName.DISTANT_TOWER:
        stages_proto = [
            (StageName.DEHAZE, True, 75, "Distant Tower preset: distance haze removal & contrast recovery"),
            (StageName.DENOISE, True, 35, "Distant Tower preset: low-pass noise floor cleaning"),
            (StageName.DEBLUR, True, 75, "Distant Tower preset: correct telephoto lens motion blur & edge acuity"),
            (StageName.SUPER_RESOLUTION, True, 75, "Distant Tower preset: x2 magnification & micro-detailing"),
        ]
        rationale.append("Applied 'Distant Tower' inspection preset for telephoto structural imagery.")

    elif preset == PresetName.PIPELINE_CLOSEUP:
        stages_proto = [
            (StageName.DEHAZE, False, 0, "Pipeline Close-up preset: dehaze omitted for macro surface"),
            (StageName.DENOISE, True, 45, "Pipeline Close-up preset: clean surface sensor grain"),
            (StageName.DEBLUR, True, 85, "Pipeline Close-up preset: high-pass unsharp mask for hairline cracks"),
            (StageName.SUPER_RESOLUTION, report.resolution_flag, 65, "Pipeline Close-up preset: resolution boost"),
        ]
        rationale.append("Applied 'Pipeline Close-up' preset optimized for surface rust and hairline cracks.")

    elif preset == PresetName.LOW_LIGHT:
        stages_proto = [
            (StageName.DEHAZE, True, 75, "Low Light preset: CLAHE dynamic range expansion in LAB space"),
            (StageName.DENOISE, True, 70, "Low Light preset: aggressive sensor chroma/luma noise reduction"),
            (StageName.DEBLUR, True, 60, "Low Light preset: restore softened shadow edges"),
            (StageName.SUPER_RESOLUTION, report.resolution_flag, 60, "Low Light preset: super-resolution"),
        ]
        rationale.append("Applied 'Low Light' inspection preset to boost underexposed shadow details.")

    else:  # AUTO Preset (Close-Range Crystal-Clear Standard)
        stages_proto = []
        # Rule 1: Dehaze - always clear atmospheric wash & distance fog
        if report.haze.severity == Severity.HIGH:
            stages_proto.append((StageName.DEHAZE, True, 85, "Severe atmospheric haze detected; aggressive dehazing first"))
            rationale.append("Dehazing prioritized first to restore contrast before downstream processing.")
        elif report.haze.severity == Severity.MEDIUM:
            stages_proto.append((StageName.DEHAZE, True, 70, "Moderate haze detected; applying transmission & contrast recovery"))
            rationale.append("Moderate haze detected; applying transmission recovery and contrast stretching.")
        else:
            stages_proto.append((StageName.DEHAZE, True, 50, "Baseline atmospheric clearance: eliminates milky wash for close-range contrast"))
            rationale.append("Baseline atmospheric clearance applied for close-range optical contrast.")

        # Rule 2: Denoise - always eliminate 100% of sensor noise, ISO grain, and particulate
        if report.noise.severity == Severity.HIGH:
            stages_proto.append((StageName.DENOISE, True, 80, "Heavy sensor noise detected; aggressive denoising before sharpening"))
            rationale.append("Denoising scheduled before sharpening to prevent noise grain amplification.")
        elif report.noise.severity == Severity.MEDIUM:
            stages_proto.append((StageName.DENOISE, True, 65, "Moderate sensor noise present; cleaning noise floor"))
            rationale.append("Denoising enabled to clean sensor baseline and grain.")
        else:
            stages_proto.append((StageName.DENOISE, True, 55, "Full-spectrum noise removal: scrubs sensor noise floor and compression artifacts"))
            rationale.append("Full-spectrum noise removal active to ensure smooth, noise-free surfaces.")

        # Rule 3: Deblur - always restore close-range structural acuity
        if report.blur.severity == Severity.HIGH:
            stages_proto.append((StageName.DEBLUR, True, 85, "Severe blur detected; applying deblurring"))
            rationale.append("Severe blur detected; unsharp masking scheduled to reveal defect boundaries.")
        elif report.blur.severity == Severity.MEDIUM:
            stages_proto.append((StageName.DEBLUR, True, 75, "Moderate blur detected; applying edge restoration"))
            rationale.append("Moderate blur detected; applying edge restoration.")
        else:
            stages_proto.append((StageName.DEBLUR, True, 65, "Close-range structural edge re-acuity for fine inspection detail"))
            rationale.append("Baseline structural edge re-acuity scheduled for lattice fasteners and fine boundaries.")

        # Rule 4: Super-Resolution - always reconstruct close-range neural patterns
        if report.resolution_flag:
            stages_proto.append((StageName.SUPER_RESOLUTION, True, 80, "Image resolution is under 1080p; neural super-resolution"))
            rationale.append("Sub-1080p image flagged; neural super-resolution scheduled as final stage.")
        else:
            stages_proto.append((StageName.SUPER_RESOLUTION, True, 70, "Deep neural super-resolution: close-range macro texture reconstruction"))
            rationale.append("Deep neural super-resolution active for close-range macro pattern synthesis.")

    # Apply manual overrides while strictly preserving pipeline stage ordering:
    # 1. DEHAZE -> 2. DENOISE -> 3. DEBLUR -> 4. SUPER_RESOLUTION
    ordered_stage_names = [
        StageName.DEHAZE,
        StageName.DENOISE,
        StageName.DEBLUR,
        StageName.SUPER_RESOLUTION,
    ]

    proto_dict = {name: (en, st, rz) for name, en, st, rz in stages_proto}

    for stage_name in ordered_stage_names:
        default_enabled, default_strength, default_reason = proto_dict.get(
            stage_name, (False, 50, "Default configuration")
        )

        if stage_name.value in stage_override_map:
            override = stage_override_map[stage_name.value]
            planned_stages.append(
                PlannedStage(
                    name=stage_name,
                    enabled=override.enabled,
                    strength=override.strength,
                    engine=override.engine,
                    reason=f"User override ({'enabled' if override.enabled else 'disabled'}, strength={override.strength})",
                )
            )
        else:
            from app.enhance.registry import registry
            stage_inst = registry.get_stage(stage_name.value)
            engine_type = stage_inst.engine_type if stage_inst else "classical"
            planned_stages.append(
                PlannedStage(
                    name=stage_name,
                    enabled=default_enabled,
                    strength=default_strength,
                    engine=engine_type,
                    reason=default_reason,
                )
            )

    return PipelinePlan(
        preset=preset,
        stages=planned_stages,
        rationale=rationale,
    )
