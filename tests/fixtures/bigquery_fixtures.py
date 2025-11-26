from src.connectors.bigquery.bigquery_connector import BigQueryConnectorContextManager
import pytest


# Optionally, read credentials path from env variable or pytest option
CREDENTIALS_PATH = r"C:\Users\Vladyslav_Buzan\Downloads\scalov-2efd40d6aeca.json"
PROJECT_ID = "scalov"

@pytest.fixture(scope="session")
def bq_connector():
    """
    Pytest fixture that provides a BigQueryConnectorContextManager instance.
    Scope 'session' so it's created once per test session.
    """
    with BigQueryConnectorContextManager(
        project_id=PROJECT_ID,
        credentials_path=CREDENTIALS_PATH
    ) as connector:
        yield connector

