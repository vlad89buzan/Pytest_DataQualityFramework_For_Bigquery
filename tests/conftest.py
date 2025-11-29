import pytest
import yaml
import os
import re
import datetime
from dotenv import load_dotenv

from tests.fixtures.bigquery_fixtures import *
from tests.fixtures.data_quality_fixtures import *


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="npd5",
        help="Environment to run tests against (prd, ppd, npd1, npd2, ...)"
    )


@pytest.fixture(scope="session")
def environment(pytestconfig):
    """
    Load environment configuration from .env + env_config.yaml
    """
    # 1️⃣ Load .env variables
    load_dotenv()

    # 2️⃣ Load raw YAML as text
    env_name = pytestconfig.getoption("env")
    with open("config/env_config.yaml", "r") as f:
        content = f.read()

    # 3️⃣ Replace ${VAR} placeholders with actual env values
    def replace_env_var(match):
        var_name = match.group(1)
        return os.getenv(var_name, f"<<MISSING_ENV:{var_name}>>")

    content = re.sub(r"\$\{([^}]+)\}", replace_env_var, content)

    # 4️⃣ Parse YAML
    config = yaml.safe_load(content)

    # 5️⃣ Validate environment exists
    if env_name not in config:
        raise ValueError(f"Unknown environment: {env_name}")

    return config[env_name]


def pytest_itemcollected(item):
    """
    Append TCID marker to nodeid if present
    """
    tcid = item.get_closest_marker("tcid")
    if tcid:
        item._nodeid = f"{item.nodeid} [{tcid.args[0]}]"


def pytest_configure(config):
    """
    Automatically generate timestamped HTML report with env name in the filename
    """
    # Ensure reports folder exists
    os.makedirs("reports", exist_ok=True)

    # Only set HTML report if not provided via CLI
    if not config.option.htmlpath:
        env_name = config.getoption("env")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"reports/{env_name}_report_{timestamp}.html"
        config.option.htmlpath = report_path

    # Ensure self-contained HTML
    config.option.self_contained_html = True
