from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .models.models import PhaseEnum, StatusEnum


# Resource Schemas
class ResourceBase(BaseModel):
    skill_type: str
    total_units: float = 10.0
    available_units: float = 10.0


class ResourceCreate(ResourceBase):
    pass


class Resource(ResourceBase):
    id: int

    class Config:
        from_attributes = True


# Allocation Schemas
class AllocationBase(BaseModel):
    trial_id: int
    resource_id: int
    allocated_units: float
    team_name: str | None = None
    user_name: str | None = None


class AllocationCreate(AllocationBase):
    pass


class Allocation(AllocationBase):
    id: int
    allocation_date: datetime

    class Config:
        from_attributes = True


# Milestone Schemas
class MilestoneBase(BaseModel):
    trial_id: int
    milestone_name: str


class MilestoneCreate(MilestoneBase):
    pass


class Milestone(MilestoneBase):
    id: int
    date_achieved: datetime

    class Config:
        from_attributes = True


# Clinical Trial Schemas
class ClinicalTrialBase(BaseModel):
    name: str
    sponsor: str
    phase: PhaseEnum
    status: StatusEnum = StatusEnum.PLANNING
    start_date: Optional[datetime] = None
    estimated_dbl_date: Optional[datetime] = None


class ClinicalTrialCreate(ClinicalTrialBase):
    pass


class ClinicalTrialUpdate(BaseModel):
    name: Optional[str] = None
    sponsor: Optional[str] = None
    phase: Optional[PhaseEnum] = None
    status: Optional[StatusEnum] = None
    start_date: Optional[datetime] = None
    estimated_dbl_date: Optional[datetime] = None


class ClinicalTrial(ClinicalTrialBase):
    id: int
    allocations: List[Allocation] = []
    milestones: List[Milestone] = []

    class Config:
        from_attributes = True


# Quota Schemas
class QuotaBase(BaseModel):
    team_name: str
    skill_type: str
    trial_id: int | None = None
    max_units: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class QuotaCreate(QuotaBase):
    pass


class Quota(QuotaBase):
    id: int

    class Config:
        from_attributes = True


# User Quota Schemas
class UserQuotaBase(BaseModel):
    user_name: str
    skill_type: str
    trial_id: int | None = None
    max_units: float
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class UserQuotaCreate(UserQuotaBase):
    pass


class UserQuota(UserQuotaBase):
    id: int

    class Config:
        from_attributes = True


