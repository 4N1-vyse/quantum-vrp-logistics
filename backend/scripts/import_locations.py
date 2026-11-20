import csv
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models import Location


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_FILE = PROJECT_ROOT / "csv_data" / "locations.csv"


def import_locations(db: Session):
    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            location = Location(
                location_id=row["location_id"],
                name=row["name"],
                type=row["type"],
                lat_deg=float(row["lat_deg"]),
                lon_deg=float(row["lon_deg"]),
                source=row["source"],
            )

            existing = db.get(Location, location.location_id)

            if existing:
                for key, value in {
                    "name": location.name,
                    "type": location.type,
                    "lat_deg": location.lat_deg,
                    "lon_deg": location.lon_deg,
                    "source": location.source,
                }.items():
                    setattr(existing, key, value)
            else:
                db.add(location)

        db.commit()


if __name__ == "__main__":
    db = SessionLocal()

    try:
        import_locations(db)
        print("Locations imported successfully.")

        locations = db.query(Location).all()

        for location in locations:
            print(location.location_id, "-", location.name)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
