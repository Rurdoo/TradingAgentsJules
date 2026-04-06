import unittest
from unittest.mock import patch, MagicMock
from tradingagents.dataflows.y_finance import get_stockstats_indicator

class TestYFinance(unittest.TestCase):
    @patch('tradingagents.dataflows.y_finance.StockstatsUtils.get_stock_stats')
    def test_get_stockstats_indicator_success(self, mock_get_stock_stats):
        # Setup the mock to return a normal value
        mock_get_stock_stats.return_value = 150.25

        # Call the function
        result = get_stockstats_indicator("AAPL", "close_50_sma", "2023-01-01")

        # Verify the result
        self.assertEqual(result, "150.25")
        mock_get_stock_stats.assert_called_once_with("AAPL", "close_50_sma", "2023-01-01")

    @patch('builtins.print')
    @patch('tradingagents.dataflows.y_finance.StockstatsUtils.get_stock_stats')
    def test_get_stockstats_indicator_exception(self, mock_get_stock_stats, mock_print):
        # Setup the mock to raise an exception
        mock_get_stock_stats.side_effect = Exception("Test exception")

        # Call the function
        result = get_stockstats_indicator("AAPL", "close_50_sma", "2023-01-01")

        # Verify the result is an empty string as per the exception handling logic
        self.assertEqual(result, "")

        # Verify the mock was called with the correct arguments
        mock_get_stock_stats.assert_called_once_with("AAPL", "close_50_sma", "2023-01-01")

        # Verify print was called with the expected error message
        mock_print.assert_called_once_with(
            "Error getting stockstats indicator data for indicator close_50_sma on 2023-01-01: Test exception"
        )

if __name__ == '__main__':
    unittest.main()
