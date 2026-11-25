import os
import sys

sys.path.insert(0, "/app")

from app.database.session import SessionLocal, create_tables
from app.models import Attendance, Marks, Student, User


def demo_data_is_complete() -> bool:
    create_tables()
    with SessionLocal() as db:
        return (
            db.query(User).count() >= 209
            and db.query(Student).count() >= 200
            and db.query(Marks).count() > 0
            and db.query(Attendance).count() > 0
        )


def main() -> None:
    if os.getenv("SEED_DEMO_DATA", "false").lower() != "true":
        print("Demo data seeding is disabled.")
        return

    if demo_data_is_complete():
        print("Demo data is already initialized.")
        return

    from scripts.seed import run_seeder

    run_seeder()


if __name__ == "__main__":
    main()
