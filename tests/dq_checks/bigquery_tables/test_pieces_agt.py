import pytest

table_name = "scalov.pieces.AGT"


@pytest.fixture(scope='module')
def source_data(bq_connector):
    target_query = """
    select * from scalov.pieces.AGT
    """
    df = bq_connector.get_data_sql(target_query)
    return df

@pytest.mark.tcid("TC-123")
def test_table_exists(bq_connector, data_quality_library):
    data_quality_library.check_table_exists(bq_connector, table_name)

@pytest.mark.tcid("TC-124")
def test_table_not_empty(bq_connector, data_quality_library):
    data_quality_library.check_table_is_not_empty(bq_connector, table_name)

@pytest.mark.tcid("TC-125")
def test_null_values(bq_connector, data_quality_library, source_data):
    columns_to_check = ["Kromka", "Thickness"]
    data_quality_library. \
        check_not_null_values(source_data
                              , column_names=columns_to_check  # comment this line if all columns needed
                              )

@pytest.mark.tcid("TC-126")
def test_duplicates(bq_connector, data_quality_library, source_data):
    columns_to_check = ["Code", "Thickness"]
    data_quality_library.check_duplicates(source_data
                                          , column_names=columns_to_check
                                          , check_each_column=True
                                          )

@pytest.mark.tcid("TC-127")
def test_duplicates_subset(bq_connector, data_quality_library, source_data):
    columns_to_check = ["Code", "Thickness"]
    data_quality_library.check_duplicates(source_data
                                          , column_names=columns_to_check
                                          # , check_each_column=True
                                          )

@pytest.mark.tcid("TC-128")
def test_duplicates_by_raw(bq_connector, data_quality_library, source_data):
    # columns_to_check = ["Code", "Thickness"]
    data_quality_library.check_duplicates(source_data
                                          # , column_names=columns_to_check
                                          # , check_each_column=True
                                          )

@pytest.mark.tcid("TC-129")
def test_schema_is_correct(bq_connector, data_quality_library):
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

    data_quality_library.check_table_schema(bq_connector, table_name, expected_schema)

@pytest.mark.tcid("TC-130")
def test_column_validity(bq_connector, data_quality_library, source_data):
    import pandas as pd
    rules = {
        # "Thickness": {"min": 10, "max": 20, "allowed_values": [8, 18]},
        "bq_load_dttm": {"max": pd.Timestamp("2025-11-25 03:00:15", tz="UTC")},
    }
    data_quality_library.check_column_validity(source_data, rules)


@pytest.fixture(scope='module')
def expected(bq_connector):
    target_query = """
    SELECT * FROM `scalov.pieces.AGT`
    where Code like '%732%'
    """
    df = bq_connector.get_data_sql(target_query)
    return df


@pytest.fixture(scope='module')
def actual(bq_connector):
    target_query = """
    SELECT * FROM `scalov.pieces.AGT_381`
    """
    df = bq_connector.get_data_sql(target_query)
    return df

@pytest.mark.tcid("TC-131")
def test_counts(expected, actual, data_quality_library):
    data_quality_library.check_count(expected, actual)

@pytest.mark.tcid("TC-132")
def test_datasets(expected, actual, data_quality_library):
    data_quality_library.check_data_full_data_set(expected, actual)
