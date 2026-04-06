import unittest
from unittest.mock import patch
from tradingagents.dataflows.alpha_vantage_indicator import get_indicator

class TestAlphaVantageIndicator(unittest.TestCase):
    @patch('tradingagents.dataflows.alpha_vantage_indicator._make_api_request')
    def test_missing_time_column(self, mock_make_api_request):
        # Mock API response returning a CSV string without a 'time' column
        mock_csv_data = "date,close,high,low,open,volume\n2023-01-01,150.0,155.0,148.0,149.0,1000000\n"
        mock_make_api_request.return_value = mock_csv_data

        symbol = "AAPL"
        indicator = "close_50_sma"
        curr_date = "2023-01-02"
        look_back_days = 30

        result = get_indicator(
            symbol=symbol,
            indicator=indicator,
            curr_date=curr_date,
            look_back_days=look_back_days
        )

        expected_error_message = "Error: 'time' column not found in data for close_50_sma. Available columns: ['date', 'close', 'high', 'low', 'open', 'volume']"
        self.assertEqual(result, expected_error_message)

if __name__ == '__main__':
    unittest.main()
