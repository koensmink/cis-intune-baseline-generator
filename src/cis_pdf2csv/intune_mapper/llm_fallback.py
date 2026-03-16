from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Protocol

from .models import IntuneMapping, SuggestedMapping


class LLMClient(Protocol):
    def suggest_mapping(self, mapping: IntuneMapping) -> dict: ...
    def suggest_mappings_batch(self, mappings: list[IntuneMapping]) -> list[dict]: ...


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

    def suggest_mappings_batch(self, mappings: list[IntuneMapping]) -> list[dict]:
        return [self.suggest_mapping(m) for m in mappings]


class OpenAILLMClient:
    """
    OpenAI-backed fallback mapper with:
    - lazy import of openai
    - batch suggestion support
    - simple file cache
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4.1-mini",
        cache_path: str | Path | None = None,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError(
                "The 'openai' package is not installed. "
                "Install it first or rebuild the container with the updated dependencies."
            ) from e

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.cache_path = Path(cache_path) if cache_path else None
        self._cache: dict[str, dict] = {}

        if self.cache_path:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            if self.cache_path.exists():
                try:
                    self._cache = json.loads(self.cache_path.read_text(encoding="utf-8"))
                except Exception:
                    self._cache = {}

    def _cache_key(self, mapping: IntuneMapping) -> str:
        raw = json.dumps(
            {
                "cis_id": mapping.cis_id,
                "title": mapping.title,
                "implementation_type": mapping.implementation_type,
                "intune_area": mapping.intune_area,
                "setting_name": mapping.setting_name,
                "value": mapping.value,
                "notes": mapping.notes,
                "parsed_value_type": mapping.parsed_value_type,
                "quality_flags": mapping.quality_flags,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _save_cache(self) -> None:
        if self.cache_path:
            self.cache_path.write_text(
                json.dumps(self._cache, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def suggest_mapping(self, mapping: IntuneMapping) -> dict:
        return self.suggest_mappings_batch([mapping])[0]

    def suggest_mappings_batch(self, mappings: list[IntuneMapping]) -> list[dict]:
        if not mappings:
            return []

        uncached: list[IntuneMapping] = []
        results: list[dict | None] = [None] * len(mappings)

        for idx, mapping in enumerate(mappings):
            key = self._cache_key(mapping)
            cached = self._cache.get(key)
            if cached:
                results[idx] = cached
            else:
                uncached.append(mapping)

        if uncached:
            generated = self._call_openai_batch(uncached)
            generated_iter = iter(generated)

            for idx, mapping in enumerate(mappings):
                if results[idx] is None:
                    value = next(generated_iter)
                    key = self._cache_key(mapping)
                    self._cache[key] = value
                    results[idx] = value

            self._save_cache()

        return [r for r in results if r is not None]

    def _call_openai_batch(self, mappings: list[IntuneMapping]) -> list[dict]:
        system_prompt = (
            "You map CIS security controls to Microsoft Intune implementation candidates. "
            "Return only valid JSON as an object with a top-level key named 'suggestions'. "
            "The value of 'suggestions' must be an array. "
            "Each array item must contain: "
            "cis_id, suggested_implementation_type, suggested_intune_area, "
            "suggested_setting_name, suggested_value, confidence, reasoning. "
            "Confidence must be a float between 0.0 and 1.0. "
            "Be conservative. If uncertain, set suggested_intune_area to 'Manual Triage'."
        )

        payload = []
        for m in mappings:
            payload.append(
                {
                    "cis_id": m.cis_id,
                    "title": m.title,
                    "implementation_type": m.implementation_type,
                    "intune_area": m.intune_area,
                    "setting_name": m.setting_name,
                    "value": m.value,
                    "notes": m.notes,
                    "parsed_value_type": m.parsed_value_type,
                    "quality_flags": m.quality_flags,
                }
            )

        user_prompt = json.dumps(payload, ensure_ascii=False, indent=2)

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Generate mapping suggestions for these manual-review CIS controls. "
                        "Return JSON with one top-level key: 'suggestions', "
                        "containing an array of suggestion objects.\n\n"
                        f"{user_prompt}"
                    ),
                },
            ],
        )

        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        suggestions = data.get("suggestions", [])

        normalized: list[dict] = []
        by_id = {m.cis_id: m for m in mappings}

        for item in suggestions:
            cis_id = item.get("cis_id")
            original = by_id.get(cis_id)

            if original is None:
                continue

            normalized.append(
                {
                    "suggested_implementation_type": item.get(
                        "suggested_implementation_type", "settings_catalog"
                    ),
                    "suggested_intune_area": item.get(
                        "suggested_intune_area", "Manual Triage"
                    ),
                    "suggested_setting_name": item.get(
                        "suggested_setting_name", f"Review {original.title}"
                    ),
                    "suggested_value": item.get("suggested_value", original.value),
                    "confidence": float(item.get("confidence", 0.50)),
                    "reasoning": item.get("reasoning", "Generated by OpenAI fallback."),
                }
            )

        while len(normalized) < len(mappings):
            original = mappings[len(normalized)]
            normalized.append(
                {
                    "suggested_implementation_type": "settings_catalog",
                    "suggested_intune_area": "Manual Triage",
                    "suggested_setting_name": f"Review {original.title}",
                    "suggested_value": original.value,
                    "confidence": 0.35,
                    "reasoning": "OpenAI response incomplete; fallback suggestion generated.",
                }
            )

        return normalized


def suggest_manual_review_mappings(
    mappings: list[IntuneMapping],
    client: LLMClient | None = None,
) -> list[SuggestedMapping]:
    llm = client or HeuristicLLMClient()
    manual_review = [m for m in mappings if m.implementation_type == "manual_review"]

    if not manual_review:
        return []

    suggestion_data = llm.suggest_mappings_batch(manual_review)
    suggestions: list[SuggestedMapping] = []

    for mapping, data in zip(manual_review, suggestion_data):
        suggestions.append(
            SuggestedMapping(
                cis_id=mapping.cis_id,
                title=mapping.title,
                **data,
            )
        )

    return suggestions
