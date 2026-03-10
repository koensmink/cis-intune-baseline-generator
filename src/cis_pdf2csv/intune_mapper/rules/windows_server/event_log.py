from __future__ import annotations

from ..base import MappingRule
from ...models import IntuneMapping, NormalizedControl


class EventLogRule(MappingRule):
    rule_id = "windows_server_2025.event_log"

    def matches(self, control: NormalizedControl) -> bool:
        t = control.title.lower()
        return "event log" in t or "log size" in t

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.control_id,
            title=control.title,
            implementation_type="settings_catalog",
            intune_area="Event Log",
            setting_name="Event log retention and size",
            value=control.parsed_recommendation.normalized_text or "Use CIS recommended value",
            confidence=0.75,
            rule_id=self.rule_id,
            parsed_value_type=control.parsed_recommendation.value_type,
            quality_flags=control.quality_flags,
        )
