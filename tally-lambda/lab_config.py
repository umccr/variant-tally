from dataclasses import dataclass


@dataclass
class LabConfig:
    """
    Class for the details of a lab
    """
    # the displayable lab name for reports and messages
    name: str

    bucket_name: str

    account_number: str