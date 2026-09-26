from uuid import UUID

import httpx

from app.core.config import settings


class UserServiceClient:
    def __init__(self):
        self.base_url = settings.user_service_url
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def create_user(
        self,
        email: str,
        full_name: str,
    ) -> dict:
        """Create a user in the User Service."""
        payload = {
            "email": email,
            "full_name": full_name,
        }
        
        response = await self.client.post("/api/v1/users", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_user_by_email(self, email: str) -> dict | None:
        response = await self.client.get(f"/api/v1/users/by-email", params={"email": email})
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.client.aclose()
