from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "universities.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")


class Base(DeclarativeBase):
    pass


class University(Base):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    country: Mapped[str] = mapped_column(String(64), default="")
    city: Mapped[str] = mapped_column(String(128), default="")
    website: Mapped[str] = mapped_column(String(255), default="")

    aliases: Mapped[list[Alias]] = relationship("Alias", back_populates="university")
    tuition_costs: Mapped[list[TuitionCost]] = relationship("TuitionCost", back_populates="university")
    salary_data: Mapped[list[SalaryData]] = relationship("SalaryData", back_populates="university")


class Alias(Base):
    __tablename__ = "aliases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alias: Mapped[str] = mapped_column(String(255), index=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), index=True)

    university: Mapped[University] = relationship("University", back_populates="aliases")


class TuitionCost(Base):
    __tablename__ = "tuition_costs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), index=True)
    tuition: Mapped[float | None] = mapped_column(Float)
    housing: Mapped[float | None] = mapped_column(Float)
    living_cost: Mapped[float | None] = mapped_column(Float)
    application_fee: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(255), default="")
    last_updated: Mapped[str] = mapped_column(String(64), default="")

    university: Mapped[University] = relationship("University", back_populates="tuition_costs")


class SalaryData(Base):
    __tablename__ = "salary_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id"), index=True)
    median_salary: Mapped[float | None] = mapped_column(Float)
    average_debt: Mapped[float | None] = mapped_column(Float)
    roi_score: Mapped[float | None] = mapped_column(Float)

    university: Mapped[University] = relationship("University", back_populates="salary_data")


class RagDocument(Base):
    __tablename__ = "rag_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    university: Mapped[str] = mapped_column(String(255), default="")
    title: Mapped[str] = mapped_column(String(255), default="")
    source_url: Mapped[str] = mapped_column(String(512), default="")
    category: Mapped[str] = mapped_column(String(128), default="")
    full_text: Mapped[str] = mapped_column(Text, default="")
    checksum: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[str] = mapped_column(String(64), default="")
    updated_at: Mapped[str] = mapped_column(String(64), default="")

    chunks: Mapped[list[RagChunk]] = relationship("RagChunk", back_populates="document")


class RagChunk(Base):
    __tablename__ = "rag_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chunk_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    doc_id: Mapped[int] = mapped_column(ForeignKey("rag_documents.id"), index=True)
    chunk_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(String(64), default="")

    document: Mapped[RagDocument] = relationship("RagDocument", back_populates="chunks")


engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Generator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
