# RouteQ - Optimization Integration Contract

## 1. Purpose

This document defines the common interface between the RouteQ backend, classical route optimizer, and quantum optimizer.

All modules must follow this contract to ensure integration compatibility.

## 2. Transport Scope

- Initial prototype supports maritime transportation only.
- All timestamps must use UTC.
- Weight is measured in tonnes.
- Distance is measured in kilometres and nautical miles.
- Speed is measured in knots.
- All input data must identify synthetic assumptions where applicable.

## 3. AssignmentInstance

This is the input structure passed from the backend to an optimizer.

| Field | Type | Description |
|---|---|---|
| scenario_id | string | Unique scenario identifier |
| transport_mode | string | maritime |
| shipment_ids | list[string] | Shipment identifiers |
| candidate_costs | list[object] | Available assignment options and costs |
| capacity_constraints | object | Vessel capacity constraints |
| deadline_constraints | object | Shipment deadline constraints |
| units | object | Units used in calculations |
| assumptions | list[string] | Assumptions used to construct the instance |
| source_snapshot_id | string | Identifier of the input data snapshot |

### Candidate cost structure

Each candidate option must identify:

- shipment_id
- vessel_id
- route_id
- passage_id
- cost

The cost unit and calculation assumptions must be documented.

## 4. AssignmentResult

This is the common output returned by either optimizer.

| Field | Type | Description |
|---|---|---|
| selected_options | list[object] | Selected shipment assignment options |
| feasible | boolean | Whether all required constraints are satisfied |
| objective_value | number or null | Final objective value |
| objective_breakdown | object | Breakdown of objective components |
| solver_name | string | Name of the solver |
| runtime_seconds | number | Solver execution time |
| warnings | list[string] | Warnings or limitations |
| provenance | object | Input and solver information |

Each selected option must identify:

- shipment_id
- vessel_id
- route_id
- passage_id
- cost

## 5. QuantumResult

The quantum optimizer must return the common AssignmentResult fields along with:

| Field | Type | Description |
|---|---|---|
| logical_qubits | integer | Number of logical qubits used |
| qaoa_depth | integer | QAOA circuit depth |
| shots | integer | Number of measurement shots |
| seed | integer | Random seed used |
| feasible_sample_rate | number | Fraction of feasible samples |
| exact_reference_cost | number or null | Classical exact reference objective |
| candidate_accepted | boolean | Whether the quantum candidate passed acceptance checks |

## 6. Solver Interface

Both optimizers must expose a callable function:

`solve(instance: AssignmentInstance) -> AssignmentResult`

The quantum optimizer must expose equivalent functionality and return its additional quantum metrics.

The backend must not depend on internal implementation details of either optimizer.

## 7. Constraint Expectations

The optimizers must account for:

1. Vessel capacity.
2. Shipment deadlines.
3. Valid route and passage assignments.
4. Assignment consistency.
5. Feasibility of the final selected options.

An infeasible result must not be reported as a successful optimization.

## 8. Prototype Limitations

- Use the supplied project datasets and documented assumptions.
- Do not claim live vessel tracking or live shipping schedules.
- Do not claim quantum speedup.
- Compare quantum results against a classical exact reference on the same small test instance.
- Report runtime and feasibility honestly.

## 9. Integration Responsibilities

- Backend: request validation, data preparation, API endpoints, persistence and orchestration.
- Classical optimizer: candidate generation, cost evaluation and classical optimization.
- Quantum optimizer: QUBO formulation, QAOA simulation and result evaluation.

Any proposed changes to this contract must be communicated to all three contributors before implementation.