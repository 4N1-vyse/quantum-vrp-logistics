# RouteQ - Person 2: data + classical optimization (maritime only)

What this project part does
1. Real forecast data (Open-Meteo) for every waypoint of every candidate passage, cached in `cache/`.
2. Sails each passage with each vessel, sampling the forecast at the hour the vessel gets there.
3. Builds an **AssignmentInstance** (all feasible vessel/passage options and their costs).
4. Solves it with OR-Tools CP-SAT and cross-checks with exact enumeration.
5. Returns an **AssignmentResult** (selected vessel and passage per shipment, total cost, breakdown, feasibility, runtime).

## Run it (Windows, PowerShell, inside this folder)
```
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pytest                      # expect: 19 passed
python run_optimizer.py --no-weather  # works offline, waves and currents ignored (labelled)
python fetch_all.py                   # real forecast, about 1 minute, needs internet
python run_optimizer.py               # the real run, uses cache/
```
If `activate` is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
If `pip install -r` fails on a pinned version, run `python -m pip install pandas requests ortools pytest`.

## Files
| File | Purpose |
|---|---|
| `data/*.csv` | ports, routes, passages (71 rows), shipments, vessels |
| `geo.py` | distance, heading, time per segment with ocean current |
| `conditions.py` | read current from the forecast, km/h to knots, never reuse last value |
| `weather.py`, `fetch_all.py` | fetch and cache Open-Meteo forecasts (44 unique points) |
| `voyage.py` | sail one passage with one vessel speed, sampling forecast on arrival time |
| `instance.py` | AssignmentInstance, AssignmentResult, `build_instance()` |
| `optimizer.py` | `solve_cpsat()` and `solve_exact()` |
| `run_optimizer.py` | build, solve, compare, write `output/` |
| `test_*.py` | 19 tests |
| `docs/` | data spec, data manifest (fill it), optimizer notes for the viva |
| `maps/maritime_passages.kml` | import into Google My Maps to see the passages as lines |

## Output files (in `output/`)
`assignment_instance.json` (input for the solvers; Person 3 can reuse it), `assignment_result.json`, `assignment_result_exact.json`, `assignment_summary.csv`.

## Your to-do list (cannot be done by the code)
1. Run `fetch_all.py` and fill `docs/data_manifest.md` (fetch time, valid window, 44 points).
2. Verify the 6 port coordinates against the World Port Index or UN/LOCODE and edit `data/locations.csv` (`source` column).
3. Look at `maps/maritime_passages.kml` in Google My Maps; fix any waypoint on land.
4. Check the forecast response units and direction convention (km/h and degrees "toward" are assumed and tested).
5. Tell Persons 1 and 3: shipments.csv has `route_id`; vessels.csv now has 6 vessels; the interface is in `instance.py`.

## What you can honestly claim
Best assignment under our cost model, constructed candidate passages, synthetic fleet, saved forecast snapshot. Not claimed: globally optimal routes, real-time operation, "safe route", quantum advantage.
