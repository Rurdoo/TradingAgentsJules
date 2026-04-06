import unittest
from datetime import datetime
from tradingagents.dataflows.yfinance_news import _extract_article_data

class TestYFinanceNews(unittest.TestCase):
    def test_extract_article_data_nested_full(self):
        """Test extraction with a full nested content structure."""
        article = {
            "content": {
                "title": "Test Title",
                "summary": "Test Summary",
                "provider": {"displayName": "Test Publisher"},
                "canonicalUrl": {"url": "http://example.com/canonical"},
                "pubDate": "2023-01-01T12:00:00Z"
            }
        }
        expected = {
            "title": "Test Title",
            "summary": "Test Summary",
            "publisher": "Test Publisher",
            "link": "http://example.com/canonical",
            "pub_date": datetime(2023, 1, 1, 12, 0, 0)
        }
        # Assuming datetime output has tzinfo if parsing adds it, wait, Python 3.11+ fromisoformat handles Z.
        # Looking at _extract_article_data: pub_date_str.replace("Z", "+00:00")
        # So it might have timezone info. Let's just compare fields if needed, or use proper timezone.
        result = _extract_article_data(article)
        self.assertEqual(result["title"], expected["title"])
        self.assertEqual(result["summary"], expected["summary"])
        self.assertEqual(result["publisher"], expected["publisher"])
        self.assertEqual(result["link"], expected["link"])
        # Check date
        if result["pub_date"]:
            self.assertEqual(result["pub_date"].isoformat(), "2023-01-01T12:00:00+00:00")
        else:
            self.fail("pub_date was None")

    def test_extract_article_data_nested_missing_fields(self):
        """Test extraction with nested content missing most fields (defaults test)."""
        article = {
            "content": {}
        }
        result = _extract_article_data(article)
        self.assertEqual(result["title"], "No title")
        self.assertEqual(result["summary"], "")
        self.assertEqual(result["publisher"], "Unknown")
        self.assertEqual(result["link"], "")
        self.assertIsNone(result["pub_date"])

    def test_extract_article_data_nested_clickthrough_url(self):
        """Test URL extraction falls back to clickThroughUrl."""
        article = {
            "content": {
                "clickThroughUrl": {"url": "http://example.com/click"}
            }
        }
        result = _extract_article_data(article)
        self.assertEqual(result["link"], "http://example.com/click")

    def test_extract_article_data_invalid_pubdate(self):
        """Test invalid pubDate string handles ValueError gracefully."""
        article = {
            "content": {
                "pubDate": "invalid-date-string"
            }
        }
        result = _extract_article_data(article)
        self.assertIsNone(result["pub_date"])

    def test_extract_article_data_invalid_pubdate_type(self):
        """Test invalid pubDate type (e.g., number) handles AttributeError gracefully."""
        article = {
            "content": {
                "pubDate": 1234567890
            }
        }
        result = _extract_article_data(article)
        self.assertIsNone(result["pub_date"])

    def test_extract_article_data_flat_structure(self):
        """Test extraction with flat structure (fallback)."""
        article = {
            "title": "Flat Title",
            "summary": "Flat Summary",
            "publisher": "Flat Publisher",
            "link": "http://example.com/flat"
        }
        result = _extract_article_data(article)
        self.assertEqual(result["title"], "Flat Title")
        self.assertEqual(result["summary"], "Flat Summary")
        self.assertEqual(result["publisher"], "Flat Publisher")
        self.assertEqual(result["link"], "http://example.com/flat")
        self.assertIsNone(result["pub_date"])

    def test_extract_article_data_flat_missing_fields(self):
        """Test extraction with flat structure missing fields."""
        article = {}
        result = _extract_article_data(article)
        self.assertEqual(result["title"], "No title")
        self.assertEqual(result["summary"], "")
        self.assertEqual(result["publisher"], "Unknown")
        self.assertEqual(result["link"], "")
        self.assertIsNone(result["pub_date"])

if __name__ == "__main__":
    unittest.main()
