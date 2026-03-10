from __future__ import annotations

from typing import Protocol

from .models import IntuneMapping, SuggestedMapping


class LLMClient(Protocol):
    def suggest_mapping(self, mapping: IntuneMapping) -> dict: ...


class HeuristicLLMClient:
    """Default deterministic stub for environments without an LLM provider."""

    def suggest_mapping(self, mapping: IntuneMapping) -> dict:
        return {
            "suggested_implementation_type": "settings_catalog",
            "suggested_intune_area": "Manual Triage",
            "suggested_setting_name": f"Review {mapping.title}",
            "suggested_value": mapping.value,
            "confidence": 0.35,
            "reasoning": "Heuristic fallback generated because no external LLM client was provided.",
        }


def suggest_manual_review_mappings(
    mappings: list[IntuneMapping],
    client: LLMClient | None = None,
) -> list[SuggestedMapping]:
    llm = client or HeuristicLLMClient()
    suggestions: list[SuggestedMapping] = []

    for mapping in mappings:
        if mapping.implementation_type != "manual_review":
            continue

        suggestion_data = llm.suggest_mapping(mapping)
        suggestions.append(
            SuggestedMapping(
                cis_id=mapping.cis_id,
                title=mapping.title,
                **suggestion_data,
            )
        )

    return suggestions
