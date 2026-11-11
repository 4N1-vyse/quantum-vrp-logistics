from uuid import uuid4

from fastapi import APIRouter, status

from backend.app.schemas.scenario import (
    ScenarioCreate,
    ScenarioResponse,
)

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])

# Temporary in-memory storage
#This is temporary storage. Scenarios will disappear when the server restarts. We'll replace it with PostgreSQL later
scenarios = [] 

@router.post(
    "",
    response_model=ScenarioResponse,
    status_code=status.HTTP_201_CREATED
)
def create_scenario(scenario: ScenarioCreate):
    new_scenario = ScenarioResponse(
        id=str(uuid4()),
        name=scenario.name,
        transport_mode=scenario.transport_mode,
        route_id=scenario.route_id
    )

    scenarios.append(new_scenario)

    return new_scenario

@router.get("", response_model=list[ScenarioResponse])
def get_scenarios():
    return scenarios

