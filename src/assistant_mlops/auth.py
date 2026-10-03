import os


def endpoint_headers(prefix, key):
    """Credentials belong only to the explicitly configured endpoint, never its fallback."""
    token = os.getenv(f"{prefix}_PROXY_TOKEN", "").strip()
    cookie = os.getenv(f"{prefix}_PROXY_COOKIE", "").replace("\n", "").strip()
    if cookie.lower().startswith("cookie:"):
        cookie = cookie.split(":", 1)[1].strip()
    headers = {"Authorization": f"token {token}" if token else f"Bearer {key}"}
    if cookie:
        headers["Cookie"] = cookie
    return headers
