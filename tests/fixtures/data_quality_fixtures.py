from src.data_quality.data_quality_validation_library import DataQualityLibrary
import pytest
@pytest.fixture(scope='session')
def data_quality_library():
    dql = DataQualityLibrary()
    yield dql