Scope: maritime (ship) only. 6 ports, 5 routes.
Units: time in UTC, coordinates lat_deg/lon_deg, distance km and nmi, ship speed knots.
locations.csv: location_id,name,type,lat_deg,lon_deg,source
routes.csv: route_id,origin,destination
maritime_passages.csv: passage_id,route_id,seq,waypoint_name,lat_deg,lon_deg
shipments.csv: shipment_id,mode,route_id,weight_t,deadline_utc,synthetic
Assumptions: ship speed 16 kn, route R1 has 2 passages (R1-A, R1-B), other routes 1 passage each, 5 synthetic shipments.