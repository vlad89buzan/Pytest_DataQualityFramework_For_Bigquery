from google.cloud import bigquery
import pandas as pd


class BigQueryConnectorContextManager:
    def __init__(self, project_id: str, credentials_path: str = None):
        """
        :param project_id: Google Cloud project ID
        :param credentials_path: Path to service account JSON file (optional).
                                 If not provided, GCP default credentials will be used.
        """
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.client = None

    def __enter__(self):
        try:
            if self.credentials_path:
                self.client = bigquery.Client.from_service_account_json(
                    self.credentials_path,
                    project=self.project_id
                )
            else:
                # Uses environment or workstation credentials
                self.client = bigquery.Client(project=self.project_id)

            return self

        except Exception as e:
            raise ConnectionError(f"Failed to connect to BigQuery: {e}")

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.client:
            self.client.close()

    def get_data_sql(self, sql: str) -> pd.DataFrame:
        """
        Executes a SQL query on BigQuery and returns a pandas DataFrame.
        """
        try:
            query_job = self.client.query(sql)
            df = query_job.to_dataframe()
            return df
        except Exception as e:
            raise RuntimeError(f"Failed to execute SQL query: {e}")
