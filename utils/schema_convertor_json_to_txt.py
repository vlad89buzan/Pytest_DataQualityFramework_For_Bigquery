




# utils/schema_converter_json_to_csv.py

import json
from pathlib import Path
from typing import Any

def convert_bq_schema_to_txt(input_json_path: Path | str, output_txt_path: Path | str) -> None:
    """
    Reads BigQuery schema from provided.json
    and writes a proper Python dictionary string with True/False (uppercase)
    to schema.txt – ready to be used in your tests.
    """
    # Read JSON file
    with open(input_json_path, 'r', encoding='utf-8') as f:
        schema_data: list[dict[str, Any]] = json.load(f)

    # Mapping BigQuery → PyArrow/Pandas types
    type_mapping = {
        "STRING": "STRING",
        "BYTES": "BYTES",
        "INT64": "INT64", "INTEGER": "INT64",
        "FLOAT64": "FLOAT64", "FLOAT": "FLOAT64",
        "NUMERIC": "NUMERIC", "BIGNUMERIC": "NUMERIC",
        "BOOL": "BOOL", "BOOLEAN": "BOOL",
        "TIMESTAMP": "TIMESTAMP",
        "DATE": "DATE",
        "TIME": "TIME",
        "DATETIME": "DATETIME",
        "GEOGRAPHY": "STRING",
    }

    lines = []
    for col in schema_data:
        name = col["column_name"]
        bq_type = col["data_type"].upper()
        nullable = col.get("is_nullable", "YES").upper() == "YES"

        arrow_type = type_mapping.get(bq_type, "STRING")  # fallback to STRING

        # Important: Use True/False (Python) instead of true/false
        nullable_str = "True" if nullable else "False"
        line = f'    "{name}": {{"type": "{arrow_type}", "nullable": {nullable_str}}},'
        lines.append(line)

    # Remove trailing comma from the last line
    if lines:
        lines[-1] = lines[-1].rstrip(",")

    result = "\n".join(lines)

    # Optional: wrap in a dict for direct copy-paste into tests
    full_output = "{\n" + result + "\n}"

    # Write to schema.txt
    with open(output_txt_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(full_output)

    print("Schema successfully converted to Python dict with True/False!")
    print(f"   Input  : {input_json_path}")
    print(f"   Output : {output_txt_path}")
    print(f"   Columns: {len(schema_data)}")


if __name__ == "__main__":
    current_dir = Path(__file__).parent
    input_file = current_dir / "provided.json"
    output_file = current_dir / "schema.txt"

    if not input_file.exists():
        print(f"Error: {input_file} not found!")
        print("   Please place your BigQuery schema JSON into utils/provided.json")
    else:
        convert_bq_schema_to_txt(input_file, output_file)