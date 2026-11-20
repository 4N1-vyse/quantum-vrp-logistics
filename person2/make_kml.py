"""Rebuild maps/maritime_passages.kml from data/ (run after editing waypoints or ports)."""
import pathlib
import pandas as pd
from xml.sax.saxutils import escape

pas = pd.read_csv("data/maritime_passages.csv")
loc = pd.read_csv("data/locations.csv")
colours = {"R1": "ff0000ff", "R2": "ff00a5ff", "R3": "ff00aa00", "R4": "ffff0000", "R5": "ffaa00aa"}  # aabbggrr
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>RouteQ maritime passages</name>']
for rid, c in colours.items():
    out.append(f'<Style id="{rid}"><LineStyle><color>{c}</color><width>3</width></LineStyle></Style>')
for pid, g in pas.groupby("passage_id"):
    g = g.sort_values("seq")
    coords = " ".join(f"{lo},{la},0" for la, lo in zip(g.lat_deg, g.lon_deg))
    out.append(f'<Placemark><name>{escape(pid)}</name><description>Illustrative passage, not for navigation</description>'
               f'<styleUrl>#{g.route_id.iloc[0]}</styleUrl><LineString><tessellate>1</tessellate>'
               f'<coordinates>{coords}</coordinates></LineString></Placemark>')
for _, r in loc.iterrows():
    out.append(f'<Placemark><name>{escape(r["name"])} ({r.location_id})</name>'
               f'<Point><coordinates>{r.lon_deg},{r.lat_deg},0</coordinates></Point></Placemark>')
out.append('</Document></kml>')
pathlib.Path("maps").mkdir(exist_ok=True)
pathlib.Path("maps/maritime_passages.kml").write_text("\n".join(out), encoding="utf-8")
print("wrote maps/maritime_passages.kml with", pas.passage_id.nunique(), "passages")
