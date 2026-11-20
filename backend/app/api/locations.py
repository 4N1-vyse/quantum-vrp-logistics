from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import Location
from backend.app.schemas.location import LocationResponse


router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


@router.get("", response_model=list[LocationResponse])
def get_locations(db: Session = Depends(get_db)):
    return (
        db.query(Location)
        .order_by(Location.location_id)
        .all()
    )
