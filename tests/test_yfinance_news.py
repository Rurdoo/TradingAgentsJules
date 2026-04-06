import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from tradingagents.dataflows.yfinance_news import get_news_yfinance

class TestYFinanceNews(unittest.TestCase):
    @patch("tradingagents.dataflows.yfinance_news.yf.Ticker")
    @patch("tradingagents.dataflows.yfinance_news.yf_retry")
    def test_get_news_yfinance_success(self, mock_yf_retry, mock_ticker):
        # Mock yf_retry to just return the result of the lambda (which calls get_news)
        mock_yf_retry.side_effect = lambda f: f()

        # Setup mock Ticker
        mock_stock = MagicMock()
        mock_ticker.return_value = mock_stock

        # Mock get_news return value with one article inside the date range and one outside (but actually both inside for this success case)
        mock_stock.get_news.return_value = [
            {
                "content": {
                    "title": "Great News",
                    "summary": "Apple is doing great.",
                    "provider": {"displayName": "FinanceNews"},
                    "canonicalUrl": {"url": "http://example.com/great-news"},
                    "pubDate": "2023-10-15T12:00:00Z"
                }
            },
            {
                "content": {
                    "title": "More News",
                    "summary": "Apple releases new product.",
                    "provider": {"displayName": "TechDaily"},
                    "clickThroughUrl": {"url": "http://example.com/more-news"},
                    "pubDate": "2023-10-16T15:30:00Z"
                }
            }
        ]

        result = get_news_yfinance("AAPL", "2023-10-14", "2023-10-17")

        self.assertIn("## AAPL News, from 2023-10-14 to 2023-10-17:", result)
        self.assertIn("### Great News (source: FinanceNews)", result)
        self.assertIn("Apple is doing great.", result)
        self.assertIn("Link: http://example.com/great-news", result)
        self.assertIn("### More News (source: TechDaily)", result)
        self.assertIn("Apple releases new product.", result)
        self.assertIn("Link: http://example.com/more-news", result)

        mock_ticker.assert_called_once_with("AAPL")
        mock_stock.get_news.assert_called_once_with(count=20)

    @patch("tradingagents.dataflows.yfinance_news.yf.Ticker")
    @patch("tradingagents.dataflows.yfinance_news.yf_retry")
    def test_get_news_yfinance_filtered_out(self, mock_yf_retry, mock_ticker):
        mock_yf_retry.side_effect = lambda f: f()

        mock_stock = MagicMock()
        mock_ticker.return_value = mock_stock
        mock_stock.get_news.return_value = [
            {
                "content": {
                    "title": "Old News",
                    "summary": "This is old.",
                    "provider": {"displayName": "FinanceNews"},
                    "canonicalUrl": {"url": "http://example.com/old-news"},
                    "pubDate": "2023-10-10T12:00:00Z"
                }
            }
        ]

        result = get_news_yfinance("AAPL", "2023-10-14", "2023-10-17")

        self.assertEqual(result, "No news found for AAPL between 2023-10-14 and 2023-10-17")

        mock_ticker.assert_called_once_with("AAPL")
        mock_stock.get_news.assert_called_once_with(count=20)

    @patch("tradingagents.dataflows.yfinance_news.yf.Ticker")
    @patch("tradingagents.dataflows.yfinance_news.yf_retry")
    def test_get_news_yfinance_no_news(self, mock_yf_retry, mock_ticker):
        mock_yf_retry.side_effect = lambda f: f()

        mock_stock = MagicMock()
        mock_ticker.return_value = mock_stock
        mock_stock.get_news.return_value = []

        result = get_news_yfinance("AAPL", "2023-10-14", "2023-10-17")

        self.assertEqual(result, "No news found for AAPL")

        mock_ticker.assert_called_once_with("AAPL")
        mock_stock.get_news.assert_called_once_with(count=20)

    @patch("tradingagents.dataflows.yfinance_news.yf.Ticker")
    def test_get_news_yfinance_exception(self, mock_ticker):
        # Simulate exception during initialization or processing
        mock_ticker.side_effect = Exception("API error")

        result = get_news_yfinance("AAPL", "2023-10-14", "2023-10-17")

        self.assertEqual(result, "Error fetching news for AAPL: API error")

        mock_ticker.assert_called_once_with("AAPL")


if __name__ == "__main__":
    unittest.main()
