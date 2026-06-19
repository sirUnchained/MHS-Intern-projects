import os

# you must configure it
PROXY_URL = "http://127.0.0.1:8889"


def enable_proxy() -> None:
    os.environ["http_proxy"] = PROXY_URL
    os.environ["https_proxy"] = PROXY_URL


def disable_proxy() -> None:
    os.environ["http_proxy"] = ""
    os.environ["https_proxy"] = ""
