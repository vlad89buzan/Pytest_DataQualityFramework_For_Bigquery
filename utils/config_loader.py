import os
import yaml
from dotenv import load_dotenv
import re

def load_env_config(path="config/env_config.yaml"):
    # Load .env file first
    load_dotenv()

    # Read YAML as raw text
    with open(path, "r") as f:
        content = f.read()

    # Replace ${VAR} with actual environment variables
    def replace_env_var(match):
        var_name = match.group(1)
        return os.getenv(var_name, f"<<MISSING_ENV:{var_name}>>")

    content = re.sub(r"\$\{([^}]+)\}", replace_env_var, content)

    # Load final YAML
    return yaml.safe_load(content)
