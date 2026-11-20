from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.optimization import OptimizationRun
from backend.app.models.scenario import Scenario
from backend.app.schemas.optimization import (
    OptimizationRequest,
    OptimizationRunResponse,
)


router = APIRouter(
    prefix="/optimization",
    tags=["Optimization"]
)


@router.post(
    "/runs",
    response_model=OptimizationRunResponse,
    status_code=status.HTTP_201_CREATED
)
def create_optimization_run(
    request: OptimizationRequest,
    db: Session = Depends(get_db)
):
    scenario = db.get(Scenario, request.scenario_id)

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    run = OptimizationRun(
        scenario_id=request.scenario_id,
        solver=request.solver,
        status="pending",
        request_data=request.model_dump()
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run


@router.get(
    "/runs/{run_id}",
    response_model=OptimizationRunResponse
)
def get_optimization_run(
    run_id: str,
    db: Session = Depends(get_db)
):
    run = db.get(OptimizationRun, run_id)

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization run not found"
        )
    return run

@router.get(
    "/scenarios/{scenario_id}/runs",
    response_model=list[OptimizationRunResponse]
)
def get_scenario_optimization_runs(
    scenario_id: str,
    db: Session = Depends(get_db)
):
    scenario = db.get(Scenario, scenario_id)

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found"
        )

    runs = (
        db.query(OptimizationRun)
        .filter(OptimizationRun.scenario_id == scenario_id)
        .order_by(OptimizationRun.created_at.desc())
        .all()
    )

    return runs