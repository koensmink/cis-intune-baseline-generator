from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ALLOWED_IMPLEMENTATION_TYPES = {
    "settings_catalog": "settings_catalog",
    "administrative_template": "administrative_template",
    "endpoint_security": "endpoint_security",
    "custom_oma_uri": "custom_oma_uri",
    "configuration_profile": "configuration_profile",
    "compliance_policy": "compliance_policy",
    "script": "script",
    "manual_review": "manual_review",
}


IMPLEMENTATION_TYPE_ALIASES = {
    "settings catalog": "settings_catalog",
    "settings_catalog": "settings_catalog",
    "device restrictions": "configuration_profile",
    "device restriction": "configuration_profile",
    "device configuration": "configuration_profile",
    "device configuration profile": "configuration_profile",
    "configuration profile": "configuration_profile",
    "intune configuration profile": "configuration_profile",
    "administrative template": "administrative_template",
    "administrative templates": "administrative_template",
    "endpoint security": "endpoint_security",
    "custom oma-uri": "custom_oma_uri",
    "custom oma uri": "custom_oma_uri",
    "oma-uri": "custom_oma_uri",
    "oma uri": "custom_oma_uri",
    "compliance": "compliance_policy",
    "compliance policy": "compliance_policy",
    "powershell": "script",
    "powershell script": "script",
    "script": "script",
    "manual triage": "manual_review",
    "manual review": "manual_review",
}


ALLOWED_INTUNE_AREAS = {
    "settings_catalog": "Settings Catalog",
    "administrative_template": "Administrative Templates",
    "endpoint_security": "Endpoint Security",
    "custom_oma_uri": "Custom OMA-URI",
    "configuration_profile": "Configuration Profile",
    "compliance_policy": "Compliance Policy",
    "script": "Scripts",
    "manual_review": "Manual Review",
}


AREA_ALIASES = {
    "settings catalog": "Settings Catalog",
    "device restrictions": "Configuration Profile",
    "device restriction": "Configuration Profile",
    "device configuration": "Configuration Profile",
    "device configuration profile": "Configuration Profile",
    "configuration profile": "Configuration Profile",
    "intune configuration profile": "Configuration Profile",
    "administrative template": "Administrative Templates",
    "administrative templates": "Administrative Templates",
    "endpoint security": "Endpoint Security",
    "custom oma-uri": "Custom OMA-URI",
    "custom oma uri": "Custom OMA-URI",
    "compliance policy": "Compliance Policy",
    "compliance": "Compliance Policy",
    "powershell scripts": "Scripts",
    "powershell script": "Scripts",
    "script": "Scripts",
    "manual triage": "Manual Review",
    "manual review": "Manual Review",
}


@dataclass
class NormalizedSuggestion:
    suggested_implementation_type: str
    suggested_intune_area: str
    suggested_setting_name: str
    suggested_value: str
    confidence: float
    reasoning: str
    mapping_source: str
    needs_validation: bool
    normalization_notes: list[str]


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Enabled" if value else "Disabled"
    return str(value).strip()


def _normalize_confidence(value: Any) -> float:
    if value is None:
        return 0.5

    if isinstance(value, (int, float)):
        v = float(value)
        return max(0.0, min(1.0, v))

    text = str(value).strip().lower()

    mapping = {
        "very high": 0.95,
        "high": 0.85,
        "medium": 0.60,
        "moderate": 0.60,
        "low": 0.35,
        "very low": 0.15,
    }
    if text in mapping:
        return mapping[text]

    try:
        v = float(text)
        return max(0.0, min(1.0, v))
    except ValueError:
        return 0.5


def _normalize_implementation_type(value: Any) -> tuple[str, str | None]:
    text = _clean_text(value).lower()
    if text in IMPLEMENTATION_TYPE_ALIASES:
        return IMPLEMENTATION_TYPE_ALIASES[text], None
    if text in ALLOWED_IMPLEMENTATION_TYPES:
        return text, None
    return "manual_review", f"Unknown implementation type '{value}' mapped to manual_review"


def _normalize_intune_area(value: Any, implementation_type: str) -> tuple[str, str | None]:
    text = _clean_text(value).lower()
    if text in AREA_ALIASES:
        return AREA_ALIASES[text], None
    if implementation_type in ALLOWED_INTUNE_AREAS:
        return ALLOWED_INTUNE_AREAS[implementation_type], f"Unknown intune area '{value}' normalized from implementation type"
    return "Manual Review", f"Unknown intune area '{value}' mapped to Manual Review"


def _looks_like_free_text_value(value: str) -> bool:
    if not value:
        return True

    low = value.lower()

    heuristic_markers = [
        "ensure ",
        "review ",
        "compliant if ",
        "secure ",
        "must be ",
        "should be ",
        "verify ",
        "manual ",
        "owner read/write",
        "organization",
        "organizational",
        "pii",
    ]

    if any(marker in low for marker in heuristic_markers):
        return True

    if len(value) > 120:
        return True

    return False


def normalize_suggestion_dict(raw: dict[str, Any]) -> NormalizedSuggestion:
    notes: list[str] = []

    impl, impl_note = _normalize_implementation_type(raw.get("suggested_implementation_type"))
    if impl_note:
        notes.append(impl_note)

    area, area_note = _normalize_intune_area(raw.get("suggested_intune_area"), impl)
    if area_note:
        notes.append(area_note)

    setting_name = _clean_text(raw.get("suggested_setting_name"))
    if not setting_name:
        setting_name = "Manual review required"
        notes.append("Empty suggested_setting_name replaced with default")

    suggested_value = _clean_text(raw.get("suggested_value"))
    confidence = _normalize_confidence(raw.get("confidence"))
    reasoning = _clean_text(raw.get("reasoning"))

    needs_validation = False

    if impl == "manual_review":
        needs_validation = True
        notes.append("Implementation type is manual_review")

    if _looks_like_free_text_value(suggested_value):
        needs_validation = True
        notes.append("Suggested value looks like analyst text instead of a deployable setting value")

    if confidence < 0.70:
        needs_validation = True
        notes.append(f"Low confidence: {confidence:.2f}")

    return NormalizedSuggestion(
        suggested_implementation_type=impl,
        suggested_intune_area=area,
        suggested_setting_name=setting_name,
        suggested_value=suggested_value,
        confidence=confidence,
        reasoning=reasoning,
        mapping_source="llm",
        needs_validation=needs_validation,
        normalization_notes=notes,
    )


def normalize_suggestions(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for record in records:
        core = {
            "cis_id": record.get("cis_id", ""),
            "title": record.get("title", ""),
        }

        ns = normalize_suggestion_dict(record)

        normalized.append(
            {
                **core,
                "suggested_implementation_type": ns.suggested_implementation_type,
                "suggested_intune_area": ns.suggested_intune_area,
                "suggested_setting_name": ns.suggested_setting_name,
                "suggested_value": ns.suggested_value,
                "confidence": ns.confidence,
                "reasoning": ns.reasoning,
                "mapping_source": ns.mapping_source,
                "needs_validation": ns.needs_validation,
                "normalization_notes": "; ".join(ns.normalization_notes),
            }
        )

    return normalized
