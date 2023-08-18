import os

def check_env_variables(required_variables: list[str] = ["VEGA_USER_WALLET_NAME", "VEGA_WALLET_TOKENS_PASSPHRASE_FILE", "VEGA_WALLET_TOKENS_FILE"]):
    for env_var in required_variables:
        if os.getenv(env_var, None) is None:
            raise EnvironmentError(f"The \"{env_var}\" environment variable is not set, but it is required")