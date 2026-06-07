import time
import logging
from ninja import Router, Schema
from django.db import connection, OperationalError
from django.core.cache import cache

logger = logging.getLogger(__name__)

router = Router(tags=["Health"])


class ComponentStatus(Schema):
    status: str
    latency_ms: float | None = None
    detail: str | None = None


class HealthSchema(Schema):
    status: str  # "ok" | "degraded" | "down"
    database: ComponentStatus
    cache: ComponentStatus


def _check_db() -> ComponentStatus:
    start = time.monotonic()
    try:
        connection.ensure_connection()
        connection.cursor().execute("SELECT 1")
        return ComponentStatus(status="ok", latency_ms=round((time.monotonic() - start) * 1000, 2))
    except OperationalError as e:
        logger.error("Health DB check failed: %s", e)
        return ComponentStatus(status="down", detail=str(e))


def _check_cache() -> ComponentStatus:
    start = time.monotonic()
    try:
        cache.set("_health_ping", "1", timeout=5)
        hit = cache.get("_health_ping")
        if hit != "1":
            return ComponentStatus(status="degraded", detail="write/read mismatch")
        return ComponentStatus(status="ok", latency_ms=round((time.monotonic() - start) * 1000, 2))
    except Exception as e:
        logger.error("Health cache check failed: %s", e)
        return ComponentStatus(status="down", detail=str(e))


@router.get("/", response={200: HealthSchema, 503: HealthSchema}, auth=None, throttle=[])
def health(request):
    db = _check_db()
    cache_status = _check_cache()

    all_ok = db.status == "ok" and cache_status.status == "ok"
    any_down = db.status == "down" or cache_status.status == "down"

    overall = "ok" if all_ok else ("down" if any_down else "degraded")
    result = HealthSchema(status=overall, database=db, cache=cache_status)

    status_code = 200 if overall == "ok" else 503
    return status_code, result
