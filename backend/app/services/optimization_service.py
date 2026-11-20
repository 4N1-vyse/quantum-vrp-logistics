from backend.app.models.scenario import Scenario
from backend.app.models.shipment import Shipment
from backend.app.models.vessel import Vessel
from backend.app.models.route import Route
from backend.app.models.passage import Passage
from backend.app.models.waypoint import Waypoint

from sqlalchemy.orm import Session

from backend.app.schemas.optimization import (
    AssignmentInstance,
    CandidateOption,
    CapacityConstraint,
    DeadlineConstraint,
)

from backend.app.utils.geo import (
    calculate_passage_distance_km,
    calculate_travel_hours,
    calculate_estimated_arrival_utc,
)

def get_scenario(db: Session, scenario_id: str) -> Scenario:
    """
    Retrieve a scenario from the database.
    """

    scenario = db.get(Scenario, scenario_id)

    if scenario is None:
        raise ValueError("Scenario not found")

    if scenario.transport_mode != "maritime":
        raise ValueError("Only maritime scenarios are supported")

    return scenario

def get_scenario_shipments(
    db: Session,
    scenario: Scenario
) -> list[Shipment]:
    """
    Retrieve all shipments belonging to the scenario's route.
    """

    shipments = (
        db.query(Shipment)
        .filter(
            Shipment.route_id == scenario.route_id,
            Shipment.transport_mode == scenario.transport_mode
        )
        .order_by(Shipment.shipment_id)
        .all()
    )

    if not shipments:
        raise ValueError("No shipments found for this scenario")

    return shipments

def get_scenario_route(
    db: Session,
    scenario: Scenario
) -> Route:
    """
    Retrieve the route associated with a scenario.
    """

    route = db.get(Route, scenario.route_id)

    if route is None:
        raise ValueError("Route not found for this scenario")

    return route

def get_route_passages(
    db: Session,
    route: Route
) -> list[Passage]:
    """
    Retrieve all passages belonging to a route.
    """

    passages = (
        db.query(Passage)
        .filter(Passage.route_id == route.route_id)
        .order_by(Passage.passage_id)
        .all()
    )

    if not passages:
        raise ValueError("No passages found for this route")

    return passages

def get_passage_waypoints(
    db: Session,
    passage: Passage
) -> list[Waypoint]:
    """
    Retrieve waypoints for a passage in sequence order.
    """

    waypoints = (
        db.query(Waypoint)
        .filter(Waypoint.passage_id == passage.passage_id)
        .order_by(Waypoint.seq)
        .all()
    )

    if len(waypoints) < 2:
        raise ValueError(
            f"Passage {passage.passage_id} must have at least two waypoints"
        )

    return waypoints

def get_available_vessels(db: Session) -> list[Vessel]:
    """
    Retrieve all vessels available for optimization.
    """

    vessels = (
        db.query(Vessel)
        .order_by(Vessel.vessel_id)
        .all()
    )

    if not vessels:
        raise ValueError("No vessels found in the database")

    return vessels

def generate_candidate_options(
    shipments: list[Shipment],
    vessels: list[Vessel],
    passages: list[Passage],
    db: Session,
) -> list[CandidateOption]:
    """
    Generate all valid shipment-vessel-passage combinations.
    """

    candidates = []

    for shipment in shipments:
        for vessel in vessels:
            for passage in passages:

                waypoints = get_passage_waypoints(db, passage)

                distance_km = calculate_passage_distance_km(waypoints)

                travel_hours = calculate_travel_hours(
                    distance_km,
                    vessel.speed_kn
                )

                arrival_utc = calculate_estimated_arrival_utc(
                    shipment.earliest_departure_utc,
                    travel_hours
                )

                cost = shipment.weight_t * distance_km

                candidate = CandidateOption(
                    shipment_id=shipment.shipment_id,
                    vessel_id=vessel.vessel_id,
                    route_id=shipment.route_id,
                    passage_id=passage.passage_id,
                    distance_km=distance_km,
                    estimated_travel_hours=travel_hours,
                    estimated_arrival_utc=arrival_utc,
                    cost=cost,
                )

                candidates.append(candidate)

    return candidates

def generate_capacity_constraints(
    shipments: list[Shipment],
    vessels: list[Vessel],
    route: Route,
) -> list[CapacityConstraint]:
    """
    Generate vessel capacity constraints for a route.
    """

    constraints = []

    total_weight = sum(shipment.weight_t for shipment in shipments)

    for vessel in vessels:
        constraint = CapacityConstraint(
            route_id=route.route_id,
            vessel_id=vessel.vessel_id,
            shipment_ids=[
                shipment.shipment_id for shipment in shipments
            ],
            total_weight_t=total_weight,
            capacity_t=vessel.capacity_t,
        )

        constraints.append(constraint)

    return constraints

def generate_deadline_constraints(
    shipments: list[Shipment],
    candidates: list[CandidateOption],
) -> list[DeadlineConstraint]:
    """
    Generate deadline constraints for every candidate assignment.
    """

    shipment_lookup = {
        shipment.shipment_id: shipment
        for shipment in shipments
    }

    constraints = []

    for candidate in candidates:
        shipment = shipment_lookup[candidate.shipment_id]

        constraint = DeadlineConstraint(
            shipment_id=candidate.shipment_id,
            vessel_id=candidate.vessel_id,
            route_id=candidate.route_id,
            passage_id=candidate.passage_id,
            deadline_utc=shipment.deadline_utc,
            estimated_arrival_utc=candidate.estimated_arrival_utc,
            satisfied=(
                candidate.estimated_arrival_utc
                <= shipment.deadline_utc
            ),
        )

        constraints.append(constraint)

    return constraints

from uuid import uuid4

def build_assignment_instance(
    db: Session,
    scenario_id: str,
) -> AssignmentInstance:
    """
    Build the complete optimization input for a scenario.
    """

    scenario = get_scenario(db, scenario_id)
    shipments = get_scenario_shipments(db, scenario)
    route = get_scenario_route(db, scenario)
    passages = get_route_passages(db, route)
    vessels = get_available_vessels(db)

    candidates = generate_candidate_options(
        shipments, vessels, passages, db
    )

    capacity_constraints = generate_capacity_constraints(
        shipments, vessels, route
    )

    deadline_constraints = generate_deadline_constraints(
        shipments, candidates
    )

    return AssignmentInstance(
        scenario_id=scenario.id,
        transport_mode="maritime",
        shipment_ids=[
            shipment.shipment_id for shipment in shipments
        ],
        candidate_costs=candidates,
        capacity_constraints=capacity_constraints,
        deadline_constraints=deadline_constraints,
        units={
            "distance": "km",
            "weight": "tonnes",
            "time": "UTC hours",
            "cost": "cost units",
            "speed": "knots",
        },
        assumptions=[
            "Only maritime transportation is supported.",
            "Each shipment must be assigned to exactly one candidate passage.",
            "All registered vessels are considered available.",
            "Vessel capacity applies to the selected shipment load.",
            "Estimated travel time assumes constant vessel speed.",
            "Cost equals shipment weight multiplied by passage distance.",
            "Cost is a proxy and does not represent actual monetary charges.",
        ],
        source_snapshot_id=str(uuid4()),
    )