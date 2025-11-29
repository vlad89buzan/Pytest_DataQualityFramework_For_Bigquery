from src.connectors.bigquery.bigquery_connector import BigQueryConnectorContextManager
import pytest
import os


# Optionally, read credentials path from env variable or pytest option


@pytest.fixture(scope="session")
def bq_connector(environment):
    """
    Pytest fixture that provides a BigQueryConnectorContextManager instance.
    Scope 'session' so it's created once per test session.
    """
    project_id = environment["project"]
    credentials_path = environment["credentials"]

    with BigQueryConnectorContextManager(
            project_id=project_id,
            credentials_path=credentials_path
    ) as connector:
        yield connector
