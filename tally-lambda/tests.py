import unittest
from typing import List, Tuple, Optional

from polars.polars import ShapeError
from polars.testing import assert_frame_equal, assert_series_equal
import polars as pl
from schema_1 import schema_1
from lab_data_read_and_normalise import retrieve
from lab_data_aggregate import compute

correct_columns = ["contig", "position", "ref", "alt", "hom_count", "het_count"]


class TestRetrieve(unittest.TestCase):

    def test_extra_columns(self):
        df, msgs = retrieve(None, "test-data/test-extra-columns/", True)

        # our only warning message should be mentioning the made-up column
        self.assertIn("a_column_we_dont_need", msgs[0])

    def test_missing_columns(self):
        self.assertRaises(ShapeError, lambda: retrieve(None, "test-data/test-missing-columns/", True))

    def test_unknown_contigs(self):
        df, msgs = retrieve(None, "test-data/test-unknown-contigs/", True)

        # we should have less rows than in the orig CSV
        self.assertEqual(df.select(pl.len()).item(), 5)

        # our only warning message should be mentioning the made-up contig we threw out
        self.assertIn("NC_000999.99", msgs[0])


class TestAggregate(unittest.TestCase):

    def test_simple(self):
        sources: List[Tuple[Optional[str], str, bool]] = [(None, "test-data/labb-1/", True),
                                                          (None, "test-data/labc-1/", True)]

        df, msgs = compute(sources)

        # note some of the tests that this dataset provides
        # - hom and het counts that are zero (not) contributing to the hom_lab_num and het_lab_num counts
        # - basic summing of hom and het counts
        # - sorting of results

        df_truth = pl.DataFrame({
            "contig": ["NC_000001.11", "NC_000001.11", "NC_000001.11", "NC_000002.12"],
            "position": [13595, 14773, 17501, 566583],
            "ref": ["A", "C", "CT", "T"],
            "alt": ["G", "T", "C", "C"],
            "hom_count": [1, 10003, 333, 10],
            "het_count": [1002, 100004, 0, 11],
        }, schema=schema_1)
        df_truth = df_truth.with_columns(
            pl.Series("hom_lab_num", [1, 2, 1, 1], pl.UInt32),
                   pl.Series("het_lab_num", [2, 2, 0, 1], pl.UInt32))

        assert_frame_equal(df, df_truth)


if __name__ == '__main__':
    unittest.main()
