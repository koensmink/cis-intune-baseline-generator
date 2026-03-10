from __future__ import annotations

from .models import MappingInputControl, NormalizedControl
from .value_parser import parse_recommendation


def normalize_control(control: MappingInputControl, target: str = "windows_server_2025") -> NormalizedControl:
    parsed = parse_recommendation(control.recommendation or control.default_value)

    normalized_title = " ".join(control.title.split()).strip()
    profile = (control.profile or "Unknown").strip()

    flags = list(parsed.quality_flags)
    if profile.lower() == "unknown":
        flags.append("missing_profile")

    return NormalizedControl(
        control_id=control.control_id,
        title=normalized_title,
        target=target,
        profile=profile,
        assessment=control.assessment,
        recommendation=control.recommendation,
        parsed_recommendation=parsed,
        description=control.description,
        rationale=control.rationale,
        impact=control.impact,
        audit=control.audit,
        remediation=control.remediation,
        default_value=control.default_value,
        references=control.references,
        quality_flags=flags,
    )
