from datetime import date
from typing import Tuple, Optional

from boto3 import client
from mypy_boto3_s3.client import S3Client

from lab_config import LabConfig


def find(lab: LabConfig) -> Optional[Tuple[str,bool]]:
    """
    Find where in a bucket the latest lab data is and what format it is.
    If there is no data in the bucket at this prefix then

    Args:
        lab: a lab to query

    Returns:
        a tuple with the prefix in the lab for where the latest data is and a boolean if the data is CSV (parquet otherwise)
    """
    s3_client: S3Client = client("s3")

    # look for the latest data submission - folders are in the format YYYY-mm-dd
    prefix = "lab-counts/"

    list_obj_response = s3_client.list_objects_v2(Bucket=lab.bucket_name, Prefix=prefix)

    # find all the folder names that are plausibly an ISO date
    possible_dates = filter(lambda a: len(a) == 10, map(lambda b : b['Key'][len(prefix):-1], list_obj_response["Contents"]))

    # find the latest date
    latest_date = max(map(lambda n: date.fromisoformat(n), possible_dates))
    latest_date_prefix = f"{prefix}{latest_date.isoformat()}/"

    # now try to determine which files are actually in this folder
    found_csv = False
    found_parquet = False

    for obj in list_obj_response["Contents"]:
        if obj["Key"].startswith(latest_date_prefix) and obj["Key"].endswith(".csv"):
            found_csv = True
        if obj["Key"].startswith(latest_date_prefix) and obj["Key"].endswith(".parquet"):
            found_parquet = True

    if found_csv and found_parquet:
        raise Exception("Specific lab date cannot have both CSV and Parquet data")

    if not found_csv and not found_parquet:
        return None

    return latest_date_prefix, found_csv
