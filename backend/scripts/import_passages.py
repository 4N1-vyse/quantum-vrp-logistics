import csv
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models import Passage, Waypoint


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_FILE = PROJECT_ROOT / "csv_data" / "maritime_passages.csv"


def import_passages(db: Session):
    passages = {
        passage.passage_id: passage
        for passage in db.query(Passage).all()
    }

    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            passage_id = row["passage_id"]
            route_id = row["route_id"]

            if passage_id not in passages:
                passage = Passage(
                    passage_id=passage_id,
                    route_id=route_id,
                )
                db.add(passage)
                passages[passage_id] = passage

            elif passages[passage_id].route_id != route_id:
                raise ValueError(
                    f"Passage {passage_id} has an unexpected route ID"
                )

            seq = int(row["seq"])

            waypoint = (
                db.query(Waypoint)
                .filter(
                    Waypoint.passage_id == passage_id,
                    Waypoint.seq == seq,
                )
                .first()
            )

            if waypoint is None:
                waypoint = Waypoint(
                    passage_id=passage_id,
                    seq=seq,
                    waypoint_name=row["waypoint_name"],
                    lat_deg=float(row["lat_deg"]),
                    lon_deg=float(row["lon_deg"]),
                )
                db.add(waypoint)
            else:
                waypoint.waypoint_name = row["waypoint_name"]
                waypoint.lat_deg = float(row["lat_deg"])
                waypoint.lon_deg = float(row["lon_deg"])

        db.commit()


if __name__ == "__main__":
    db = SessionLocal()

    try:
        import_passages(db)
        print("Passages and waypoints imported successfully.")

        passages = db.query(Passage).all()

        for passage in passages:
            waypoint_count = (
                db.query(Waypoint)
                .filter(Waypoint.passage_id == passage.passage_id)
                .count()
            )

            print(
                f"{passage.passage_id} "
                f"(Route {passage.route_id}): "
                f"{waypoint_count} waypoints"
            )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
