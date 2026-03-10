from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Protocol, Sequence


IMPLEMENTATION_PRIORITY = {
    "endpoint_security": 1,
    "settings_catalog": 2,
    "administrative_template": 3,
    "custom_oma_uri": 4,
    "manual_review": 5,
}


@dataclass
class NormalizedControl:
    """Normalized CIS control input used by the Intune resolver.

    The parser currently provides a subset of these fields.
    Optional GPO/registry fields are included for forward compatibility.
    """

    cis_id: str
    title: str
    profile: str = "Unknown"
    description: Optional[str] = None
    rationale: Optional[str] = None
    gpo_path: Optional[str] = None
    registry_path: Optional[str] = None
    registry_value_name: Optional[str] = None
    recommended_value: Optional[str] = None


@dataclass
class IntuneMapping:
    cis_id: str
    title: str
    implementation_type: str
    intune_area: str
    setting_name: str
    value: str
    confidence: float
    rule_name: str


@dataclass
class MappingConflict:
    cis_id: str
    title: str
    selected_rule: str
    selected_implementation_type: str
    matched_rules: List[str]


class MappingRule(Protocol):
    name: str

    def matches(self, control: NormalizedControl) -> bool:
        ...

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        ...


class ConsumerExperienceRule:
    name = "consumer_experience_rule"

    def matches(self, control: NormalizedControl) -> bool:
        return "consumer experiences" in control.title.lower()

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.cis_id,
            title=control.title,
            implementation_type="settings_catalog",
            intune_area="Windows OS Hardening",
            setting_name="Turn off Microsoft consumer experiences",
            value="Enabled",
            confidence=0.95,
            rule_name=self.name,
        )


class DefenderRealtimeMonitoringRule:
    name = "defender_realtime_monitoring_rule"

    def matches(self, control: NormalizedControl) -> bool:
        title = control.title.lower()
        return "microsoft defender" in title or "real-time protection" in title

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.cis_id,
            title=control.title,
            implementation_type="endpoint_security",
            intune_area="Defender Security",
            setting_name="Microsoft Defender Antivirus - Real-time protection",
            value=control.recommended_value or "Enabled",
            confidence=0.75,
            rule_name=self.name,
        )


class FirewallProfileRule:
    name = "firewall_profile_rule"

    def matches(self, control: NormalizedControl) -> bool:
        title = control.title.lower()
        return "firewall" in title and "profile" in title

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.cis_id,
            title=control.title,
            implementation_type="endpoint_security",
            intune_area="Firewall",
            setting_name="Microsoft Defender Firewall profile state",
            value=control.recommended_value or "Enabled",
            confidence=0.75,
            rule_name=self.name,
        )


class BitLockerRule:
    name = "bitlocker_rule"

    def matches(self, control: NormalizedControl) -> bool:
        title = control.title.lower()
        return "bitlocker" in title or "drive encryption" in title

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.cis_id,
            title=control.title,
            implementation_type="endpoint_security",
            intune_area="BitLocker",
            setting_name="Require BitLocker",
            value=control.recommended_value or "Enabled",
            confidence=0.75,
            rule_name=self.name,
        )


class EdgeAdministrativeTemplateRule:
    name = "edge_administrative_template_rule"

    def matches(self, control: NormalizedControl) -> bool:
        title = control.title.lower()
        return "microsoft edge" in title

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.cis_id,
            title=control.title,
            implementation_type="administrative_template",
            intune_area="Browser Hardening",
            setting_name=control.title,
            value=control.recommended_value or "See CIS recommendation",
            confidence=0.50,
            rule_name=self.name,
        )


class ManualReviewRule:
    name = "manual_review_rule"

    def matches(self, control: NormalizedControl) -> bool:
        return True

    def apply(self, control: NormalizedControl) -> IntuneMapping:
        return IntuneMapping(
            cis_id=control.cis_id,
            title=control.title,
            implementation_type="manual_review",
            intune_area="Manual Review",
            setting_name="Needs analyst validation",
            value=control.recommended_value or "Unknown",
            confidence=0.00,
            rule_name=self.name,
        )


class IntuneResolver:
    def __init__(self, rules: Optional[Sequence[MappingRule]] = None):
        self.rules: Sequence[MappingRule] = rules or [
            DefenderRealtimeMonitoringRule(),
            FirewallProfileRule(),
            BitLockerRule(),
            ConsumerExperienceRule(),
            EdgeAdministrativeTemplateRule(),
            ManualReviewRule(),
        ]

    def resolve_control(
        self,
        control: NormalizedControl,
    ) -> tuple[IntuneMapping, List[IntuneMapping]]:
        matches: List[IntuneMapping] = []

        for rule in self.rules:
            if rule.matches(control):
                matches.append(rule.apply(control))

        matches.sort(
            key=lambda m: (
                IMPLEMENTATION_PRIORITY.get(m.implementation_type, 99),
                -m.confidence,
            )
        )
        return matches[0], matches

    def resolve_controls(
        self,
        controls: Iterable[NormalizedControl],
    ) -> tuple[List[IntuneMapping], List[MappingConflict]]:
        resolved: List[IntuneMapping] = []
        conflicts: List[MappingConflict] = []

        for control in controls:
            winner, all_matches = self.resolve_control(control)
            resolved.append(winner)

            concrete_matches = [
                m for m in all_matches if m.implementation_type != "manual_review"
            ]
            if len(concrete_matches) > 1:
                conflicts.append(
                    MappingConflict(
                        cis_id=control.cis_id,
                        title=control.title,
                        selected_rule=winner.rule_name,
                        selected_implementation_type=winner.implementation_type,
                        matched_rules=[m.rule_name for m in concrete_matches],
                    )
                )

        return resolved, conflicts


def controls_from_parser_rows(rows: Iterable[dict]) -> List[NormalizedControl]:
    controls: List[NormalizedControl] = []
    for row in rows:
        controls.append(
            NormalizedControl(
                cis_id=row.get("control_id", ""),
                title=row.get("title", ""),
                profile=row.get("profile", "Unknown"),
                description=row.get("description"),
                rationale=row.get("rationale"),
                gpo_path=row.get("gpo_path"),
                registry_path=row.get("registry_path"),
                registry_value_name=row.get("registry_value_name"),
                recommended_value=row.get("recommended_value"),
            )
        )
    return controls


def export_baseline_csv(mappings: Sequence[IntuneMapping], out_path: Path) -> None:
    fieldnames = [
        "cis_id",
        "title",
        "implementation_type",
        "intune_area",
        "setting_name",
        "value",
        "confidence",
        "rule_name",
    ]
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for m in mappings:
            writer.writerow(m.__dict__)


def export_manual_review_csv(mappings: Sequence[IntuneMapping], out_path: Path) -> None:
    fieldnames = [
        "cis_id",
        "title",
        "intune_area",
        "setting_name",
        "value",
        "confidence",
    ]
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for m in mappings:
            if m.implementation_type == "manual_review":
                writer.writerow(
                    {
                        "cis_id": m.cis_id,
                        "title": m.title,
                        "intune_area": m.intune_area,
                        "setting_name": m.setting_name,
                        "value": m.value,
                        "confidence": m.confidence,
                    }
                )


def export_conflicts_csv(conflicts: Sequence[MappingConflict], out_path: Path) -> None:
    fieldnames = [
        "cis_id",
        "title",
        "selected_rule",
        "selected_implementation_type",
        "matched_rules",
    ]
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for c in conflicts:
            writer.writerow(
                {
                    "cis_id": c.cis_id,
                    "title": c.title,
                    "selected_rule": c.selected_rule,
                    "selected_implementation_type": c.selected_implementation_type,
                    "matched_rules": ",".join(c.matched_rules),
                }
            )


def export_intune_policies_json(
    mappings: Sequence[IntuneMapping],
    out_path: Path,
) -> None:
    policies: dict[str, list[dict]] = {}

    for m in mappings:
        policies.setdefault(m.intune_area, []).append(
            {
                "cis_id": m.cis_id,
                "title": m.title,
                "implementation_type": m.implementation_type,
                "setting_name": m.setting_name,
                "value": m.value,
                "confidence": m.confidence,
            }
        )

    out_path.write_text(json.dumps(policies, indent=2, ensure_ascii=False), encoding="utf-8")
