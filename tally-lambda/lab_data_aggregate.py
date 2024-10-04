from typing import List, Tuple

import polars as pl
from polars import DataFrame

from lab_data_read_and_normalise import retrieve
from schema_1 import schema_1, coord_columns


def compute(lab_sources: List[Tuple[str, str, bool]]) -> Tuple[DataFrame, List[str]]:
    """

    Args:
        lab_sources: precise instructions for where to load the lab data from

    Returns:

    """
    msgs_combined: List[str] = []
    lab_combined = pl.DataFrame(schema=schema_1)

    for lab_source in lab_sources:
        lab_data, lab_msgs = retrieve(lab_source[0], lab_source[1], lab_source[2])

        msgs_combined.extend(lab_msgs)

        lab_combined = lab_combined.vstack(lab_data)

    agg = (
        lab_combined
            .group_by(coord_columns)
            .agg(pl.col('hom_count').sum(),
               pl.col('het_count').sum(),
               hom_lab_num=pl.col('hom_count').cast(pl.Boolean).sum(),
               het_lab_num=pl.col('het_count').cast(pl.Boolean).sum())
            .sort(by=coord_columns)
    )

    return agg, msgs_combined
