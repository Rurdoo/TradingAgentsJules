import unittest
from unittest.mock import patch, MagicMock
from tradingagents.dataflows.alpha_vantage_fundamentals import (
    get_fundamentals,
    get_balance_sheet,
    get_cashflow,
    get_income_statement,
    _filter_reports_by_date
)

class TestAlphaVantageFundamentals(unittest.TestCase):

    @patch('tradingagents.dataflows.alpha_vantage_fundamentals._make_api_request')
    def test_get_fundamentals(self, mock_make_request):
        """Test that get_fundamentals calls _make_api_request correctly."""
        mock_make_request.return_value = '{"Symbol": "AAPL", "Name": "Apple Inc."}'

        result = get_fundamentals("AAPL", curr_date="2023-01-01")

        mock_make_request.assert_called_once_with("OVERVIEW", {"symbol": "AAPL"})
        self.assertEqual(result, '{"Symbol": "AAPL", "Name": "Apple Inc."}')

    @patch('tradingagents.dataflows.alpha_vantage_fundamentals._make_api_request')
    def test_get_balance_sheet(self, mock_make_request):
        """Test get_balance_sheet with mock and filter applied."""
        mock_data = {
            "symbol": "AAPL",
            "annualReports": [
                {"fiscalDateEnding": "2023-09-30", "totalAssets": "100"},
                {"fiscalDateEnding": "2022-09-30", "totalAssets": "90"}
            ]
        }
        mock_make_request.return_value = mock_data

        # Test with curr_date before the 2023 report
        result = get_balance_sheet("AAPL", curr_date="2023-01-01")

        mock_make_request.assert_called_once_with("BALANCE_SHEET", {"symbol": "AAPL"})
        self.assertEqual(len(result["annualReports"]), 1)
        self.assertEqual(result["annualReports"][0]["fiscalDateEnding"], "2022-09-30")

    @patch('tradingagents.dataflows.alpha_vantage_fundamentals._make_api_request')
    def test_get_cashflow(self, mock_make_request):
        """Test get_cashflow with mock and filter applied."""
        mock_data = {
            "symbol": "AAPL",
            "quarterlyReports": [
                {"fiscalDateEnding": "2023-03-31"},
                {"fiscalDateEnding": "2022-12-31"}
            ]
        }
        mock_make_request.return_value = mock_data

        result = get_cashflow("AAPL", curr_date="2023-02-01")

        mock_make_request.assert_called_once_with("CASH_FLOW", {"symbol": "AAPL"})
        self.assertEqual(len(result["quarterlyReports"]), 1)
        self.assertEqual(result["quarterlyReports"][0]["fiscalDateEnding"], "2022-12-31")

    @patch('tradingagents.dataflows.alpha_vantage_fundamentals._make_api_request')
    def test_get_income_statement(self, mock_make_request):
        """Test get_income_statement with mock and filter applied."""
        mock_data = {
            "symbol": "AAPL",
            "annualReports": [
                {"fiscalDateEnding": "2023-12-31"}
            ]
        }
        mock_make_request.return_value = mock_data

        result = get_income_statement("AAPL", curr_date="2024-01-01")

        mock_make_request.assert_called_once_with("INCOME_STATEMENT", {"symbol": "AAPL"})
        self.assertEqual(len(result["annualReports"]), 1)
        self.assertEqual(result["annualReports"][0]["fiscalDateEnding"], "2023-12-31")

    def test_filter_reports_by_date_no_curr_date(self):
        """Test filtering when curr_date is None."""
        data = {"annualReports": [{"fiscalDateEnding": "2023-12-31"}]}
        result = _filter_reports_by_date(data, curr_date=None)
        self.assertEqual(result, data)

    def test_filter_reports_by_date_not_dict(self):
        """Test filtering when result is not a dict (e.g. string)."""
        data = "Some error string"
        result = _filter_reports_by_date(data, curr_date="2023-01-01")
        self.assertEqual(result, data)

    def test_filter_reports_by_date_missing_keys(self):
        """Test filtering when dict doesn't have report keys."""
        data = {"symbol": "AAPL"}
        result = _filter_reports_by_date(data, curr_date="2023-01-01")
        self.assertEqual(result, data)

    def test_filter_reports_by_date_exact_match(self):
        """Test filtering when fiscalDateEnding exactly matches curr_date."""
        data = {"annualReports": [{"fiscalDateEnding": "2023-12-31"}]}
        result = _filter_reports_by_date(data, curr_date="2023-12-31")
        self.assertEqual(len(result["annualReports"]), 1)

if __name__ == '__main__':
    unittest.main()
