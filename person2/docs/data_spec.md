# Data specification (Person 2) - maritime only

Scope: maritime (ship) only. 6 ports, 5 routes, 10 candidate passages, 6 synthetic vessels, 6 synthetic shipments.

## Conventions
| Item | Rule |
|---|---|
| Time | UTC, ISO-8601 with Z |
| Coordinates | decimal degrees WGS84, fields lat_deg / lon_deg |
| Distance | nautical miles (nmi); 1 nmi = 1.852 km |
| Speed | knots (kn). Forecast current speed arrives in km/h and is divided by 1.852 |
| Weight | tonnes (t) |
| Direction | degrees clockwise from north. Open-Meteo current direction = direction the current flows TOWARD |
| Cost | abstract cost units |
| Missing data | flagged in `warnings`, never filled silently. Forecast hours outside the fetched window return "no data" (the last value is never reused) |

## Files in /data
| File | Columns | Origin |
|---|---|---|
| locations.csv | location_id,name,type,lat_deg,lon_deg,source | Real ports, coordinates from Google Maps (verify against World Port Index / UN/LOCODE) |
| routes.csv | route_id,origin,destination | Scenario choice (real port pairs) |
| maritime_passages.csv | passage_id,route_id,seq,waypoint_name,lat_deg,lon_deg | Constructed illustrative paths, not navigation data |
| shipments.csv | shipment_id,mode,route_id,weight_t,earliest_departure_utc,deadline_utc,synthetic | Synthetic |
| vessels.csv | vessel_id,type,capacity_t,speed_kn,hour_rate,tonne_rate,synthetic | Synthetic |
| cache/marine_<lat>_<lon>.json | fetched_at_utc, source, url, response | Real: Open-Meteo Marine API |

## Assumptions
1. All vessels are available at the origin port at the plan start.
2. Each vessel makes at most one voyage; shipments on the same route and passage can share a voyage.
3. Constant through-water speed per vessel; ocean current changes speed over ground by its along-track component only.
4. Voyage cost = hour_rate x hours + 20 x mean wave height (m); plus tonne_rate x weight for each shipment.
5. A shipment is allowed on a voyage only if the vessel can carry it alone and the voyage arrives by the deadline.
6. When a forecast exists, synthetic shipment times are shifted so that the scenario starts at the forecast start.
7. Waves and currents are a comparison aid, not a safety assessment. No "safe route" claims.
