from __future__ import annotations

from ..base import MappingRule
from ...models import IntuneMapping, NormalizedControl


class AuditPolicyRule(MappingRule):
    rule_id = "windows_server_2025.audit_policy"

    def matches(self, control: NormalizedControl) -> bool:
        return "audit" in control.title.lower()

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.control_id,
            title=control.title,
            implementation_type="settings_catalog",
            intune_area="Audit Policy",
            setting_name="Advanced Audit Policy Configuration",
            value=control.parsed_recommendation.normalized_text or "Use CIS recommended value",
            confidence=0.78,
            rule_id=self.rule_id,
            parsed_value_type=control.parsed_recommendation.value_type,
            quality_flags=control.quality_flags,
        )
