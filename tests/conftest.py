import pytest
from tests.fixtures.bigquery_fixtures import *
from tests.fixtures.data_quality_fixtures import *
import yaml

def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="npd5",
        help="Environment to run tests against (prd, ppd, npd1, npd2, ...)"
    )

@pytest.fixture(scope="session")
def environment(pytestconfig):
    env_name = pytestconfig.getoption("env")

    with open("config/env_config.yaml") as f:
        config = yaml.safe_load(f)

    if env_name not in config:
        raise ValueError(f"Unknown environment: {env_name}")

    return config[env_name]

def pytest_itemcollected(item):
    tcid = item.get_closest_marker("tcid")
    if tcid:
        item._nodeid = f"{item.nodeid} [{tcid.args[0]}]"

