from __future__ import annotations

from ..base import MappingRule
from ...models import IntuneMapping, NormalizedControl


class SecurityOptionsRule(MappingRule):
    rule_id = "windows_server_2025.security_options"

    def matches(self, control: NormalizedControl) -> bool:
        t = control.title.lower()
        return "security option" in t or "consumer experiences" in t

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.control_id,
            title=control.title,
            implementation_type="settings_catalog",
            intune_area="Windows OS Hardening",
            setting_name="Security options",
            value=control.parsed_recommendation.normalized_text or "Enabled",
            confidence=0.85,
            rule_id=self.rule_id,
            parsed_value_type=control.parsed_recommendation.value_type,
            quality_flags=control.quality_flags,
        )
