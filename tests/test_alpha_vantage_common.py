import unittest
from datetime import datetime
from tradingagents.dataflows.alpha_vantage_common import format_datetime_for_api

class TestFormatDatetimeForApi(unittest.TestCase):
    def test_pre_formatted_string(self):
        """Test with string already in YYYYMMDDTHHMM format."""
        self.assertEqual(format_datetime_for_api("20230101T1230"), "20230101T1230")

    def test_date_string_only(self):
        """Test with YYYY-MM-DD string."""
        self.assertEqual(format_datetime_for_api("2023-01-01"), "20230101T0000")

    def test_datetime_string_with_minutes(self):
        """Test with YYYY-MM-DD HH:MM string."""
        self.assertEqual(format_datetime_for_api("2023-01-01 12:30"), "20230101T1230")

    def test_datetime_object(self):
        """Test with a datetime object."""
        dt = datetime(2023, 1, 1, 12, 30)
        self.assertEqual(format_datetime_for_api(dt), "20230101T1230")

    def test_unsupported_date_format(self):
        """Test with unsupported date string format."""
        with self.assertRaisesRegex(ValueError, "Unsupported date format"):
            format_datetime_for_api("01/01/2023")

    def test_empty_string(self):
        """Test with empty string."""
        self.assertEqual(format_datetime_for_api(""), "")

    def test_invalid_type(self):
        """Test with unsupported types."""
        with self.assertRaisesRegex(ValueError, "Date must be string or datetime object"):
            format_datetime_for_api(12345)

    def test_none_input(self):
        """Test with None."""
        self.assertEqual(format_datetime_for_api(None), "")

if __name__ == "__main__":
    unittest.main()
