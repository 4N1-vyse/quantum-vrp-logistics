import csv
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models import Vessel


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CSV_FILE = PROJECT_ROOT / "csv_data" / "vessels.csv"


def import_vessels(db: Session):
    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            vessel_id = row["vessel_id"]

            vessel = db.get(Vessel, vessel_id)

            if vessel is None:
                vessel = Vessel(vessel_id=vessel_id)
                db.add(vessel)

            vessel.type = row["type"]
            vessel.capacity_t = float(row["capacity_t"])
            vessel.speed_kn = float(row["speed_kn"])
            vessel.is_synthetic = row["synthetic"].strip().lower() in (
                "yes", "true", "1"
            )

        db.commit()


if __name__ == "__main__":
    db = SessionLocal()

    try:
        import_vessels(db)
        print("Vessels imported successfully.")

        vessels = db.query(Vessel).all()

        for vessel in vessels:
            print(
                f"{vessel.vessel_id}: {vessel.type}, "
                f"Capacity: {vessel.capacity_t} tonnes, "
                f"Speed: {vessel.speed_kn} knots"
            )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
