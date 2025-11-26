from src.connectors.file_system.parquet_reader import ParquetReader
import pytest


@pytest.fixture(scope='session')
def parquet_reader():
    reader = ParquetReader()
    yield reader
