from datetime import datetime
from enum import Enum
from typing import List

from sqlalchemy import Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class PhaseEnum(str, Enum):
    PHASE_1 = "PHASE_1"
    PHASE_2 = "PHASE_2"
    PHASE_3 = "PHASE_3"


class StatusEnum(str, Enum):
    PLANNING = "PLANNING"
    APPROVED = "APPROVED"
    RECRUITING = "RECRUITING"
    FPFV_REACHED = "FPFV_REACHED"
    ACTIVE = "ACTIVE"
    DBL = "DBL"
    COMPLETED = "COMPLETED"


class ClinicalTrial(Base):
    __tablename__ = "clinicaltrial"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    sponsor: Mapped[str] = mapped_column(String, nullable=False)
    phase: Mapped[PhaseEnum] = mapped_column(SAEnum(PhaseEnum), nullable=False)
    status: Mapped[StatusEnum] = mapped_column(SAEnum(StatusEnum), nullable=False, default=StatusEnum.PLANNING)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estimated_dbl_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    allocations: Mapped[List["Allocation"]] = relationship("Allocation", back_populates="trial", cascade="all, delete-orphan")
    milestones: Mapped[List["Milestone"]] = relationship("Milestone", back_populates="trial", cascade="all, delete-orphan")


class Resource(Base):
    __tablename__ = "resource"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_type: Mapped[str] = mapped_column(String, nullable=False)
    total_units: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)
    available_units: Mapped[float] = mapped_column(Float, nullable=False, default=10.0)

    allocations: Mapped[List["Allocation"]] = relationship("Allocation", back_populates="resource")


class Allocation(Base):
    __tablename__ = "allocation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trial_id: Mapped[int] = mapped_column(ForeignKey("clinicaltrial.id"), nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id"), nullable=False)
    allocated_units: Mapped[float] = mapped_column(Float, nullable=False)
    allocation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    team_name: Mapped[str | None] = mapped_column(String, nullable=True)
    user_name: Mapped[str | None] = mapped_column(String, nullable=True)

    trial: Mapped[ClinicalTrial] = relationship("ClinicalTrial", back_populates="allocations")
    resource: Mapped[Resource] = relationship("Resource", back_populates="allocations")


class Milestone(Base):
    __tablename__ = "milestone"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trial_id: Mapped[int] = mapped_column(ForeignKey("clinicaltrial.id"), nullable=False)
    milestone_name: Mapped[str] = mapped_column(String, nullable=False)
    date_achieved: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    trial: Mapped[ClinicalTrial] = relationship("ClinicalTrial", back_populates="milestones")


class Quota(Base):
    __tablename__ = "quota"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    skill_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Optional trial-bound quota; if null, applies across trials
    trial_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    max_units: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class UserQuota(Base):
    __tablename__ = "user_quota"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    skill_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    # Optional trial-bound quota; if null, applies across trials
    trial_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    max_units: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


