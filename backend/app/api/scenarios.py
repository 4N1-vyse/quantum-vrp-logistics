from uuid import uuid4

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.scenario import Scenario
from backend.app.schemas.scenario import (
    ScenarioCreate,
    ScenarioResponse,
)

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.post(
    "",
    response_model=ScenarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_scenario(
    scenario: ScenarioCreate,
    db: Session = Depends(get_db),
):
    new_scenario = Scenario(
        id=str(uuid4()),
        name=scenario.name,
        transport_mode=scenario.transport_mode,
        route_id=scenario.route_id,
    )

    db.add(new_scenario)
    db.commit()
    db.refresh(new_scenario)

    return new_scenario


@router.get(
    "",
    response_model=list[ScenarioResponse],
)
def get_scenarios(db: Session = Depends(get_db)):
    return db.query(Scenario).all()
