from src.connectors.bigquery.bigquery_connector import BigQueryConnectorContextManager

sql = """
SELECT * FROM `scalov.pieces.AGT`
"""

with BigQueryConnectorContextManager(
        project_id="scalov",
        credentials_path=r"C:\Users\Vladyslav_Buzan\Downloads\scalov-2efd40d6aeca.json"
) as bq:
    df = bq.get_data_sql(sql)
    print(df)
