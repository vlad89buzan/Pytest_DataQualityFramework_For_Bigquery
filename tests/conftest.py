import pytest
import yaml
import os
import re
import datetime
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account

from tests.fixtures.bigquery_fixtures import *
from tests.fixtures.data_quality_fixtures import *


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


# ───────────────────────────────
# UPLOAD REPORT TO GCP
# ───────────────────────────────
def pytest_unconfigure(config):
    save_local = config.getoption("save_local")

    if save_local:
        return  # local save only

    env_cfg = getattr(config, "_env_cfg", None)
    if not env_cfg:
        print("\n⚠️ Environment config not loaded. Cannot upload.\n")
        return

    bucket_name = env_cfg.get("gcp_bucket")
    sa_path = env_cfg.get("credentials")

    if not bucket_name:
        print("\n⚠️ gcp_bucket not found in environment config. Upload skipped.\n")
        return
    if not sa_path or not os.path.exists(sa_path):
        print(f"\n❌ Service account file not found: {sa_path}\n")
        return

    temp_report_path = getattr(config, "_report_path", None)
    final_filename = getattr(config, "_final_report_filename", None)
    env_name = getattr(config, "_env_name", None)
    date_str = getattr(config, "_date_str", None)

    if not temp_report_path or not os.path.exists(temp_report_path):
        print("\n⚠️ Report file not found. Cannot upload.\n")
        return

    # GCP path: pytest_reports/<env>/<YYYYMMDD>/<filename.html>
    gcs_path = f"pytest_reports/{env_name}/{date_str}/{final_filename}"

    try:
        print(f"\n📤 Uploading report to GCP:")
        print(f"   Bucket: {bucket_name}")
        print(f"   Path:   {gcs_path}")
        print(f"   Using SA: {sa_path}")

        # Use the same service account as BigQuery
        creds = service_account.Credentials.from_service_account_file(sa_path)
        client = storage.Client(credentials=creds)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(temp_report_path)

        print("✅ Report successfully uploaded to GCP.\n")

    except Exception as e:
        print(f"\n❌ Failed to upload report: {e}\n")
