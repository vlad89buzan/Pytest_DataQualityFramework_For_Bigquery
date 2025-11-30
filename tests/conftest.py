import pytest
import yaml
import os
import re
import datetime
from dotenv import load_dotenv
from utils.upload_to_gcp import * # upload to bucket
from tests.fixtures.bigquery_fixtures import *
from tests.fixtures.data_quality_fixtures import *
from tests.fixtures.global_vars_fixture import *


# ───────────────────────────────
# CLI OPTIONS
# ───────────────────────────────
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="npd5",
        help="Environment to run tests against (prd, ppd, npd1, npd2, ...)"
    )
    parser.addoption(
        "--save-local",
        action="store_true",
        help="Save report locally instead of uploading to GCP bucket",
    )


# ───────────────────────────────
# ENVIRONMENT FIXTURE
# ───────────────────────────────
@pytest.fixture(scope="session")
def environment(pytestconfig):
    """
    Load environment configuration from .env + env_config.yaml
    """
    load_dotenv()
    env_name = pytestconfig.getoption("env")

    with open("config/env_config.yaml", "r") as f:
        content = f.read()

    # Replace ${VAR} placeholders with actual env values
    def replace_env_var(match):
        var_name = match.group(1)
        return os.getenv(var_name, f"<<MISSING_ENV:{var_name}>>")

    content = re.sub(r"\$\{([^}]+)\}", replace_env_var, content)
    config = yaml.safe_load(content)

    if env_name not in config:
        raise ValueError(f"Unknown environment: {env_name}")

    # Store environment config in pytest for access later
    pytestconfig._env_cfg = config[env_name]
    return config[env_name]


# ───────────────────────────────
# TCID MARKER
# ───────────────────────────────
def pytest_itemcollected(item):
    tcid = item.get_closest_marker("tcid")
    if tcid:
        item._nodeid = f"{item.nodeid} [{tcid.args[0]}]"


# ───────────────────────────────
# REPORT CONFIGURATION
# ───────────────────────────────
def pytest_configure(config):
    env_name = config.getoption("env")
    save_local = config.getoption("save_local")

    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    report_filename = f"{env_name}_report_{timestamp}.html"

    # Local folder structure: reports/<env>/<YYYYMMDD>/
    base_dir = f"reports/{env_name}/{date_str}"
    os.makedirs(base_dir, exist_ok=True)

    if save_local:
        report_path = f"{base_dir}/{report_filename}"
    else:
        # Temporary local file before upload
        report_path = f"{base_dir}/tmp_{report_filename}"

    if not config.option.htmlpath:
        config.option.htmlpath = report_path

    config.option.self_contained_html = True

    # Store for later access
    config._report_path = report_path
    config._final_report_filename = report_filename
    config._date_str = date_str
    config._env_name = env_name



