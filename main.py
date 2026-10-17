from typing import List

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

defaults = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}
yaml_layer = {"workers": 6, "api_key": "key-h01x9x76x3"}
env_file = {"port": 8006, "workers": 6}
os_env = {
    "port": 8996,
    "workers": 9,
    "log_level": "info",
    "api_key": "key-v9z495fwlo",
}


def coerce(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return str(value).strip().lower() in ("true", "1", "yes", "on")
    return str(value)


@app.get("/effective-config")
def effective_config(overrides: List[str] = Query(default=[], alias="set")):
    cfg = {}
    for layer in (defaults, yaml_layer, env_file, os_env):
        cfg.update(layer)

    for item in overrides:
        if "=" in item:
            key, value = item.split("=", 1)
            cfg[key.strip().lower()] = value.strip()

    result = {key: coerce(key, value) for key, value in cfg.items()}
    result["api_key"] = "****"
    return result
