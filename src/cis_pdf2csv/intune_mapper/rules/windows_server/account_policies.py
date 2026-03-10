from __future__ import annotations

from ..base import MappingRule
from ...models import IntuneMapping, NormalizedControl


class AccountPoliciesRule(MappingRule):
    rule_id = "windows_server_2025.account_policies"

    def matches(self, control: NormalizedControl) -> bool:
        t = control.title.lower()
        return "password" in t or "account lockout" in t

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.control_id,
            title=control.title,
            implementation_type="settings_catalog",
            intune_area="Account Policies",
            setting_name="Password and lockout policy",
            value=control.parsed_recommendation.normalized_text or "Use CIS recommended value",
            confidence=0.8,
            rule_id=self.rule_id,
            parsed_value_type=control.parsed_recommendation.value_type,
            quality_flags=control.quality_flags,
        )
