import time
import pandas as pd
from weather import fetch_marine

pas = pd.read_csv("data/maritime_passages.csv")
points = sorted({(round(a, 2), round(b, 2)) for a, b in zip(pas.lat_deg, pas.lon_deg)})
print(len(points), "unique points")
for i, (la, lo) in enumerate(points, 1):
    try:
        fetch_marine(la, lo, days=7)      # saved into the cache folder
        print(i, la, lo, "ok")
    except Exception as e:
        print(i, la, lo, "FAILED", e)
    time.sleep(0.3)
