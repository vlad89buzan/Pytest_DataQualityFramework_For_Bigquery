import pytest


@pytest.fixture(scope="session")
def current_release_date():
    return "2025-11-30"
