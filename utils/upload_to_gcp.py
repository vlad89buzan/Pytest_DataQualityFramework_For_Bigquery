from google.cloud import storage
from google.oauth2 import service_account
import os

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