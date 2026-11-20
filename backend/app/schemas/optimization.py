from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field



class CandidateOption(BaseModel):
    shipment_id: str
    vessel_id: str
    route_id: str
    passage_id: str

    distance_km: float = Field(ge=0)
    estimated_travel_hours: float = Field(ge=0)
    estimated_arrival_utc: datetime

    cost: float = Field(ge=0)


class CapacityConstraint(BaseModel):
    route_id: str
    vessel_id: str
    shipment_ids: list[str]

    total_weight_t: float = Field(ge=0)
    capacity_t: float = Field(gt=0)


class DeadlineConstraint(BaseModel):
    shipment_id: str
    vessel_id: str
    route_id: str
    passage_id: str
    deadline_utc: datetime
    estimated_arrival_utc: datetime
    satisfied: bool


class AssignmentInstance(BaseModel):
    scenario_id: str
    transport_mode: Literal["maritime"]

    shipment_ids: list[str]
    candidate_costs: list[CandidateOption]

    capacity_constraints: list[CapacityConstraint]
    deadline_constraints: list[DeadlineConstraint]

    units: dict[str, str]
    assumptions: list[str]
    source_snapshot_id: str


class SelectedOption(BaseModel):
    shipment_id: str
    vessel_id: str
    route_id: str
    passage_id: str
    cost: float


class AssignmentResult(BaseModel):
    selected_options: list[SelectedOption]

    feasible: bool
    objective_value: float | None = None
    objective_breakdown: dict[str, Any] = Field(default_factory=dict)

    solver_name: str
    runtime_seconds: float = Field(ge=0)

    warnings: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


class QuantumResult(AssignmentResult):
    logical_qubits: int = Field(ge=0)
    qaoa_depth: int = Field(ge=0)
    shots: int = Field(gt=0)
    seed: int

    feasible_sample_rate: float = Field(ge=0, le=1)
    exact_reference_cost: float | None = None
    candidate_accepted: bool


class OptimizationRequest(BaseModel):
    scenario_id: str = Field(min_length=1)
    solver: Literal["classical", "quantum", "both"] = "both"
    seed: int = 42
    shots: int = Field(default=1024, gt=0)

class OptimizationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scenario_id: str
    solver: str
    status: str
    request_data: dict
    result_data: dict | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None