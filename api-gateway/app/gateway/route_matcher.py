from app.gateway.routes import Route, routes


def get_route(method: str, path: str) -> Route | None:
    for route in routes:
        if route.method != method:
            continue

        p_parts = [p for p in route.path.strip("/").split("/") if p]
        r_parts = [r for r in path.strip("/").split("/") if r]

        if len(p_parts) != len(r_parts):
            continue

        matched = True
        for a, b in zip(p_parts, r_parts):
            if a.startswith("{") and a.endswith("}"):
                continue
            if a != b:
                matched = False
                break

        if matched:
            return route

    return None
