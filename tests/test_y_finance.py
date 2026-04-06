import unittest
from unittest.mock import patch, MagicMock
from tradingagents.dataflows.y_finance import get_stockstats_indicator

class TestYFinance(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()
