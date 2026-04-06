import unittest
import pandas as pd
from tradingagents.dataflows.stockstats_utils import filter_financials_by_date


class TestStockstatsUtils(unittest.TestCase):
    def test_filter_financials_by_date_drops_future_columns(self):
        """Test that columns strictly after the cutoff date are dropped."""
        df = pd.DataFrame({
            "2020-12-31": [100, 200],
            "2021-12-31": [110, 210],
            "2022-12-31": [120, 220]
        })
        curr_date = "2021-12-31"
        result = filter_financials_by_date(df, curr_date)

        expected_columns = ["2020-12-31", "2021-12-31"]
        self.assertEqual(list(result.columns), expected_columns)
        self.assertEqual(result.shape, (2, 2))

    def test_filter_financials_by_date_empty_curr_date(self):
        """Test that an empty curr_date returns the original DataFrame."""
        df = pd.DataFrame({
            "2020-12-31": [100, 200],
            "2021-12-31": [110, 210]
        })
        # Empty string
        result1 = filter_financials_by_date(df, "")
        pd.testing.assert_frame_equal(result1, df)

        # None
        result2 = filter_financials_by_date(df, None)
        pd.testing.assert_frame_equal(result2, df)

    def test_filter_financials_by_date_empty_df(self):
        """Test that an empty DataFrame is handled correctly."""
        df = pd.DataFrame()
        result = filter_financials_by_date(df, "2021-12-31")
        self.assertTrue(result.empty)
        pd.testing.assert_frame_equal(result, df)

    def test_filter_financials_by_date_keeps_past_and_present(self):
        """Test that columns before and on the cutoff date are kept."""
        df = pd.DataFrame({
            pd.Timestamp("2021-06-30"): [1, 2],
            pd.Timestamp("2021-12-31"): [3, 4],
            pd.Timestamp("2022-06-30"): [5, 6]
        })
        curr_date = "2021-12-31"
        result = filter_financials_by_date(df, curr_date)

        expected_columns = [pd.Timestamp("2021-06-30"), pd.Timestamp("2021-12-31")]
        self.assertEqual(list(result.columns), expected_columns)

    def test_filter_financials_by_date_non_date_columns(self):
        """Test behavior with non-date columns (they evaluate to NaT and are dropped)."""
        df = pd.DataFrame({
            "2020-01-01": [1],
            "Metric Name": [2],
            "2021-01-01": [3]
        })
        curr_date = "2020-12-31"
        result = filter_financials_by_date(df, curr_date)

        # Only '2020-01-01' should be kept since NaT <= cutoff is False
        expected_columns = ["2020-01-01"]
        self.assertEqual(list(result.columns), expected_columns)

if __name__ == "__main__":
    unittest.main()
