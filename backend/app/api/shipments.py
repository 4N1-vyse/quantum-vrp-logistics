from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.shipment import Shipment
from backend.app.schemas.shipment import (
    ShipmentCreate,
    ShipmentResponse,
)

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.post(
    "",
    response_model=ShipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db),
):
    new_shipment = Shipment(
        shipment_id=shipment.shipment_id,
        transport_mode=shipment.transport_mode,
        route_id=shipment.route_id,
        weight_t=shipment.weight_t,
        earliest_departure_utc=shipment.earliest_departure_utc,
        deadline_utc=shipment.deadline_utc,
        is_synthetic=shipment.is_synthetic,
    )

    db.add(new_shipment)

    try:
        db.commit()
        db.refresh(new_shipment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shipment with this ID already exists",
        )

    return new_shipment


@router.get(
    "",
    response_model=list[ShipmentResponse],
)
def get_shipments(db: Session = Depends(get_db)):
    return db.query(Shipment).all()


@router.get(
    "/{shipment_id}",
    response_model=ShipmentResponse,
)
def get_shipment(
    shipment_id: str,
    db: Session = Depends(get_db),
):
    shipment = db.query(Shipment).filter(
        Shipment.shipment_id == shipment_id
    ).first()

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found",
        )

    return shipment

