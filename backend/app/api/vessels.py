from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import Vessel
from backend.app.schemas.vessel import VesselResponse


router = APIRouter(
    prefix="/vessels",
    tags=["Vessels"]
)


@router.get("", response_model=list[VesselResponse])
def get_vessels(db: Session = Depends(get_db)):
    return (
        db.query(Vessel)
        .order_by(Vessel.vessel_id)
        .all()
    )
