import random
import pytest
from instance import AssignmentInstance, build_instance, key
from optimizer import solve_cpsat, solve_exact

def make_inst(vessels, shipments, voyages, deadline_ok=None):
    """vessels: id->(cap, tonne_rate); shipments: id->(route, weight);
    voyages: (vessel, passage, route)->cost. deadline_ok: set of (shipment, vessel, passage) allowed (None = all)."""
    V = {v: {"capacity_t": c, "speed_kn": 16.0, "hour_rate": 0.0, "tonne_rate": r} for v, (c, r) in vessels.items()}
    S = {s: {"route_id": r, "weight_t": w, "deadline_utc": "x"} for s, (r, w) in shipments.items()}
    VY = {key(v, p): {"vessel_id": v, "passage_id": p, "route_id": r, "hours": 1.0, "arrival_utc": "x",
                      "mean_wave_m": 0.0, "voyage_cost": c, "dist_nmi": 1.0, "max_wave_m": 0.0, "warnings": []}
          for (v, p, r), c in voyages.items()}
    feas, rej, cand = {}, {}, {}
    for s, sd in S.items():
        feas[s], rej[s] = [], {}
        for k, vy in VY.items():
            if vy["route_id"] != sd["route_id"]:
                continue
            v = vy["vessel_id"]
            if sd["weight_t"] > V[v]["capacity_t"]:
                rej[s][k] = "over vessel capacity"
            elif deadline_ok is not None and (s, v, vy["passage_id"]) not in deadline_ok:
                rej[s][k] = "arrives after deadline"
            else:
                feas[s].append(k)
                cand[f"{s}|{k}"] = vy["voyage_cost"] + V[v]["tonne_rate"] * sd["weight_t"]
    return AssignmentInstance("test", "maritime", list(S), S, V, VY, cand, feas, rej,
                              {v: x["capacity_t"] for v, x in V.items()},
                              {s: "x" for s in S}, {}, [], "test")

def test_consolidation_example():
    # S1 180t + S2 95t on route R1. Both on V2 costs 140 + 0.4*275 = 250 (the optimum).
    inst = make_inst({"V1": (200, 0.5), "V2": (300, 0.4)},
                     {"S1": ("R1", 180), "S2": ("R1", 95)},
                     {("V1", "R1-A", "R1"): 100, ("V2", "R1-A", "R1"): 140})
    for solve in (solve_cpsat, solve_exact):
        r = solve(inst)
        assert r.feasible and abs(r.objective_value - 250) < 0.01
        assert r.selected_options["S1"]["vessel"] == r.selected_options["S2"]["vessel"] == "V2"

def test_over_capacity_gives_infeasible_not_crash():
    inst = make_inst({"V1": (200, 0.5)}, {"S1": ("R1", 500)}, {("V1", "R1-A", "R1"): 100})
    for solve in (solve_cpsat, solve_exact):
        r = solve(inst)
        assert r.feasible is False and r.objective_value is None
        assert any("S1" in w and "capacity" in w for w in r.warnings)

def test_deadline_makes_it_infeasible():
    inst = make_inst({"V1": (200, 0.5)}, {"S1": ("R1", 50)}, {("V1", "R1-A", "R1"): 100}, deadline_ok=set())
    r = solve_cpsat(inst)
    assert r.feasible is False and any("deadline" in w for w in r.warnings)

def test_one_voyage_per_vessel_can_make_it_infeasible():
    # two shipments on different routes but only one vessel -> cannot serve both
    inst = make_inst({"V1": (200, 0.5)}, {"S1": ("R1", 10), "S2": ("R2", 10)},
                     {("V1", "R1-A", "R1"): 10, ("V1", "R2-A", "R2"): 10})
    for solve in (solve_cpsat, solve_exact):
        r = solve(inst)
        assert r.feasible is False and r.warnings

def test_cpsat_matches_exact_on_random_instances():
    rng = random.Random(7)
    for _ in range(40):
        vessels = {f"V{i}": (rng.choice([60, 100, 150, 250]), rng.choice([0.4, 0.5, 0.6])) for i in range(3)}
        shipments = {f"S{i}": (rng.choice(["R1", "R2"]), rng.choice([20, 40, 70, 90])) for i in range(4)}
        voyages = {(v, p, r): rng.randint(50, 300) for v in vessels for p, r in (("R1-A", "R1"), ("R1-B", "R1"), ("R2-A", "R2"))}
        inst = make_inst(vessels, shipments, voyages)
        a, b = solve_cpsat(inst), solve_exact(inst)
        assert a.feasible == b.feasible
        if a.feasible:
            assert abs(a.objective_value - b.objective_value) < 0.02

def test_real_data_no_weather_solves_and_matches():
    inst = build_instance(use_weather=False)
    assert len(inst.shipment_ids) == 6
    a, b = solve_cpsat(inst), solve_exact(inst)
    assert a.feasible and b.feasible and abs(a.objective_value - b.objective_value) < 0.02
    # every shipment gets exactly one vessel and passage on its own route
    for s in inst.shipment_ids:
        sel = a.selected_options[s]
        assert inst.voyages[f"{sel['vessel']}|{sel['passage']}"]["route_id"] == inst.shipments[s]["route_id"]
    # capacity respected on every voyage
    for v in a.objective_breakdown["voyages"]:
        assert v["load_t"] <= v["capacity_t"]
    # every shipment arrives by its deadline
    for s in inst.shipment_ids:
        sel = a.selected_options[s]
        assert inst.voyages[f"{sel['vessel']}|{sel['passage']}"]["arrival_utc"] <= inst.shipments[s]["deadline_utc"]

def test_weather_mode_without_cache_raises_clear_error(tmp_path, monkeypatch):
    import instance
    monkeypatch.setattr(instance, "CACHE", tmp_path / "nothing_here")
    with pytest.raises(RuntimeError, match="fetch_all"):
        build_instance(use_weather=True)
