"""AssignmentInstance / AssignmentResult and the builder that fills them (Person 2).

Model in one paragraph
----------------------
Each vessel makes at most ONE voyage (one passage) in the planning window.
A shipment is carried by one (vessel, passage) whose route matches the shipment's route.
Shipments on the same voyage share it, so their total weight must fit the vessel.
A shipment is only allowed on a voyage that arrives before its deadline.
Cost = for every voyage used: hour_rate * hours + WAVE_PENALTY_PER_M * mean_wave_m
       plus for every shipment: tonne_rate * weight_t   (tonne_rate belongs to its vessel).
"""
import json, pathlib, datetime as dt
from dataclasses import dataclass, field, asdict
import pandas as pd

from voyage import evaluate_voyage, CACHE

HERE = pathlib.Path(__file__).parent
WAVE_PENALTY_PER_M = 20.0      # cost units per metre of mean wave height (assumption)

def key(vessel_id, passage_id):
    return f"{vessel_id}|{passage_id}"

def split_key(k):
    v, p = k.split("|")
    return v, p

@dataclass
class AssignmentInstance:
    scenario_id: str
    transport_mode: str
    shipment_ids: list
    shipments: dict                 # id -> {route_id, weight_t, deadline_utc}
    vessels: dict                   # id -> {capacity_t, speed_kn, hour_rate, tonne_rate}
    voyages: dict                   # "V1|R1-A" -> {route_id, hours, arrival_utc, mean_wave_m, voyage_cost, ...}
    candidate_costs: dict           # "S1|V1|R1-A" -> cost if S1 sailed alone on that voyage
    feasible_options: dict          # "S1" -> ["V1|R1-A", ...]
    rejected_options: dict          # "S1" -> {"V1|R1-B": "arrives after deadline", ...}
    capacity_constraints: dict      # vessel id -> capacity_t
    deadline_constraints: dict      # shipment id -> deadline (UTC ISO)
    units: dict
    assumptions: list
    source_snapshot_id: str
    warnings: list = field(default_factory=list)

    def to_json(self, path):
        pathlib.Path(path).write_text(json.dumps(asdict(self), indent=2, default=str))

@dataclass
class AssignmentResult:
    selected_options: dict          # shipment id -> {"vessel": ..., "passage": ...}
    feasible: bool
    objective_value: float | None
    objective_breakdown: dict
    solver_name: str
    runtime_seconds: float
    warnings: list
    provenance: dict

    def to_json(self, path):
        pathlib.Path(path).write_text(json.dumps(asdict(self), indent=2, default=str))

def _iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")

def _forecast_info():
    """Return (latest forecast start, snapshot id, warnings) from the cache, or (None, 'none', [])."""
    files = sorted(pathlib.Path(CACHE).glob("marine_*.json")) if pathlib.Path(CACHE).exists() else []
    if not files:
        return None, "none", []
    starts, fetched = [], []
    for f in files:
        s = json.loads(f.read_text())
        starts.append(dt.datetime.fromisoformat(s["response"]["hourly"]["time"][0]).replace(tzinfo=dt.timezone.utc))
        fetched.append(s["fetched_at_utc"])
    warns = []
    if len(set(starts)) > 1:
        warns.append("cache files have different forecast start times; using the latest start")
    return max(starts), f"open-meteo-marine fetched {min(fetched)[:16]}Z ({len(files)} points)", warns

def build_instance(use_weather=True, data_dir=None):
    data_dir = pathlib.Path(data_dir) if data_dir else HERE / "data"
    pas = pd.read_csv(data_dir / "maritime_passages.csv")
    ship = pd.read_csv(data_dir / "shipments.csv")
    ves = pd.read_csv(data_dir / "vessels.csv")
    warnings, assumptions = [], []

    dep = [dt.datetime.fromisoformat(x) for x in ship["earliest_departure_utc"]]
    ddl = [dt.datetime.fromisoformat(x) for x in ship["deadline_utc"]]
    plan_start = max(dep)
    if len(set(dep)) > 1:
        warnings.append("shipments have different earliest departures; all voyages start at the latest one")

    snapshot = "none (no forecast used)"
    if use_weather:
        fstart, snapshot, w = _forecast_info()
        warnings += w
        if fstart is None:
            raise RuntimeError("No forecast in cache/. Run `python fetch_all.py` first, or use --no-weather.")
        shift = fstart - min(dep)
        if shift != dt.timedelta(0):
            dep = [d + shift for d in dep]
            ddl = [d + shift for d in ddl]
            plan_start = max(dep)
            assumptions.append(f"synthetic shipment times shifted by {shift} so the scenario starts at the forecast start")

    assumptions += [
        "all vessels are available at the origin port at the plan start",
        "each vessel makes at most one voyage; shipments on the same voyage share it",
        "constant through-water speed per vessel; current effect = along-track component only",
        f"wave penalty {WAVE_PENALTY_PER_M} cost units per metre of mean wave height",
        "passages are illustrative candidate paths, not navigation routes",
        "vessels, shipments and cost rates are synthetic",
    ]

    vessels = {r.vessel_id: {"capacity_t": float(r.capacity_t), "speed_kn": float(r.speed_kn),
                             "hour_rate": float(r.hour_rate), "tonne_rate": float(r.tonne_rate)}
               for r in ves.itertuples()}
    shipments = {r.shipment_id: {"route_id": r.route_id, "weight_t": float(r.weight_t),
                                 "deadline_utc": _iso(d)}
                 for r, d in zip(ship.itertuples(), ddl)}

    voyages = {}
    for vid, v in vessels.items():
        for pid, g in pas.groupby("passage_id"):
            r = evaluate_voyage(g, plan_start, v["speed_kn"], use_weather=use_weather)
            cost = None
            if r["mean_wave_m"] is not None:
                cost = v["hour_rate"] * r["hours"] + WAVE_PENALTY_PER_M * r["mean_wave_m"]
            voyages[key(vid, pid)] = {
                "vessel_id": vid, "passage_id": pid, "route_id": g["route_id"].iloc[0],
                "hours": r["hours"], "arrival_utc": _iso(r["arrival"]), "dist_nmi": r["dist_nmi"],
                "mean_wave_m": r["mean_wave_m"], "max_wave_m": r["max_wave_m"],
                "voyage_cost": cost, "warnings": r["warnings"]}

    feasible, rejected, cand = {}, {}, {}
    for sid, s in shipments.items():
        feasible[sid], rejected[sid] = [], {}
        for k, vy in voyages.items():
            if vy["route_id"] != s["route_id"]:
                continue
            vessel = vessels[vy["vessel_id"]]
            if s["weight_t"] > vessel["capacity_t"]:
                rejected[sid][k] = "over vessel capacity"
            elif vy["voyage_cost"] is None:
                rejected[sid][k] = "no wave data"
            elif vy["arrival_utc"] > s["deadline_utc"]:
                rejected[sid][k] = "arrives after deadline"
            else:
                feasible[sid].append(k)
                cand[f"{sid}|{k}"] = vy["voyage_cost"] + vessel["tonne_rate"] * s["weight_t"]

    return AssignmentInstance(
        scenario_id="maritime-demo", transport_mode="maritime",
        shipment_ids=list(shipments), shipments=shipments, vessels=vessels, voyages=voyages,
        candidate_costs=cand, feasible_options=feasible, rejected_options=rejected,
        capacity_constraints={v: x["capacity_t"] for v, x in vessels.items()},
        deadline_constraints={s: x["deadline_utc"] for s, x in shipments.items()},
        units={"time": "UTC", "distance": "nmi", "speed": "kn", "weight": "t",
               "wave_height": "m", "cost": "abstract cost units"},
        assumptions=assumptions, source_snapshot_id=snapshot, warnings=warnings)
