"""Build the AssignmentInstance, solve it two ways, compare, save results (Person 2).

python run_optimizer.py                 # uses the cached forecast (run fetch_all.py first)
python run_optimizer.py --no-weather    # no forecast: waves and currents ignored (clearly flagged)
"""
import argparse, pathlib, sys
import pandas as pd
from instance import build_instance
from optimizer import solve_cpsat, solve_exact

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-weather", action="store_true")
    args = ap.parse_args()
    try:
        inst = build_instance(use_weather=not args.no_weather)
    except RuntimeError as e:
        print("ERROR:", e)
        sys.exit(1)

    out = pathlib.Path("output")
    out.mkdir(exist_ok=True)
    inst.to_json(out / "assignment_instance.json")

    print(f"Scenario: {inst.scenario_id} | forecast: {inst.source_snapshot_id}")
    for w in inst.warnings:
        print("WARNING:", w)
    print("\nOptions kept per shipment (vessel|passage):")
    for s in inst.shipment_ids:
        print(f"  {s}: {len(inst.feasible_options[s])} feasible, {len(inst.rejected_options[s])} rejected")

    res_cp = solve_cpsat(inst)
    res_ex = solve_exact(inst)
    res_cp.to_json(out / "assignment_result.json")
    res_ex.to_json(out / "assignment_result_exact.json")

    print("\n=== Result (OR-Tools CP-SAT) ===")
    print("feasible:", res_cp.feasible, "| objective:", res_cp.objective_value,
          f"| runtime: {res_cp.runtime_seconds:.3f}s")
    for w in res_cp.warnings:
        print("WARNING:", w)
    if res_cp.feasible:
        rows = []
        for s in inst.shipment_ids:
            sel = res_cp.selected_options[s]
            vy = inst.voyages[f"{sel['vessel']}|{sel['passage']}"]
            rows.append({"shipment": s, "weight_t": inst.shipments[s]["weight_t"], "vessel": sel["vessel"],
                         "passage": sel["passage"], "hours": round(vy["hours"], 1),
                         "arrival_utc": vy["arrival_utc"], "deadline_utc": inst.shipments[s]["deadline_utc"],
                         "mean_wave_m": None if vy["mean_wave_m"] is None else round(vy["mean_wave_m"], 2)})
        df = pd.DataFrame(rows)
        df.to_csv(out / "assignment_summary.csv", index=False)
        print(df.to_string(index=False))
        print("\nCost breakdown:", {k: v for k, v in res_cp.objective_breakdown.items() if k != "voyages"})
    print("\n=== Cross-check with exact enumeration ===")
    print("exact objective:", res_ex.objective_value, f"| runtime: {res_ex.runtime_seconds:.3f}s")
    same = (res_cp.feasible == res_ex.feasible) and (
        not res_cp.feasible or abs(res_cp.objective_value - res_ex.objective_value) < 0.02)
    print("MATCH" if same else "MISMATCH - investigate!")

if __name__ == "__main__":
    main()
