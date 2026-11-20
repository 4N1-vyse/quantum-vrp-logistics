from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import Passage, Waypoint
from backend.app.schemas.passage import PassageResponse
from backend.app.schemas.waypoint import WaypointResponse


router = APIRouter(
    prefix="/passages",
    tags=["Passages"]
)


@router.get("", response_model=list[PassageResponse])
def get_passages(db: Session = Depends(get_db)):
    return (
        db.query(Passage)
        .order_by(Passage.passage_id)
        .all()
    )


@router.get(
    "/{passage_id}/waypoints",
    response_model=list[WaypointResponse]
)
def get_passage_waypoints(
    passage_id: str,
    db: Session = Depends(get_db)
):
    passage = db.get(Passage, passage_id)

    if passage is None:
        raise HTTPException(
            status_code=404,
            detail="Passage not found"
        )

    return (
        db.query(Waypoint)
        .filter(Waypoint.passage_id == passage_id)
        .order_by(Waypoint.seq)
        .all()
    )
