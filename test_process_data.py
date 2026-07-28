"""Tests for the Soul Foods data-processing step."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from process_data import process_sales_data


REPOSITORY_ROOT = Path(__file__).resolve().parent
DATA_DIRECTORY = REPOSITORY_ROOT / "data"


class ProcessSalesDataTests(unittest.TestCase):
    def test_processed_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_file = Path(temporary_directory) / "output.csv"
            processed = process_sales_data(DATA_DIRECTORY, output_file)
            saved = pd.read_csv(output_file)

        self.assertEqual(
            list(processed.columns),
            ["sales", "date", "region"],
        )
        self.assertEqual(len(processed), 5_880)
        self.assertFalse(processed.isna().any().any())
        self.assertTrue((processed["sales"] > 0).all())
        self.assertEqual(processed["date"].min(), "2018-02-06")
        self.assertEqual(processed["date"].max(), "2022-02-14")
        pd.testing.assert_frame_equal(processed, saved)


if __name__ == "__main__":
    unittest.main()
