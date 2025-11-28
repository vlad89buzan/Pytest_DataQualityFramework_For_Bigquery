"""
Description: Data Quality checks for pieces tables
Requirement(s): TICKET-1234
Author(s): Name Surname
"""

import pytest
import pandas as pd


# -------------------- Table fixtures --------------------
@pytest.fixture(scope="module")
def table_AGT(environment):
    return environment["tables"]["AGT"]


@pytest.fixture(scope="module")
def table_AGT_381(environment):
    return environment["tables"]["AGT_381"]


# -------------------- Data fixtures --------------------
@pytest.fixture(scope='module')
def source_data(bq_connector, table_AGT):
    """Load full data from AGT table."""
    target_query = f"SELECT * FROM `{table_AGT}`"
    df = bq_connector.get_data_sql(target_query)
    return df


@pytest.fixture(scope='module')
def expected(bq_connector, table_AGT):
    """Load filtered data from AGT table for comparison."""
    target_query = f"""
    SELECT * FROM `{table_AGT}`
    WHERE Code LIKE '%732%'
    """
    df = bq_connector.get_data_sql(target_query)
    return df


@pytest.fixture(scope='module')
def actual(bq_connector, table_AGT_381):
    """Load full data from AGT_381 table for comparison."""
    target_query = f"SELECT * FROM `{table_AGT_381}`"
    df = bq_connector.get_data_sql(target_query)
    return df


# -------------------- Tests --------------------
@pytest.mark.tcid("TC-123")
def test_table_exists(bq_connector, data_quality_library, table_AGT):
    data_quality_library.check_table_exists(bq_connector, table_AGT)


@pytest.mark.tcid("TC-124")
def test_table_not_empty(bq_connector, data_quality_library, table_AGT):
    data_quality_library.check_table_is_not_empty(bq_connector, table_AGT)


@pytest.mark.tcid("TC-125")
def test_null_values(data_quality_library, source_data):
    columns_to_check = ["Kromka", "Thickness"]
    data_quality_library.check_not_null_values(
        source_data,
        column_names=columns_to_check  # comment this line if all columns needed
    )


@pytest.mark.tcid("TC-126")
def test_duplicates(data_quality_library, source_data):
    columns_to_check = ["Code", "Thickness"]
    data_quality_library.check_duplicates(
        source_data,
        column_names=columns_to_check,
        check_each_column=True
    )


@pytest.mark.tcid("TC-127")
def test_duplicates_subset(data_quality_library, source_data):
    columns_to_check = ["Code", "Thickness"]
    data_quality_library.check_duplicates(
        source_data,
        column_names=columns_to_check
        # , check_each_column=True
    )


@pytest.mark.tcid("TC-128")
def test_duplicates_by_raw(data_quality_library, source_data):
    data_quality_library.check_duplicates(
        source_data
        # , column_names=columns_to_check
        # , check_each_column=True
    )


@pytest.mark.tcid("TC-129")
def test_schema_is_correct(data_quality_library, bq_connector, table_AGT):
    expected_schema = {
        "bq_load_dttm": {"type": "TIMESTAMP", "nullable": True},
        "Code": {"type": "STRING", "nullable": True},
        "Name": {"type": "STRING", "nullable": True},
        "Kromka": {"type": "STRING", "nullable": True},
        "Thickness": {"type": "INT64", "nullable": True},
        "Length": {"type": "INT64", "nullable": True},
        "Width": {"type": "INT64", "nullable": True},
        "Stock_balance_in_sheets": {"type": "STRING", "nullable": True},
        "Stock_balance_in_pieces": {"type": "STRING", "nullable": True},
        "Reserve_balance_in_sheets": {"type": "STRING", "nullable": True},
        # "Reserve_balance_in_pieces": {"type": "STRING", "nullable": False},
    }
    data_quality_library.check_table_schema(bq_connector, table_AGT, expected_schema)


@pytest.mark.tcid("TC-130")
def test_column_validity(data_quality_library, source_data):
    rules = {
        # "Thickness": {"min": 10, "max": 20, "allowed_values": [8, 18]},
        "bq_load_dttm": {"max": pd.Timestamp("2025-11-25 03:00:15", tz="UTC")},
    }
    data_quality_library.check_column_validity(source_data, rules)


@pytest.mark.tcid("TC-131")
def test_counts(expected, actual, data_quality_library):
    data_quality_library.check_count(expected, actual)


@pytest.mark.tcid("TC-132")
def test_datasets(expected, actual, data_quality_library):
    data_quality_library.check_data_full_data_set(expected, actual)
