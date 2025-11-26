import pytest
from tests.fixtures.bigquery_fixtures import *
from tests.fixtures.data_quality_fixtures import *





def pytest_itemcollected(item):
    tcid = item.get_closest_marker("tcid")
    if tcid:
        item._nodeid = f"{item.nodeid} [{tcid.args[0]}]"
