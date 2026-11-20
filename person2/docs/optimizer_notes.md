# Classical optimizer: notes for the viva

## Problem
Assign every shipment to one vessel and one passage so that total cost is minimal, vessel capacity is respected and every shipment arrives by its deadline.

## Decisions (what the solver chooses)
- y[vessel, passage] = 1 if the vessel sails that passage (at most one per vessel).
- x[shipment, vessel, passage] = 1 if the shipment travels on that voyage (exactly one per shipment).

## Constraints
- x <= y (a shipment can only use a voyage that sails).
- Sum of weights on a voyage <= vessel capacity.
- Only (vessel, passage) options on the shipment's own route that arrive before its deadline exist at all.

## Objective
Sum over used voyages of (hour_rate x hours + 20 x mean wave m) + sum over shipments of (tonne_rate x weight).
Sharing a voyage saves the voyage cost, so the solver trades consolidation against capacity and deadlines.

## Method
OR-Tools CP-SAT (exact: it proves the optimum). Costs are scaled x100 and weights x10 to integers. Cross-checked against a plain Python enumeration; the tests compare both on 40 random instances.

## Honest limits
- Synthetic vessels, shipments and cost rates.
- Passages are constructed illustrative paths.
- Forecast is a saved snapshot, not live.
- With 6 shipments the problem is small; the classical solver finds the exact optimum instantly. Nothing here claims quantum advantage.

## Interface
AssignmentInstance in, AssignmentResult out (see instance.py). Infeasible instances return feasible=False with warnings, they do not crash.
