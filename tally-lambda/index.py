from datetime import datetime, timedelta, UTC
from os import environ
from time import time, sleep
from typing import Any, List

from boto3 import resource
from boto3.dynamodb.conditions import Key

from environ_to_config import get_config_from_environment
from q import query_labs

DAILY_MAX = 5


def handler(event: Any, context: Any):
    print(event)
    print(context)

    labs = get_config_from_environment(environ)

    query_labs(labs)

    return None


if __name__ == "__main__":
    environ["LAB_0_NAME"] = "LabA"
    environ[
        "LAB_0_BUCKET_NAME"
    ] = "variant-tally-example-lab-1"
    environ[
        "LAB_0_ACCOUNT_NUMBER"
    ] = "602836945884"

    environ["LAB_2_NAME"] = "LabB"
    environ[
        "LAB_2_BUCKET_NAME"
    ] = "variant-tally-example-lab-2"
    environ[
        "LAB_2_ACCOUNT_NUMBER"
    ] = "602836945884"

    handler(
        {
            "Records": [
                {
                    "messageId": "...",
                    "receiptHandle": "...",
                    "body": "ga4gh:VA.vokjXk9l7Wrw4IkjCGM5lxjLWJz8sfye",
                    "attributes": {
                        "ApproximateReceiveCount": "1",
                        "SentTimestamp": "1545082649183",
                        "SenderId": "ANACCESSID:tbd@place.com",
                        "ApproximateFirstReceiveTimestamp": "1545082649185",
                    },
                    "messageAttributes": {
                        "prefix": {"stringValue": "2024-05-13"},
                        "correlation": {"stringValue": "abcd"},
                    },
                    "md5OfBody": "efgh",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws:sqs:ap-southeast-2:123456789012:my-queue",
                    "awsRegion": "ap-southeast-2",
                }
            ]
        },
        {},
    )
