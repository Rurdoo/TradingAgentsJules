import unittest
import pandas as pd
import numpy as np
from tradingagents.dataflows.stockstats_utils import _clean_dataframe

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

if __name__ == "__main__":
    unittest.main()
