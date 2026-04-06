import unittest
from unittest.mock import patch, MagicMock
from tradingagents.dataflows.y_finance import get_stockstats_indicator, get_stock_stats_indicators_window

class TestYFinance(unittest.TestCase):
    @patch('tradingagents.dataflows.y_finance.StockstatsUtils.get_stock_stats')
    def test_get_stockstats_indicator_success(self, mock_get_stock_stats):
        # Setup the mock to return a valid indicator value
        mock_get_stock_stats.return_value = 150.50

        # Call the function
        result = get_stockstats_indicator("AAPL", "close_50_sma", "2023-01-01")

        # Verify the result is the string representation of the value
        self.assertEqual(result, "150.5")

        # Verify the mock was called with the correct arguments
        mock_get_stock_stats.assert_called_once_with("AAPL", "close_50_sma", "2023-01-01")

    @patch('tradingagents.dataflows.y_finance.StockstatsUtils.get_stock_stats')
    def test_get_stockstats_indicator_exception(self, mock_get_stock_stats):
        # Setup the mock to raise an exception
        mock_get_stock_stats.side_effect = Exception("Test exception")

        # Call the function
        result = get_stockstats_indicator("AAPL", "close_50_sma", "2023-01-01")

        # Verify the result is an empty string as per the exception handling logic
        self.assertEqual(result, "")

        # Verify the mock was called with the correct arguments
        mock_get_stock_stats.assert_called_once_with("AAPL", "close_50_sma", "2023-01-01")

    @patch('tradingagents.dataflows.y_finance._get_stock_stats_bulk')
    @patch('tradingagents.dataflows.y_finance.get_stockstats_indicator')
    def test_get_stock_stats_indicators_window_bulk_exception(self, mock_get_stockstats_indicator, mock_get_bulk):
        # Setup the bulk method to fail
        mock_get_bulk.side_effect = Exception("Bulk method failed")

        # Setup the fallback method to return dummy values
        mock_get_stockstats_indicator.side_effect = ["150.5", "149.0"]

        # Call the function with look_back_days=1 (requires 2 calls to the fallback: today and yesterday)
        result = get_stock_stats_indicators_window("AAPL", "close_50_sma", "2023-01-02", 1)

        # Verify the bulk method was called once
        mock_get_bulk.assert_called_once_with("AAPL", "close_50_sma", "2023-01-02")

        # Verify the fallback method was called twice (for 2023-01-02 and 2023-01-01)
        self.assertEqual(mock_get_stockstats_indicator.call_count, 2)

        # Verify the result contains the dummy values and fallback output
        self.assertIn("2023-01-02: 150.5", result)
        self.assertIn("2023-01-01: 149.0", result)
        self.assertIn("50 SMA", result)

if __name__ == '__main__':
    unittest.main()
