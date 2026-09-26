import httpx


class ProxyClient:
    # 1. Holds a single shared instance of the async HTTP client
    client: httpx.AsyncClient | None = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        # 2. Ensures the client has been initialized before use
        if cls.client is None:
            raise RuntimeError("HTTP client is not initialized.")
        return cls.client
