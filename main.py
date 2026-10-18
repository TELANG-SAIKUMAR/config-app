from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: lets the grader's web page call your API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Layers, lowest priority first
DEFAULTS = {
    "port": 8000, "workers": 1, "debug": False,
    "log_level": "info", "api_key": "default-secret-000",
}
YAML_LAYER = {"workers": 6, "api_key": "key-h01x9x76x3"}
DOTENV_LAYER = {"port": 8006, "NUM_WORKERS": 6}   # raw names from the file
OS_ENV_LAYER = {                                   # APP_ prefix already removed
    "port": 8996, "workers": 9,
    "log_level": "info", "api_key": "key-v9z495fwlo",
}

ALIASES = {"NUM_WORKERS": "workers"}


def coerce(key, value):
    """Turn values into the right type."""
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("true", "1", "yes", "on")
    return str(value)


@app.get("/")
@app.get("/effective-config")
def effective_config(request: Request):
    config = {}

    # 1. merge layers: later ones overwrite earlier ones
    for layer in (DEFAULTS, YAML_LAYER, DOTENV_LAYER, OS_ENV_LAYER):
        for key, value in layer.items():
            key = ALIASES.get(key, key)
            config[key] = coerce(key, value)

    # 2. CLI overrides from ?set=key=value (highest priority)
    for item in request.query_params.getlist("set"):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)   # split only on the FIRST "="
        key = ALIASES.get(key.strip(), key.strip())
        try:
            config[key] = coerce(key, value.strip())
        except ValueError:
            pass  # ignore a bad number like port=abc

    # 3. never leak the secret
    config["api_key"] = "****"
    return config
