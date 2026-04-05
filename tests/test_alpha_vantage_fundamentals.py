import unittest
from tradingagents.dataflows.alpha_vantage_fundamentals import _filter_reports_by_date

class TestAlphaVantageFundamentals(unittest.TestCase):
    def test_filter_reports_by_date_basic(self):
        result = {
            "annualReports": [
                {"fiscalDateEnding": "2023-12-31", "value": "100"},
                {"fiscalDateEnding": "2024-12-31", "value": "200"}
            ],
            "quarterlyReports": [
                {"fiscalDateEnding": "2024-03-31", "value": "50"},
                {"fiscalDateEnding": "2024-06-30", "value": "60"}
            ]
        }
        curr_date = "2024-05-01"
        filtered = _filter_reports_by_date(result.copy(), curr_date)

        self.assertEqual(len(filtered["annualReports"]), 1)
        self.assertEqual(filtered["annualReports"][0]["fiscalDateEnding"], "2023-12-31")

        self.assertEqual(len(filtered["quarterlyReports"]), 1)
        self.assertEqual(filtered["quarterlyReports"][0]["fiscalDateEnding"], "2024-03-31")

    def test_filter_reports_by_date_exact_match(self):
        result = {
            "annualReports": [
                {"fiscalDateEnding": "2023-12-31", "value": "100"}
            ]
        }
        curr_date = "2023-12-31"
        filtered = _filter_reports_by_date(result.copy(), curr_date)
        self.assertEqual(len(filtered["annualReports"]), 1)

    def test_filter_reports_by_date_no_curr_date(self):
        result = {"annualReports": [{"fiscalDateEnding": "2023-12-31"}]}
        self.assertEqual(_filter_reports_by_date(result, None), result)
        self.assertEqual(_filter_reports_by_date(result, ""), result)

    def test_filter_reports_by_date_invalid_result_type(self):
        self.assertEqual(_filter_reports_by_date("not a dict", "2023-12-31"), "not a dict")

    def test_filter_reports_by_date_missing_fiscalDateEnding(self):
        result = {
            "annualReports": [
                {"value": "no date"},
                {"fiscalDateEnding": "2023-12-31"}
            ]
        }
        # r.get("fiscalDateEnding", "") <= "2024-01-01" -> "" <= "2024-01-01" is True
        filtered = _filter_reports_by_date(result.copy(), "2024-01-01")
        self.assertEqual(len(filtered["annualReports"]), 2)

        # "" <= "2022-01-01" is True
        filtered = _filter_reports_by_date(result.copy(), "2022-01-01")
        self.assertEqual(len(filtered["annualReports"]), 1)
        self.assertEqual(filtered["annualReports"][0].get("value"), "no date")

    def test_filter_reports_by_date_empty_reports(self):
        result = {"annualReports": [], "quarterlyReports": []}
        filtered = _filter_reports_by_date(result.copy(), "2024-01-01")
        self.assertEqual(filtered, result)

    def test_filter_reports_by_date_no_reports_key(self):
        result = {"otherKey": "someValue"}
        filtered = _filter_reports_by_date(result.copy(), "2024-01-01")
        self.assertEqual(filtered, result)

if __name__ == "__main__":
    unittest.main()
