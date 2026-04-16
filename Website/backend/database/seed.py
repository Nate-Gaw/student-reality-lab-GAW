from __future__ import annotations

from datetime import datetime

from backend.database.models import Alias, SalaryData, SessionLocal, TuitionCost, University


def seed() -> None:
    now = datetime.utcnow().strftime("%Y-%m-%d")
    with SessionLocal() as session:
        def get_or_create(name: str, country: str, city: str, website: str) -> University:
            existing = session.query(University).filter(University.name == name).one_or_none()
            if existing:
                return existing
            university = University(name=name, country=country, city=city, website=website)
            session.add(university)
            session.flush()
            return university

        njit = get_or_create("New Jersey Institute of Technology", "USA", "Newark", "https://www.njit.edu")
        rutgers = get_or_create("Rutgers University-New Brunswick", "USA", "New Brunswick", "https://www.rutgers.edu")
        mit = get_or_create("Massachusetts Institute of Technology", "USA", "Cambridge", "https://www.mit.edu")
        stanford = get_or_create("Stanford University", "USA", "Stanford", "https://www.stanford.edu")
        harvard = get_or_create("Harvard University", "USA", "Cambridge", "https://www.harvard.edu")
        princeton = get_or_create("Princeton University", "USA", "Princeton", "https://www.princeton.edu")
        michigan = get_or_create("University of Michigan", "USA", "Ann Arbor", "https://www.umich.edu")
        berkeley = get_or_create("University of California, Berkeley", "USA", "Berkeley", "https://www.berkeley.edu")
        cmu = get_or_create("Carnegie Mellon University", "USA", "Pittsburgh", "https://www.cmu.edu")

        existing_aliases = {row.alias.lower() for row in session.query(Alias).all()}
        desired_aliases = [
            ("NJIT", njit.id),
            ("Rutgers", rutgers.id),
            ("Rugers", rutgers.id),
            ("Rutgers NB", rutgers.id),
            ("Rutgers-New Brunswick", rutgers.id),
            ("MIT", mit.id),
            ("Stanford", stanford.id),
            ("Harvard", harvard.id),
            ("Princeton", princeton.id),
            ("UMich", michigan.id),
            ("U Michigan", michigan.id),
            ("UC Berkeley", berkeley.id),
            ("Berkeley", berkeley.id),
            ("Carnegie Mellon", cmu.id),
            ("CMU", cmu.id),
        ]
        for alias, university_id in desired_aliases:
            if alias.lower() in existing_aliases:
                continue
            session.add(Alias(alias=alias, university_id=university_id))

        existing_cost_ids = {row.university_id for row in session.query(TuitionCost).all()}
        cost_rows = [
            (njit.id, 28000, 12000, 11000, 75),
            (rutgers.id, 32000, 14000, 12000, 70),
            (mit.id, 57590, 12680, 5540, 75),
            (stanford.id, 62000, 16000, 7000, 90),
            (harvard.id, 54000, 15000, 6500, 85),
            (princeton.id, 53000, 15500, 6400, 85),
            (michigan.id, 51000, 14000, 6500, 75),
            (berkeley.id, 48000, 15500, 7200, 80),
            (cmu.id, 59000, 15000, 6800, 85),
        ]
        for university_id, tuition, housing, living_cost, application_fee in cost_rows:
            if university_id in existing_cost_ids and university_id not in {njit.id, rutgers.id}:
                continue
            session.add(
                TuitionCost(
                    university_id=university_id,
                    tuition=tuition,
                    housing=housing,
                    living_cost=living_cost,
                    application_fee=application_fee,
                    source="seed",
                    last_updated=now,
                )
            )

        existing_salary_ids = {row.university_id for row in session.query(SalaryData).all()}
        salary_rows = [
            (njit.id, 95000, 45000),
            (rutgers.id, 110000, 40000),
            (mit.id, 130000, 60000),
            (stanford.id, 140000, 65000),
            (harvard.id, 135000, 55000),
            (princeton.id, 133000, 54000),
            (michigan.id, 115000, 50000),
            (berkeley.id, 135000, 55000),
            (cmu.id, 138000, 62000),
        ]
        for university_id, median_salary, average_debt in salary_rows:
            if university_id in existing_salary_ids and university_id not in {njit.id, rutgers.id}:
                continue
            session.add(
                SalaryData(
                    university_id=university_id,
                    median_salary=median_salary,
                    average_debt=average_debt,
                    roi_score=None,
                )
            )

        session.commit()


if __name__ == "__main__":
    seed()
    print("Seed data inserted.")
