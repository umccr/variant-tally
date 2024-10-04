from datetime import date
from typing import List, Tuple
import s3fs
import polars as pl
from boto3 import resource, client
from mypy_boto3_s3.client import S3Client
from mypy_boto3_s3.service_resource import S3ServiceResource

from lab_config import LabConfig
from schema_1 import schema_1, coord_columns
from lab_data_read_and_normalise import retrieve
from lab_data_discover import find
from lab_data_aggregate import compute

def query_labs(labs: List[LabConfig]) -> str:
    """
    Query a set of labs for a report on rare variant occurrence.

    Args:
        labs: a list of labs to query

    Returns:

    """
    if not labs or len(labs) == 0:
        raise Exception("No labs provided to query engine")

    # for ease of testing we want to split out the discovery of labs from the actual processing
    # we collect a list of bucket,prefix,csv for each lab source
    lab_sources: List[Tuple[str, str, bool]] = []

    for lab in labs:
        latest_date_prefix, found_csv = find(lab)

        if latest_date_prefix is None:
            print(f"Lab {lab.name} had no data")
            continue

        lab_sources.append((lab.bucket_name, latest_date_prefix, found_csv))

    df, msgs = compute(lab_sources)

    for lab in labs:
        fs = s3fs.S3FileSystem()
        destination = f"s3://{lab.bucket_name}/aggregate-counts/latest.parquet"

        # write parquet
        with fs.open(destination, mode='wb') as f:
            df.write_parquet(f)

    return "\n".join(msgs)
