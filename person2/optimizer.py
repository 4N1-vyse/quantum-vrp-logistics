"""Classical optimizers for the maritime assignment problem (Person 2).

solve_cpsat : OR-Tools CP-SAT (exact, proves optimality)
solve_exact : plain Python enumeration (exact, slow, used to double-check CP-SAT)
Both take an AssignmentInstance and return an AssignmentResult.
"""
import time
from ortools.sat.python import cp_model
from instance import AssignmentInstance, AssignmentResult, split_key

COST_SCALE = 100      # CP-SAT needs integers: costs x100
WEIGHT_SCALE = 10     # weights x10

def _no_option_warnings(inst):
    out = []
    for s in inst.shipment_ids:
        if not inst.feasible_options[s]:
            reasons = sorted(set(inst.rejected_options[s].values())) or ["no vessel/passage on this route"]
            out.append(f"{s}: no feasible vessel/passage ({'; '.join(reasons)})")
    return out

def _infeasible(inst, name, t0, warnings, extra=None):
    prov = {"snapshot": inst.source_snapshot_id, "scenario": inst.scenario_id}
    prov.update(extra or {})
    return AssignmentResult({}, False, None, {}, name, time.perf_counter() - t0,
                            list(inst.warnings) + warnings, prov)

def _make_result(inst, assign, name, t0, warnings, extra=None):
    """assign: shipment id -> option key 'V|P'. Builds the breakdown from the instance."""
    by_voyage = {}
    for s, k in assign.items():
        by_voyage.setdefault(k, []).append(s)
    voyage_total = tonne_total = 0.0
    voyages = []
    for k, sids in sorted(by_voyage.items()):
        v, p = split_key(k)
        vy, ves = inst.voyages[k], inst.vessels[v]
        load = sum(inst.shipments[s]["weight_t"] for s in sids)
        tonne = sum(ves["tonne_rate"] * inst.shipments[s]["weight_t"] for s in sids)
        voyage_total += vy["voyage_cost"]
        tonne_total += tonne
        voyages.append({"vessel": v, "passage": p, "route": vy["route_id"], "shipments": sorted(sids),
                        "load_t": load, "capacity_t": ves["capacity_t"], "hours": round(vy["hours"], 2),
                        "arrival_utc": vy["arrival_utc"], "mean_wave_m": vy["mean_wave_m"],
                        "voyage_cost": round(vy["voyage_cost"], 2), "per_tonne_cost": round(tonne, 2)})
    selected = {s: {"vessel": split_key(k)[0], "passage": split_key(k)[1]} for s, k in assign.items()}
    prov = {"snapshot": inst.source_snapshot_id, "scenario": inst.scenario_id}
    prov.update(extra or {})
    return AssignmentResult(selected, True, round(voyage_total + tonne_total, 2),
                            {"voyage_cost": round(voyage_total, 2), "per_tonne_cost": round(tonne_total, 2),
                             "voyages": voyages},
                            name, time.perf_counter() - t0, list(inst.warnings) + warnings, prov)

def solve_cpsat(inst: AssignmentInstance, time_limit_s=20):
    t0 = time.perf_counter()
    bad = _no_option_warnings(inst)
    if bad:
        return _infeasible(inst, "ortools-cpsat", t0, bad)
    m = cp_model.CpModel()
    x = {(s, k): m.NewBoolVar(f"x_{s}_{k}") for s in inst.shipment_ids for k in inst.feasible_options[s]}
    used = sorted({k for _, k in x})
    y = {k: m.NewBoolVar(f"y_{k}") for k in used}
    for s in inst.shipment_ids:
        m.AddExactlyOne(x[s, k] for k in inst.feasible_options[s])
    for (s, k), var in x.items():
        m.AddImplication(var, y[k])
    for k in used:
        v, _ = split_key(k)
        cap = int(round(inst.capacity_constraints[v] * WEIGHT_SCALE))
        m.Add(sum(int(round(inst.shipments[s]["weight_t"] * WEIGHT_SCALE)) * x[s, k]
                  for s in inst.shipment_ids if (s, k) in x) <= cap * y[k])
    for v in inst.vessels:
        m.Add(sum(y[k] for k in used if split_key(k)[0] == v) <= 1)
    obj = sum(int(round(inst.voyages[k]["voyage_cost"] * COST_SCALE)) * y[k] for k in used)
    obj += sum(int(round(inst.vessels[split_key(k)[0]]["tonne_rate"] * inst.shipments[s]["weight_t"] * COST_SCALE)) * var
               for (s, k), var in x.items())
    m.Minimize(obj)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_s
    solver.parameters.num_workers = 1          # reproducible
    solver.parameters.random_seed = 1
    status = solver.Solve(m)
    name = solver.StatusName(status)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        assign = {s: k for (s, k), var in x.items() if solver.Value(var)}
        warns = [] if status == cp_model.OPTIMAL else ["solution found but not proven optimal (time limit)"]
        return _make_result(inst, assign, "ortools-cpsat", t0, warns, {"solver_status": name})
    return _infeasible(inst, "ortools-cpsat", t0,
                       ["no assignment satisfies capacity, deadlines and one-voyage-per-vessel together"],
                       {"solver_status": name})

def solve_exact(inst: AssignmentInstance):
    t0 = time.perf_counter()
    bad = _no_option_warnings(inst)
    if bad:
        return _infeasible(inst, "exact-enumeration", t0, bad)
    ids = sorted(inst.shipment_ids, key=lambda s: len(inst.feasible_options[s]))
    best = {"cost": None, "assign": None}

    def leaf_cost(assign):
        used = set(assign.values())
        c = sum(inst.voyages[k]["voyage_cost"] for k in used)
        c += sum(inst.vessels[split_key(k)[0]]["tonne_rate"] * inst.shipments[s]["weight_t"]
                 for s, k in assign.items())
        return c

    def rec(i, assign, vessel_voyage, load):
        if i == len(ids):
            c = leaf_cost(assign)
            if best["cost"] is None or c < best["cost"] - 1e-9:
                best["cost"], best["assign"] = c, dict(assign)
            return
        s = ids[i]
        w = inst.shipments[s]["weight_t"]
        for k in inst.feasible_options[s]:
            v, _ = split_key(k)
            if vessel_voyage.get(v, k) != k:
                continue                       # vessel already sails a different voyage
            if load.get(k, 0.0) + w > inst.capacity_constraints[v] + 1e-9:
                continue
            assign[s] = k
            added = v not in vessel_voyage
            if added:
                vessel_voyage[v] = k
            load[k] = load.get(k, 0.0) + w
            rec(i + 1, assign, vessel_voyage, load)
            load[k] -= w
            if added:
                del vessel_voyage[v]
            del assign[s]

    rec(0, {}, {}, {})
    if best["assign"] is None:
        return _infeasible(inst, "exact-enumeration", t0,
                           ["no assignment satisfies capacity, deadlines and one-voyage-per-vessel together"])
    return _make_result(inst, best["assign"], "exact-enumeration", t0, [])
