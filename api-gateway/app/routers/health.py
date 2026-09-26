from fastapi import APIRouter

from app.services.health_service import HealthService

router = APIRouter()


@router.get("/health")
async def health():
    services = await HealthService.check_services()

    overall = "UP" if all(v == "UP" for v in services.values()) else "DEGRADED"

    return {
        "gateway": "UP",
        "status": overall,
        "services": services,
    }
