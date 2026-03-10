import unittest

from cis_pdf2csv.intune_mapper.value_parser import parse_recommendation


class ValueParserTests(unittest.TestCase):
    def test_boolean_parse(self):
        parsed = parse_recommendation("Enabled")
        self.assertEqual(parsed.value_type, "boolean")
        self.assertTrue(parsed.bool_value)

    def test_range_parse(self):
        parsed = parse_recommendation("15-30")
        self.assertEqual(parsed.value_type, "range")
        self.assertEqual(parsed.min_value, 15)
        self.assertEqual(parsed.max_value, 30)

    def test_missing_recommendation(self):
        parsed = parse_recommendation(None)
        self.assertIn("missing_recommendation", parsed.quality_flags)


if __name__ == "__main__":
    unittest.main()
