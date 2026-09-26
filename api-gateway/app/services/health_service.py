import httpx

from app.proxy.client import ProxyClient
from app.proxy.service_registry import SERVICES


class HealthService:
    @classmethod
    async def check_services(cls):
        client = ProxyClient.get_client()

        result = {}

        for name, service in SERVICES.items():
            try:
                response = await client.get(
                    f"{service.url}/health",
                    timeout=2,
                )

                result[name] = "UP" if response.status_code == 200 else "DOWN"

            except httpx.HTTPError:
                result[name] = "DOWN"

        return result
