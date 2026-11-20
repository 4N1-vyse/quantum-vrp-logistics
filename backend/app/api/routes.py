from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import Route
from backend.app.schemas.route import RouteResponse


router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)


@router.get("", response_model=list[RouteResponse])
def get_routes(db: Session = Depends(get_db)):
    return (
        db.query(Route)
        .order_by(Route.route_id)
        .all()
    )
