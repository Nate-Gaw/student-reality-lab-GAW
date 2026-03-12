"""
Database interface for storing and retrieving university cost data.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Enum, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=ROOT_ENV_PATH)

Base = declarative_base()


class University(Base):
    """University cost record table."""
    __tablename__ = "universities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    university_name = Column(String(500), nullable=False, index=True)
    country = Column(String(100), nullable=False, index=True)
    city = Column(String(200))
    
    degree_level = Column(String(50), nullable=False, index=True)
    program_name = Column(String(500))
    programs = Column(JSON)  # List of available programs
    
    currency = Column(String(10), default="USD")
    domestic_tuition = Column(Float)
    international_tuition = Column(Float)
    application_fee = Column(Float)
    estimated_housing_cost = Column(Float)
    estimated_living_cost = Column(Float)
    estimated_total_annual_cost = Column(Float)
    
    student_fees = Column(Float)
    books_supplies = Column(Float)
    health_insurance = Column(Float)
    
    has_scholarships = Column(Boolean)
    has_financial_aid = Column(Boolean)
    average_scholarship_amount = Column(Float)
    
    acceptance_rate = Column(Float)
    graduation_rate = Column(Float)
    enrollment_count = Column(Integer)
    international_student_percentage = Column(Float)
    
    official_website = Column(Text)
    data_source = Column(String(200))
    last_updated = Column(DateTime, default=datetime.now, index=True)
    data_quality_score = Column(Float, default=1.0)


class DatabaseManager:
    """Manage database connections and queries."""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///universities.db")
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def add_university(self, university_data: Dict) -> int:
        """Add a university record to the database."""
        session = self.get_session()
        try:
            university = University(**university_data)
            session.add(university)
            session.commit()
            session.refresh(university)
            return university.id
        finally:
            session.close()
    
    def get_university_by_name(self, name: str, degree_level: Optional[str] = None) -> List[Dict]:
        """Get university records by name."""
        session = self.get_session()
        try:
            query = session.query(University).filter(University.university_name.ilike(f"%{name}%"))
            if degree_level:
                query = query.filter(University.degree_level == degree_level)
            results = query.all()
            return [self._to_dict(r) for r in results]
        finally:
            session.close()
    
    def get_universities_by_country(self, country: str, degree_level: Optional[str] = None) -> List[Dict]:
        """Get all universities in a country."""
        session = self.get_session()
        try:
            query = session.query(University).filter(University.country.ilike(f"%{country}%"))
            if degree_level:
                query = query.filter(University.degree_level == degree_level)
            results = query.all()
            return [self._to_dict(r) for r in results]
        finally:
            session.close()
    
    def search_universities(self, search_term: str, limit: int = 50) -> List[Dict]:
        """Search universities by name, country, or program."""
        session = self.get_session()
        try:
            query = session.query(University).filter(
                (University.university_name.ilike(f"%{search_term}%")) |
                (University.country.ilike(f"%{search_term}%")) |
                (University.city.ilike(f"%{search_term}%"))
            ).limit(limit)
            results = query.all()
            return [self._to_dict(r) for r in results]
        finally:
            session.close()
    
    def get_stale_records(self, days: int = 90) -> List[Dict]:
        """Get records that haven't been updated in X days."""
        session = self.get_session()
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            results = session.query(University).filter(University.last_updated < cutoff_date).all()
            return [self._to_dict(r) for r in results]
        finally:
            session.close()
    
    def update_university(self, university_id: int, update_data: Dict):
        """Update a university record."""
        session = self.get_session()
        try:
            session.query(University).filter(University.id == university_id).update({
                **update_data,
                "last_updated": datetime.now()
            })
            session.commit()
        finally:
            session.close()
    
    @staticmethod
    def _to_dict(university: University) -> Dict:
        """Convert University object to dictionary."""
        return {
            "id": university.id,
            "university_name": university.university_name,
            "country": university.country,
            "city": university.city,
            "degree_level": university.degree_level,
            "program_name": university.program_name,
            "programs": university.programs,
            "currency": university.currency,
            "domestic_tuition": university.domestic_tuition,
            "international_tuition": university.international_tuition,
            "application_fee": university.application_fee,
            "estimated_housing_cost": university.estimated_housing_cost,
            "estimated_living_cost": university.estimated_living_cost,
            "estimated_total_annual_cost": university.estimated_total_annual_cost,
            "student_fees": university.student_fees,
            "books_supplies": university.books_supplies,
            "health_insurance": university.health_insurance,
            "has_scholarships": university.has_scholarships,
            "has_financial_aid": university.has_financial_aid,
            "average_scholarship_amount": university.average_scholarship_amount,
            "acceptance_rate": university.acceptance_rate,
            "graduation_rate": university.graduation_rate,
            "enrollment_count": university.enrollment_count,
            "international_student_percentage": university.international_student_percentage,
            "official_website": university.official_website,
            "data_source": university.data_source,
            "last_updated": university.last_updated.isoformat() if university.last_updated else None,
            "data_quality_score": university.data_quality_score,
        }
