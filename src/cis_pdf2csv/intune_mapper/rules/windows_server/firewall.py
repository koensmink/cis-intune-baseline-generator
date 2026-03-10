from __future__ import annotations

from ..base import MappingRule
from ...models import IntuneMapping, NormalizedControl


class FirewallRule(MappingRule):
    rule_id = "windows_server_2025.firewall"

    def matches(self, control: NormalizedControl) -> bool:
        return "firewall" in control.title.lower()

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.control_id,
            title=control.title,
            implementation_type="endpoint_security",
            intune_area="Firewall",
            setting_name="Microsoft Defender Firewall",
            value=control.parsed_recommendation.normalized_text or "Use CIS recommended value",
            confidence=0.82,
            rule_id=self.rule_id,
            parsed_value_type=control.parsed_recommendation.value_type,
            quality_flags=control.quality_flags,
        )
