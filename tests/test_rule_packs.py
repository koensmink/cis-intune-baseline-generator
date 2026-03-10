import unittest

from cis_pdf2csv.intune_mapper.models import MappingInputControl
from cis_pdf2csv.intune_mapper.resolver import resolve_control


class RulePackTests(unittest.TestCase):
    def test_defender_rule(self):
        control = MappingInputControl(
            control_id="1.1",
            title="(L1) Ensure Microsoft Defender Antivirus is Enabled",
            recommendation="Enabled",
        )
        mapping, conflict = resolve_control(control)
        self.assertIsNone(conflict)
        self.assertEqual(mapping.rule_id, "windows_server_2025.defender")

    def test_manual_review_fallback(self):
        control = MappingInputControl(
            control_id="9.9",
            title="Some niche control with no direct mapping",
            recommendation="Custom vendor setting",
        )
        mapping, _ = resolve_control(control)
        self.assertEqual(mapping.implementation_type, "manual_review")


if __name__ == "__main__":
    unittest.main()
