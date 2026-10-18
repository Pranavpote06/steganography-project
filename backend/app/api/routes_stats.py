from fastapi import APIRouter
from ..services.stats_service import stats_tracker

router = APIRouter()

@router.get("/stats")
def get_session_stats():
    """Returns actual real session metrics and recent operations."""
    return stats_tracker.get_stats()

@router.post("/stats/reset")
def reset_session_stats():
    """Resets session metrics and operation history."""
    stats_tracker.reset_stats()
    return {"message": "Session statistics successfully reset."}
