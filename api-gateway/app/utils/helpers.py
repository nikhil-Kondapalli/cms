from app.proxy.service_registry import SERVICES, Service


def get_service(prefix: str) -> Service:
    try:
        return SERVICES[prefix]
    except KeyError:
        raise ValueError(f"Unknown service '{prefix}'")
