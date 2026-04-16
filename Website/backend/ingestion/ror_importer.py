from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Iterable

from sqlalchemy import select

from backend.database.models import Alias, SessionLocal, University


def _iter_ror_records(zip_path: Path) -> Iterable[dict]:
    with zipfile.ZipFile(zip_path, "r") as archive:
        with archive.open("ror-data.json") as handle:
            data = json.load(handle)
            for item in data:
                yield item


def import_ror(zip_path: str) -> None:
    path = Path(zip_path)
    if not path.exists():
        raise FileNotFoundError(f"ROR zip not found: {zip_path}")

    with SessionLocal() as session:
        for record in _iter_ror_records(path):
            name = record.get("name")
            if not name:
                continue

            existing = session.scalar(select(University).where(University.name == name))
            if existing:
                continue

            university = University(
                name=name,
                country=(record.get("country", {}) or {}).get("country_name", ""),
                city=(record.get("addresses", [{}])[0] or {}).get("city", ""),
                website=(record.get("links", []) or [""])[0] or "",
            )
            session.add(university)
            session.flush()

            aliases = record.get("aliases", []) or []
            for alias in aliases:
                if not alias:
                    continue
                session.add(Alias(alias=alias, university_id=university.id))

        session.commit()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import ROR data into the database")
    parser.add_argument("zip_path", help="Path to ror-data.json.zip")
    args = parser.parse_args()

    import_ror(args.zip_path)
    print("ROR import complete.")
