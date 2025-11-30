import os
import re

from dotenv import load_dotenv

load_dotenv()
print(os.getenv('GSA_NPD'))
env_name = 'npd5'

with open("config/env_config.yaml", "r") as f:
    content = f.read()



def replace_env_var(match):
    var_name = match.group(1)
    return os.getenv(var_name, f"<<MISSING_ENV:{var_name}>>")


content = re.sub(r"\$\{([^}]+)\}", replace_env_var, content)
print(content)
