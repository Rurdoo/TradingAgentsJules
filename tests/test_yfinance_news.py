import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from tradingagents.dataflows.yfinance_news import get_news_yfinance, get_global_news_yfinance

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

    @patch("tradingagents.dataflows.yfinance_news.yf.Search")
    @patch("tradingagents.dataflows.yfinance_news.yf_retry")
    def test_get_global_news_yfinance_success(self, mock_yf_retry, mock_search):
        mock_yf_retry.side_effect = lambda f: f()

        mock_search_result = MagicMock()
        mock_search.return_value = mock_search_result

        # Return a mix of nested and flat structures, with a duplicate title
        mock_search_result.news = [
            {
                "content": {
                    "title": "Global Market Up",
                    "summary": "Markets are up globally.",
                    "provider": {"displayName": "GlobalNews"},
                    "canonicalUrl": {"url": "http://example.com/global"},
                    "pubDate": "2023-10-15T12:00:00Z"
                }
            },
            {
                "title": "Fed Rates Static",
                "summary": "Interest rates remain unchanged.",
                "publisher": "EcoDaily",
                "link": "http://example.com/fed",
                "pubDate": "2023-10-14T09:00:00Z"
            },
            {
                "title": "Global Market Up", # Duplicate title
                "summary": "This should be ignored.",
                "publisher": "SomeOtherSource",
                "link": "http://example.com/duplicate"
            }
        ]

        # Only one query mocked properly, but ThreadPoolExecutor will just hit the same mock multiple times.
        # Since we use a set for seen_titles, duplicates across threads will also be handled.

        result = get_global_news_yfinance("2023-10-17", look_back_days=7, limit=10)

        self.assertIn("## Global Market News, from 2023-10-10 to 2023-10-17:", result)
        self.assertIn("### Global Market Up (source: GlobalNews)", result)
        self.assertIn("Markets are up globally.", result)
        self.assertIn("Link: http://example.com/global", result)
        self.assertIn("### Fed Rates Static (source: EcoDaily)", result)
        # Note: Summary is not pulled for flat structures in get_global_news_yfinance
        self.assertIn("Link: http://example.com/fed", result)
        self.assertNotIn("This should be ignored.", result) # Deduplication check

        self.assertEqual(mock_search.call_count, 4) # 4 search queries

    @patch("tradingagents.dataflows.yfinance_news.yf.Search")
    @patch("tradingagents.dataflows.yfinance_news.yf_retry")
    def test_get_global_news_yfinance_filtered_out(self, mock_yf_retry, mock_search):
        mock_yf_retry.side_effect = lambda f: f()

        mock_search_result = MagicMock()
        mock_search.return_value = mock_search_result

        # Return a news article from the future
        mock_search_result.news = [
            {
                "content": {
                    "title": "Future News",
                    "summary": "This is from the future.",
                    "provider": {"displayName": "FutureNews"},
                    "canonicalUrl": {"url": "http://example.com/future"},
                    "pubDate": "2023-10-20T12:00:00Z"
                }
            }
        ]

        # The loop in get_global_news_yfinance will filter out items after curr_date + 1 day
        result = get_global_news_yfinance("2023-10-17", look_back_days=7, limit=10)

        # It doesn't return "No global news found" when filtered out later in the formatting step,
        # it just returns an empty news string under the header.
        self.assertEqual(result, "## Global Market News, from 2023-10-10 to 2023-10-17:\n\n")

    @patch("tradingagents.dataflows.yfinance_news.yf.Search")
    @patch("tradingagents.dataflows.yfinance_news.yf_retry")
    def test_get_global_news_yfinance_no_news(self, mock_yf_retry, mock_search):
        mock_yf_retry.side_effect = lambda f: f()

        mock_search_result = MagicMock()
        mock_search.return_value = mock_search_result
        mock_search_result.news = []

        result = get_global_news_yfinance("2023-10-17", look_back_days=7, limit=10)

        self.assertEqual(result, "No global news found for 2023-10-17")

    @patch("tradingagents.dataflows.yfinance_news.ThreadPoolExecutor")
    def test_get_global_news_yfinance_exception(self, mock_executor):
        # Simulate an exception that escapes the ThreadPoolExecutor context
        # (e.g. error starting threads)
        mock_executor.side_effect = Exception("Thread error")

        result = get_global_news_yfinance("2023-10-17", look_back_days=7, limit=10)

        self.assertEqual(result, "Error fetching global news: Thread error")


if __name__ == "__main__":
    unittest.main()
