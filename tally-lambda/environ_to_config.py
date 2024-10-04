from re import search
from typing import List, Mapping

from lab_config import LabConfig

ENVIRONMENT_NAME_REGEX = r"^LAB_(\d+)_NAME$"


def get_config_from_environment(
    environment_dict: Mapping[str, str]
) -> List[LabConfig]:
    """
    Convert a set of environment variables into the configuration for
    our query engine. These environment variables are a reflection of
    props passed into our top-level CDK construct (so that is where they
    need to be edited - there is no dynamic configuration).

    The environment variables fit a pattern
    LAB_0_NAME
    LAB_0_BUCKET_NAME
    LAB_0_ACCOUNT_NUMBER
    LAB_2_NAME
    LAB_2_BUCKET_NAME
    ...

    where 0 etc can be replaced with any single digit.

    The number chosen has no further value other than defining the order of
    the lab in the list of labs

    Args:
        environment_dict: a dictionry of the environment variables

    Returns:
        a list of Lab configs reflected out of the environment variables
    """
    labs: List[LabConfig] = []

    for e in sorted(environment_dict.keys()):
        re_match = search(ENVIRONMENT_NAME_REGEX, e)

        if re_match:
            # we have found a lab name - which means we can directly go and look for the other
            # settings for this lab
            lab_number = int(re_match[1])
            bn_env_var_name = f"LAB_{lab_number}_BUCKET_NAME"
            an_env_var_name = f"LAB_{lab_number}_ACCOUNT_NUMBER"

            name = environment_dict[e]

            if bn_env_var_name not in environment_dict:
                raise Exception(
                    f"Lab environment variable '{bn_env_var_name}' is missing"
                )

            if an_env_var_name not in environment_dict:
                raise Exception(
                    f"Lab environment variable '{an_env_var_name}' is missing"
                )

            labs.append(
                LabConfig(
                    name=name,
                    bucket_name=environment_dict[bn_env_var_name],
                    account_number=environment_dict[an_env_var_name],
                )
            )

    print(labs)

    return labs
