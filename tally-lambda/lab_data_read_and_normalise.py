from typing import Tuple, List, Optional

import polars as pl
from polars import Series

from known_contigs import known_contigs
from schema_1 import schema_1, coord_columns

columns = [
    "contig",
    "position",
    "ref",
    "alt",
    "hom_count",
    "het_count"
]

def retrieve(bucket_name: Optional[str], prefix: str, csv: bool) -> Tuple[pl.DataFrame, List[str]]:
    """
    Returns the variant count data for a specific lab at a specific prefix (i.e. "2020-04-01/").
    Needs to be told whether it is expecting CSV or Parquet formatted data.
    Will then attempt to normalise the data so that the returned DataFrame is
    consistent.
    Also return a list of messages that may be important from the normalisation
    process.

    :param bucket_name: a bucket name in S3 in which we are looking for data, or if none the local filesystem
    :param prefix: the object path to pass to look for data
    :param csv: whether to expect CSV or Parquet files
    :return:
    """
    warning_msgs: List[str] = []

    if not prefix.endswith("/"):
        raise ValueError(f"Prefix must end with a /, the passed in value '{prefix}' did not")

    print(f"Processing {prefix} in {bucket_name}")

    # for test purposes it is useful to be able to source example files locally
    # (in some ways this means that when we test only with local files we are assuming
    # that the polars S3 access code is correct, which feels
    # like a safe bet)
    scan_path = f"s3://{bucket_name}/{prefix}" if bucket_name else f"./{prefix}"

    if csv:
        df = pl.read_csv(f"{scan_path}*.csv", has_header=True)
        #df_schema = df.collect_schema()
        #print(f"Found a scanned collection of CSV objects with schema {df_schema}")
    else:
        df = pl.scan_parquet(f"{scan_path}*.parquet").collect()
        #df_schema = df.collect_schema()

        #print(f"Found a scanned collection of Parquet objects with schema {df_schema}")

    # we can materialise the data now - unless our files grow super
    # large we easily have memory to handle this
    #collected: pl.DataFrame = df.collect(streaming=True)

    wanted_columns: List[Series] = []

    # select out just the columns we want
    for c in df.iter_columns():
        if c.name not in schema_1.names():
            warning_msgs.append(f"Dropped unused column '{c.name}'")
        else:
            wanted_columns.append(c)

    # bring them together and asset the new data frame matches our desired
    # schema
    selected = pl.DataFrame(wanted_columns, schema=schema_1)

    # we want to only keep known contigs (and warn about the ones we are throwing out)
    unknown = selected.filter(pl.col("contig").is_in(known_contigs).not_()).select("contig").unique()

    for u in unknown.rows():
        warning_msgs.append(f"Dropped (one or more) rows with unknown contig '{u[0]}'")

    known = selected.filter(pl.col("contig").is_in(known_contigs))

    # a requirement is that any single site must not have duplicate counts
    # i.e. a variant cannot occur twice in the files for one single lab
    dups = known.filter(pl.struct(coord_columns).is_duplicated())

    if not dups.is_empty():
        raise ValueError("Found duplicates on coordinates")

    # might help if we know it is sorted
    sorted = known.sort(by=coord_columns)

    print(f"The estimate is that our retrieved data contains {sorted.estimated_size("kb")}kb of data")

    return sorted, warning_msgs
