import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from yfinance.exceptions import YFRateLimitError

from tradingagents.dataflows.stockstats_utils import _clean_dataframe, yf_retry

class TestStockstatsUtils(unittest.TestCase):
    def test_clean_dataframe_nan_inf(self):
        # Create a DataFrame with NaNs and infs
        df = pd.DataFrame({
            "Date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
            "Open": [np.nan, 10.0, np.inf, 12.0, np.nan],
            "Close": [np.nan, np.nan, 15.0, -np.inf, np.nan],
            "High": [np.nan, np.nan, np.nan, np.nan, np.nan] # All NaNs
        })

        cleaned_df = _clean_dataframe(df)

        # Expected Open:
        # Initial: [NaN, 10.0, inf, 12.0, NaN]
        # Replace inf: [NaN, 10.0, NaN, 12.0, NaN]
        # Ffill: [NaN, 10.0, 10.0, 12.0, 12.0]
        # Bfill: [10.0, 10.0, 10.0, 12.0, 12.0]
        # Fillna(0): [10.0, 10.0, 10.0, 12.0, 12.0]
        np.testing.assert_array_equal(cleaned_df["Open"].values, [10.0, 10.0, 10.0, 12.0, 12.0])

        # Expected Close:
        # Initial: [NaN, NaN, 15.0, -inf, NaN]
        # Replace inf: [NaN, NaN, 15.0, NaN, NaN]
        # Ffill: [NaN, NaN, 15.0, 15.0, 15.0]
        # Bfill: [15.0, 15.0, 15.0, 15.0, 15.0]
        # Fillna(0): [15.0, 15.0, 15.0, 15.0, 15.0]
        np.testing.assert_array_equal(cleaned_df["Close"].values, [15.0, 15.0, 15.0, 15.0, 15.0])

        # Expected High:
        # Initial: [NaN, NaN, NaN, NaN, NaN]
        # Replace inf: [NaN, NaN, NaN, NaN, NaN]
        # Ffill: [NaN, NaN, NaN, NaN, NaN]
        # Bfill: [NaN, NaN, NaN, NaN, NaN]
        # Fillna(0): [0.0, 0.0, 0.0, 0.0, 0.0]
        np.testing.assert_array_equal(cleaned_df["High"].values, [0.0, 0.0, 0.0, 0.0, 0.0])

    def test_clean_dataframe_no_price_columns(self):
        df = pd.DataFrame({
            "Date": ["2023-01-01", "2023-01-02"],
            "OtherCol": [1, 2]
        })
        cleaned_df = _clean_dataframe(df)
        self.assertEqual(list(cleaned_df.columns), ["Date", "OtherCol"])
        self.assertEqual(len(cleaned_df), 2)

    def test_clean_dataframe_invalid_dates(self):
        df = pd.DataFrame({
            "Date": ["2023-01-01", "invalid_date", "2023-01-03"],
            "Close": [10.0, 11.0, 12.0]
        })
        cleaned_df = _clean_dataframe(df)
        self.assertEqual(len(cleaned_df), 2)
        self.assertEqual(cleaned_df["Date"].dt.strftime("%Y-%m-%d").tolist(), ["2023-01-01", "2023-01-03"])
        self.assertEqual(cleaned_df["Close"].tolist(), [10.0, 12.0])

class TestYFRetry(unittest.TestCase):

    def test_yf_retry_success_first_try(self):
        func = MagicMock(return_value="success")
        result = yf_retry(func, max_retries=3, base_delay=2.0)

        self.assertEqual(result, "success")
        self.assertEqual(func.call_count, 1)

    @patch("time.sleep")
    def test_yf_retry_success_after_retries(self, mock_sleep):
        func = MagicMock(side_effect=[YFRateLimitError(), YFRateLimitError(), "success"])
        result = yf_retry(func, max_retries=3, base_delay=2.0)

        self.assertEqual(result, "success")
        self.assertEqual(func.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        # Check sleep delays: 2.0 * (2**0) = 2.0, 2.0 * (2**1) = 4.0
        mock_sleep.assert_any_call(2.0)
        mock_sleep.assert_any_call(4.0)

    @patch("time.sleep")
    def test_yf_retry_failure_max_retries(self, mock_sleep):
        func = MagicMock(side_effect=YFRateLimitError())

        with self.assertRaises(YFRateLimitError):
            yf_retry(func, max_retries=3, base_delay=2.0)

        self.assertEqual(func.call_count, 4) # initial + 3 retries
        self.assertEqual(mock_sleep.call_count, 3)
        mock_sleep.assert_any_call(2.0)
        mock_sleep.assert_any_call(4.0)
        mock_sleep.assert_any_call(8.0)

    def test_yf_retry_other_exception(self):
        func = MagicMock(side_effect=ValueError("other error"))

        with self.assertRaises(ValueError):
            yf_retry(func, max_retries=3, base_delay=2.0)

        self.assertEqual(func.call_count, 1)

if __name__ == "__main__":
    unittest.main()
