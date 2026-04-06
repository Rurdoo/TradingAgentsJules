import unittest
from unittest.mock import patch, MagicMock

from tradingagents.dataflows.alpha_vantage_news import get_news, get_global_news, get_insider_transactions


class TestAlphaVantageNews(unittest.TestCase):

    @patch("tradingagents.dataflows.alpha_vantage_news._make_api_request")
    def test_get_news(self, mock_make_api_request):
        # Setup mock return value
        mock_response = {
            "items": "50",
            "sentiment_score_definition": "x <= -0.35: Bearish; -0.35 < x <= -0.15: Somewhat-Bearish; -0.15 < x < 0.15: Neutral; 0.15 <= x < 0.35: Somewhat_Bullish; x >= 0.35: Bullish",
            "relevance_score_definition": "0 < x <= 1, with a higher score indicating higher relevance.",
            "feed": [
                {
                    "title": "Apple Inc. (AAPL) Q4 2022 Earnings Call Transcript",
                    "url": "https://www.fool.com/earnings/call-transcripts/2022/10/27/apple-inc-aapl-q4-2022-earnings-call-transcript/",
                    "time_published": "20221028T011041",
                    "authors": ["Motley Fool Transcribing"],
                    "summary": "Apple Inc. (AAPL) Q4 2022 Earnings Call Transcript",
                    "banner_image": "https://g.foolcdn.com/editorial/images/706509/apple-logo-on-a-building.jpg",
                    "source": "Motley Fool",
                    "category_within_source": "n/a",
                    "source_domain": "www.fool.com",
                    "topics": [
                        {
                            "topic": "Earnings",
                            "relevance_score": "0.999999"
                        },
                        {
                            "topic": "Technology",
                            "relevance_score": "0.5"
                        }
                    ],
                    "overall_sentiment_score": 0.1132,
                    "overall_sentiment_label": "Neutral",
                    "ticker_sentiment": [
                        {
                            "ticker": "AAPL",
                            "relevance_score": "0.089851",
                            "ticker_sentiment_score": "0.015242",
                            "ticker_sentiment_label": "Neutral"
                        }
                    ]
                }
            ]
        }
        mock_make_api_request.return_value = mock_response

        # Execute
        result = get_news("AAPL", "2023-01-01", "2023-01-31")

        # Assert
        self.assertEqual(result, mock_response)

        # Verify the call to _make_api_request
        mock_make_api_request.assert_called_once_with(
            "NEWS_SENTIMENT",
            {
                "tickers": "AAPL",
                "time_from": "20230101T0000",
                "time_to": "20230131T0000"
            }
        )

    @patch("tradingagents.dataflows.alpha_vantage_news._make_api_request")
    def test_get_global_news(self, mock_make_api_request):
        # Setup mock return value
        mock_response = {
            "items": "1",
            "feed": [
                {
                    "title": "Global Market Update",
                    "summary": "Markets are up today.",
                }
            ]
        }
        mock_make_api_request.return_value = mock_response

        # Execute
        result = get_global_news("2023-10-15", look_back_days=7, limit=10)

        # Assert
        self.assertEqual(result, mock_response)

        # Verify the call to _make_api_request
        # time_from should be 2023-10-15 minus 7 days = 2023-10-08
        mock_make_api_request.assert_called_once_with(
            "NEWS_SENTIMENT",
            {
                "topics": "financial_markets,economy_macro,economy_monetary",
                "time_from": "20231008T0000",
                "time_to": "20231015T0000",
                "limit": "10"
            }
        )

    @patch("tradingagents.dataflows.alpha_vantage_news._make_api_request")
    def test_get_insider_transactions(self, mock_make_api_request):
        # Setup mock return value
        mock_response = {
            "data": [
                {
                    "symbol": "AAPL",
                    "transaction_date": "2023-10-10",
                }
            ]
        }
        mock_make_api_request.return_value = mock_response

        # Execute
        result = get_insider_transactions("AAPL")

        # Assert
        self.assertEqual(result, mock_response)

        # Verify the call to _make_api_request
        mock_make_api_request.assert_called_once_with(
            "INSIDER_TRANSACTIONS",
            {
                "symbol": "AAPL",
            }
        )

if __name__ == "__main__":
    unittest.main()
