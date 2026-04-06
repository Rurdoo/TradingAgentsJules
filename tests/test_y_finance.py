import unittest
from unittest.mock import patch, MagicMock
from tradingagents.dataflows.y_finance import get_stockstats_indicator, get_fundamentals
from datetime import datetime

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

    @patch('tradingagents.dataflows.y_finance.yf.Ticker')
    def test_get_fundamentals_success(self, mock_ticker):
        # Mock Ticker, info, and fast_info
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            "longName": "Apple Inc.",
            "sector": "Technology",
            "marketCap": 2500000000000,
            "trailingPE": 25.5
        }
        mock_ticker_instance.fast_info = {
            "lastPrice": 150.0
        }
        mock_ticker.return_value = mock_ticker_instance

        result = get_fundamentals("AAPL")

        self.assertIn("# Company Fundamentals for AAPL", result)
        self.assertIn("Name: Apple Inc.", result)
        self.assertIn("Sector: Technology", result)
        self.assertIn("Market Cap: 2500000000000", result)
        self.assertIn("PE Ratio (TTM): 25.5", result)
        mock_ticker.assert_called_once_with("AAPL")

    @patch('tradingagents.dataflows.y_finance.yf.Ticker')
    def test_get_fundamentals_no_info(self, mock_ticker):
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {}
        mock_ticker_instance.fast_info = {}
        mock_ticker.return_value = mock_ticker_instance

        result = get_fundamentals("AAPL")

        self.assertEqual(result, "No fundamentals data found for symbol 'AAPL'")
        mock_ticker.assert_called_once_with("AAPL")

    @patch('tradingagents.dataflows.y_finance.yf.Ticker')
    def test_get_fundamentals_exception(self, mock_ticker):
        mock_ticker.side_effect = Exception("API Error")

        result = get_fundamentals("AAPL")

        self.assertEqual(result, "Error retrieving fundamentals for AAPL: API Error")
        mock_ticker.assert_called_once_with("AAPL")

if __name__ == '__main__':
    unittest.main()
