# RouteQ Prototype Transportation Cost Model

## 1. Purpose

This document defines a common transportation cost model for the classical and quantum optimization modules of RouteQ.

Both optimization engines must use the same formula, input values, and assumptions to ensure a fair comparison.

## 2. Cost Formula

The prototype uses a distance-weight cost proxy:

\[
C_{ij}=W_i \times D_j \times R
\]

Where:

- \(C_{ij}\): Cost of assigning shipment \(i\) to passage \(j\).
- \(W_i\): Shipment weight in tonnes.
- \(D_j\): Total passage distance in kilometres.
- \(R\): Prototype cost rate.

For the initial prototype:

\[
R=1 \text{ cost unit per tonne-kilometre}
\]

Therefore:

\[
C_{ij}=W_i \times D_j
\]

## 3. Passage Distance

Passage distance is calculated by summing the Haversine distances between consecutive waypoints.

Waypoints must be ordered by their sequence number (`seq`).

## 4. Optimization Objective

The objective is to minimize the total cost of selected shipment assignments:

\[
\min C_{\text{total}}=\sum_{i,j}x_{ij}C_{ij}
\]

Where:

- \(x_{ij}\) is a binary decision variable.
- \(x_{ij}=1\) if shipment \(i\) is assigned to candidate passage \(j\).
- \(x_{ij}=0\) otherwise.

## 5. Constraints

The optimization must also consider:

1. Each shipment must receive an assignment.
2. Total assigned shipment weight must not exceed vessel capacity.
3. Estimated arrival must satisfy the shipment deadline.
4. Only valid vessel, route, and passage combinations may be selected.

## 6. Assumptions and Limitations

- The cost is a normalized optimization proxy, not a real-world monetary price.
- The prototype uses the same rate for all vessels.
- The model does not currently include fuel prices, port charges, crew costs, or vessel-specific operating expenses.
- Distance is calculated from the supplied synthetic maritime waypoints.
- Travel time is calculated separately using vessel speed.
- Both classical and quantum optimizers must use identical candidate costs and constraints.

## 7. Future Improvements

The cost model can later be extended to include vessel-specific operating rates, fuel consumption, fuel prices, port charges, and other operational expenses.

Any change must be applied consistently to both optimization engines.