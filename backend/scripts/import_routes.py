import csv
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models import Route


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_FILE = PROJECT_ROOT / "csv_data" / "routes.csv"


def import_routes(db: Session):
    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            route = Route(
                route_id=row["route_id"],
                origin=row["origin"],
                destination=row["destination"],
            )

            existing = db.get(Route, route.route_id)

            if existing:
                existing.origin = route.origin
                existing.destination = route.destination
            else:
                db.add(route)

        db.commit()


if __name__ == "__main__":
    db = SessionLocal()

    try:
        import_routes(db)
        print("Routes imported successfully.")

        routes = db.query(Route).all()

        for route in routes:
            print(
                f"{route.route_id}: "
                f"{route.origin} -> {route.destination}"
            )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
