import pandas as pd


class DataQualityLibrary:
    """
    A library of static methods for performing data quality checks on pandas DataFrames.

    This class is intended to be used in a PyTest-based testing framework to validate
    the quality of data in DataFrames. Each method performs a specific data quality
    check and uses assertions to ensure that the data meets the expected conditions.
    """

    @staticmethod
    def check_duplicates(df: pd.DataFrame, column_names=None, check_each_column=False):
        """
        Check for duplicates in the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame to check.
            column_names (list, optional): Columns to check duplicates on.
                If None, checks entire row.
            check_each_column (bool, optional): If True and column_names is provided,
                check duplicates **per column individually**.

        Raises:
            AssertionError: If duplicates are found, showing counts.
        """
        if column_names:
            if check_each_column:
                # Check duplicates individually for each column
                for col in column_names:
                    duplicates = df[df.duplicated(subset=[col], keep=False)]
                    if not duplicates.empty:
                        dup_counts = (
                            duplicates.groupby([col])
                            .size()
                            .reset_index(name='count')
                            .sort_values('count', ascending=False)
                        )
                        raise AssertionError(
                            f"Duplicate values found in column '{col}':\n{dup_counts}"
                        )
            else:
                # Check duplicates based on combination of columns
                duplicates = df[df.duplicated(subset=column_names, keep=False)]
                if not duplicates.empty:
                    dup_counts = (
                        duplicates.groupby(column_names)
                        .size()
                        .reset_index(name='count')
                        .sort_values('count', ascending=False)
                    )
                    raise AssertionError(
                        f"Duplicate rows found on combination of columns {column_names}:\n{dup_counts}"
                    )
        else:
            # Full-row duplicates
            duplicates = df[df.duplicated(keep=False)]
            if not duplicates.empty:
                dup_counts = (
                    duplicates.groupby(list(df.columns))
                    .size()
                    .reset_index(name='count')
                    .sort_values('count', ascending=False)
                )
                raise AssertionError(
                    f"Duplicate full rows found:\n{dup_counts}"
                )

    @staticmethod
    def check_count(df1: pd.DataFrame, df2: pd.DataFrame):
        """Check that two DataFrames have the same number of rows."""
        assert len(df1) == len(df2), f"Row count mismatch: {len(df1)} != {len(df2)}"

    @staticmethod
    def check_data_full_data_set(df1, df2,subset_columns=None):
        """
        Check that two datasets match exactly, like UNION ALL of EXCEPT in SQL.
        Automatically aligns column types for comparison (e.g., datetime vs object).
        Shows which rows are in one dataset but not the other, with counts.

        Args:
            df1 (pd.DataFrame): First dataset (source/expected).
            df2 (pd.DataFrame): Second dataset (target/actual).
            subset_columns (list, optional): Columns to compare. If None, compare all columns.

        Raises:
            AssertionError: If any row mismatches exist.
        """
        # Columns to compare
        columns = subset_columns or df1.columns.tolist()

        # Align column types
        for col in columns:
            if col not in df2.columns:
                raise ValueError(f"Column '{col}' not found in df2")
            # If either column is datetime, convert both to datetime
            if pd.api.types.is_datetime64_any_dtype(df1[col]) or pd.api.types.is_datetime64_any_dtype(df2[col]):
                df1[col] = pd.to_datetime(df1[col], errors='coerce')
                df2[col] = pd.to_datetime(df2[col], errors='coerce')
            # If either column is numeric but different type, convert both to float
            elif pd.api.types.is_numeric_dtype(df1[col]) or pd.api.types.is_numeric_dtype(df2[col]):
                df1[col] = pd.to_numeric(df1[col], errors='coerce')
                df2[col] = pd.to_numeric(df2[col], errors='coerce')
            # Otherwise, compare as string
            else:
                df1[col] = df1[col].astype(str)
                df2[col] = df2[col].astype(str)

        # Rows in df1 but not in df2
        diff1 = df1.merge(df2, on=columns, how='left', indicator=True).query('_merge == "left_only"')[columns].copy()
        diff1['diff_type'] = 'in source not in target'

        # Rows in df2 but not in df1
        diff2 = df2.merge(df1, on=columns, how='left', indicator=True).query('_merge == "left_only"')[columns].copy()
        diff2['diff_type'] = 'in target not in source'

        # Combine differences
        differences = pd.concat([diff1, diff2], ignore_index=True)

        if not differences.empty:
            # Count duplicates for clarity
            diff_counts = differences.groupby(columns + ['diff_type']).size().reset_index(name='count')
            raise AssertionError(
                f"Datasets do not match! Differences found:\n{diff_counts.to_string(index=False)}"
            )

    @staticmethod
    def check_dataset_is_not_empty(df: pd.DataFrame):
        """Check that the DataFrame is not empty."""
        assert not df.empty, "DataFrame is empty"

    @staticmethod
    def check_dataset_is_empty(df: pd.DataFrame):
        """Check that the DataFrame is not empty."""
        assert  df.empty, "DataFrame is not empty"

    @staticmethod
    def check_not_null_values(df: pd.DataFrame, column_names=None):
        """Check that specified columns do not contain null values."""
        if column_names:
            for col in column_names:
                assert df[col].notnull().all(), f"Null values found in column: {col}"
        else:
            assert df.notnull().all().all(), "Null values found in DataFrame"

    @staticmethod
    def check_column_validity(
            df: pd.DataFrame,
            column_rules: dict
    ) -> pd.DataFrame:
        """
        Universal column validity checker.

        This method validates columns in a DataFrame according to user-defined rules.
        It supports numeric range checks, membership checks, and custom conditions.

        Args:
            df (pd.DataFrame): DataFrame to check.
            column_rules (dict): Dictionary where keys are column names and values are rule dictionaries.
                Supported rule keys:
                    - "min": minimum allowed value (inclusive)
                    - "max": maximum allowed value (inclusive)
                    - "allowed_values": list of allowed values
                    - "condition": lambda function returning True for valid rows

        Returns:
            pd.DataFrame: DataFrame of invalid rows (empty if all rows are valid).

        Raises:
            AssertionError: If any invalid values are found.

        Example:
            ```python
            # Example 1: Check numeric ranges
            DataQualityLibrary.check_column_validity(
                df=source_data,
                column_rules={
                    "min_time_spent": {"min": 0, "max": 1000},
                    "duration_minutes": {"min": 1}
                }
            )

            # Example 2: Check allowed categorical values
            DataQualityLibrary.check_column_validity(
                df=source_data,
                column_rules={
                    "facility_type": {"allowed_values": ["Clinic", "Hospital", "Lab"]}
                }
            )

            # Example 3: Custom logic (dates must not be in the future)
            DataQualityLibrary.check_column_validity(
                df=source_data,
                column_rules={
                    "visit_date": {"condition": lambda x: x <= pd.Timestamp.today()}
                }
            )
            ```
        """
        all_invalid_rows = []

        for column, rules in column_rules.items():
            invalid_mask = pd.Series(False, index=df.index)

            # --- Numeric range checks ---
            if "min" in rules:
                invalid_mask |= df[column] < rules["min"]
            if "max" in rules:
                invalid_mask |= df[column] > rules["max"]

            # --- Allowed values check ---
            if "allowed_values" in rules:
                invalid_mask |= ~df[column].isin(rules["allowed_values"])

            # --- Custom condition check ---
            if "condition" in rules:
                invalid_mask |= ~df[column].apply(rules["condition"])

            # Collect invalid rows
            invalid_rows = df.loc[invalid_mask, [column]]
            if not invalid_rows.empty:
                invalid_rows = invalid_rows.assign(invalid_column=column)
                all_invalid_rows.append(invalid_rows)

        # Combine invalid rows across all columns
        if all_invalid_rows:
            invalid_df = pd.concat(all_invalid_rows)
            raise AssertionError(
                f"Invalid values found in the following columns:\n{invalid_df.head(20)}\n"
                f"(Total {len(invalid_df)} invalid rows)"
            )
        else:
            return pd.DataFrame(columns=df.columns)

    @staticmethod
    def check_table_exists(connector, table_name: str):
        """
        Check that a table exists in the data source.

        Args:
            connector: A database/BigQuery connector object with a method to list or query tables.
            table_name (str): Full table identifier (e.g., 'dataset.table' or BigQuery 'project.dataset.table').

        Raises:
            AssertionError: If the table does not exist.
        """
        try:
            # Attempt to fetch a single row to confirm table exists
            sql = f"SELECT 1 FROM `{table_name}` LIMIT 1"
            df = connector.get_data_sql(sql)
            # If DataFrame is returned, table exists
            assert df is not None, f"Query returned None for table {table_name}"
        except Exception as e:
            raise AssertionError(f"Table {table_name} does not exist or is not accessible. Error: {e}")

    @staticmethod
    def check_table_is_not_empty(connector, table_name: str, limit: int = 1):
        """
        Check that a table is not empty.

        Args:
            connector: A database/BigQuery connector object with a method `get_data_sql`.
            table_name (str): Full table identifier (e.g., 'dataset.table' or 'project.dataset.table').
            limit (int, optional): Number of rows to fetch. Default is 1.

        Raises:
            AssertionError: If the table is empty.
        """
        sql = f"SELECT * FROM `{table_name}` LIMIT {limit}"
        df = connector.get_data_sql(sql)
        assert not df.empty, f"Table {table_name} is empty"

    @staticmethod
    def check_table_schema(bq_connector, table_name: str, expected_schema: dict):
        """
        Validate that a BigQuery table schema matches expected schema.

        Args:
            bq_connector: BigQuery connector with .client attribute.
            table_name (str): Full BigQuery table name: "dataset.table" or "project.dataset.table"
            expected_schema (dict): Expected column definitions:
                {
                    "column_name": {
                        "type": "STRING|INT64|FLOAT64|DATE|TIMESTAMP|BOOLEAN|...",
                        "nullable": True/False
                    },
                    ...
                }

        Raises:
            AssertionError: When there are mismatches in schema.
        """
        # Load actual schema from BigQuery
        table = bq_connector.client.get_table(table_name)
        actual_schema = {field.name: field for field in table.schema}

        errors = []

        # 1. Check missing or mismatched columns
        for col, expected in expected_schema.items():
            if col not in actual_schema:
                errors.append(f"Missing column: {col}")
                continue

            field = actual_schema[col]

            # Compare data type
            # Compare data type with normalization
            actual_type = field.field_type.upper()
            expected_type = expected["type"].upper()

            TYPE_EQUIVALENTS = {
                "INTEGER": "INT64",
                "INT64": "INT64",
                "FLOAT": "FLOAT64",
                "FLOAT64": "FLOAT64",
                "BOOLEAN": "BOOL",
                "BOOL": "BOOL",
                "STRING": "STRING",
                "BYTES": "BYTES",
                "DATE": "DATE",
                "TIMESTAMP": "TIMESTAMP",
            }

            actual_type_norm = TYPE_EQUIVALENTS.get(actual_type, actual_type)
            expected_type_norm = TYPE_EQUIVALENTS.get(expected_type, expected_type)

            if actual_type_norm != expected_type_norm:
                errors.append(
                    f"Type mismatch for '{col}': expected {expected_type_norm}, got {actual_type_norm}"
                )

            # Compare nullability
            actual_nullable = (field.mode.upper() == "NULLABLE")
            expected_nullable = expected["nullable"]

            if actual_nullable != expected_nullable:
                errors.append(
                    f"Nullability mismatch for '{col}': expected nullable={expected_nullable}, got nullable={actual_nullable}"
                )

        # 2. Check extra columns (not expected)
        for col in actual_schema:
            if col not in expected_schema:
                errors.append(f"Unexpected column in table: {col}")

        # Raise if errors exist
        if errors:
            raise AssertionError(
                f"Schema validation failed for table '{table_name}':\n" +
                "\n".join(errors)
            )


