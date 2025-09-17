from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..models.models import Allocation, ClinicalTrial, Milestone, Resource, StatusEnum, Base, Quota, UserQuota
from ..schemas import (
    Allocation as AllocationSchema,
    AllocationCreate,
    ClinicalTrial as ClinicalTrialSchema,
    ClinicalTrialCreate,
    ClinicalTrialUpdate,
    Resource as ResourceSchema,
    ResourceCreate,
    Quota as QuotaSchema,
    QuotaCreate,
    UserQuota as UserQuotaSchema,
    UserQuotaCreate,
)
from ..websocket_manager import manager
from ..services.forecasting_service import (
    predict_phase3_next_four_quarters,
    train_phase3_forecast_model,
)


# Simple SQLite for demo/hackathon; replace with proper settings/engine in production
DATABASE_URL = "sqlite:///./clinical_trials.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables if not exist (hackathon convenience)
Base.metadata.create_all(bind=engine)


router = APIRouter(prefix="/api", tags=["trials"])


@router.post("/trials", response_model=ClinicalTrialSchema)
def create_trial(trial_in: ClinicalTrialCreate, db: Session = Depends(get_db)):
    if db.query(ClinicalTrial).filter(ClinicalTrial.name == trial_in.name).first():
        raise HTTPException(status_code=400, detail="Trial with this name already exists")
    trial = ClinicalTrial(
        name=trial_in.name,
        sponsor=trial_in.sponsor,
        phase=trial_in.phase,
        status=trial_in.status,
        start_date=trial_in.start_date,
        estimated_dbl_date=trial_in.estimated_dbl_date,
    )
    db.add(trial)
    db.commit()
    db.refresh(trial)
    return trial


@router.get("/trials", response_model=List[ClinicalTrialSchema])
def list_trials(db: Session = Depends(get_db)):
    trials = db.query(ClinicalTrial).all()
    return trials


@router.get("/trials/{trial_id}", response_model=ClinicalTrialSchema)
def get_trial(trial_id: int, db: Session = Depends(get_db)):
    trial = db.get(ClinicalTrial, trial_id)
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    return trial


@router.put("/trials/{trial_id}", response_model=ClinicalTrialSchema)
def update_trial(trial_id: int, trial_update: ClinicalTrialUpdate, db: Session = Depends(get_db)):
    trial = db.get(ClinicalTrial, trial_id)
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")

    new_status = trial_update.status

    for field, value in trial_update.dict(exclude_unset=True).items():
        setattr(trial, field, value)

    db.add(trial)
    db.commit()
    db.refresh(trial)

    # Step 1: create milestone on specific status transitions
    if new_status in {StatusEnum.APPROVED, StatusEnum.FPFV_REACHED, StatusEnum.DBL}:
        ms = Milestone(trial_id=trial.id, milestone_name=new_status.value, date_achieved=datetime.utcnow())
        db.add(ms)
        db.commit()

    # Step 2: automated resource release upon DBL
    if new_status == StatusEnum.DBL:
        allocations = db.query(Allocation).filter(Allocation.trial_id == trial.id).all()
        for alloc in allocations:
            resource = db.get(Resource, alloc.resource_id)
            if resource:
                resource.available_units += alloc.allocated_units
                db.add(resource)
        # delete allocations
        db.query(Allocation).filter(Allocation.trial_id == trial.id).delete()
        db.commit()

        # broadcast resource updates
        resources = db.query(Resource).all()
        message = {
            "type": "resources_update",
            "resources": [
                {
                    "id": r.id,
                    "skill_type": r.skill_type,
                    "total_units": r.total_units,
                    "available_units": r.available_units,
                }
                for r in resources
            ],
        }
        try:
            import anyio

            anyio.from_thread.run(manager.broadcast, message)
        except Exception:
            pass

    return trial


@router.post("/trials/{trial_id}/resources", response_model=AllocationSchema)
def allocate_resource(trial_id: int, alloc_in: AllocationCreate, db: Session = Depends(get_db)):
    trial = db.get(ClinicalTrial, trial_id)
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    # Prevent new allocations for trials at/after DBL or COMPLETED
    if trial.status in {StatusEnum.DBL, StatusEnum.COMPLETED}:
        raise HTTPException(status_code=400, detail="Allocations are not permitted for trials at/after DBL")
    resource = db.get(Resource, alloc_in.resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    if alloc_in.allocated_units <= 0:
        raise HTTPException(status_code=400, detail="allocated_units must be greater than 0")
    if resource.available_units < alloc_in.allocated_units:
        raise HTTPException(status_code=400, detail="Insufficient available units")

    # Team quotas are not enforced per committee directive; only per-user quotas apply

    # Enforce user quotas if present
    if alloc_in.user_name:
        now = datetime.utcnow()
        u_quota = (
            db.query(UserQuota)
            .filter(
                UserQuota.user_name == alloc_in.user_name,
                UserQuota.skill_type == resource.skill_type,
                ((UserQuota.trial_id == trial.id) | (UserQuota.trial_id.is_(None))),
                ((UserQuota.start_date.is_(None)) | (UserQuota.start_date <= now)),
                ((UserQuota.end_date.is_(None)) | (UserQuota.end_date >= now)),
            )
            .order_by(UserQuota.trial_id.desc().nulls_last())
            .first()
        )
        if u_quota:
            user_alloc_q = db.query(Allocation).join(Resource, Allocation.resource_id == Resource.id).filter(
                Allocation.user_name == alloc_in.user_name,
                Resource.skill_type == resource.skill_type,
            )
            if u_quota.trial_id is not None:
                user_alloc_q = user_alloc_q.filter(Allocation.trial_id == trial.id)
            current_units = sum(a.allocated_units for a in user_alloc_q.all())
            if current_units + alloc_in.allocated_units > u_quota.max_units:
                raise HTTPException(status_code=400, detail="User quota exceeded for this skill/trial/time window")

    allocation = Allocation(
        trial_id=trial.id,
        resource_id=resource.id,
        allocated_units=alloc_in.allocated_units,
        team_name=alloc_in.team_name,
        user_name=alloc_in.user_name,
    )
    resource.available_units -= alloc_in.allocated_units
    db.add(allocation)
    db.add(resource)
    db.commit()
    db.refresh(allocation)

    # broadcast update
    message = {
        "type": "allocation_created",
        "allocation": {
            "id": allocation.id,
            "trial_id": allocation.trial_id,
            "resource_id": allocation.resource_id,
            "allocated_units": allocation.allocated_units,
            "allocation_date": allocation.allocation_date.isoformat(),
        },
        "resource": {
            "id": resource.id,
            "skill_type": resource.skill_type,
            "total_units": resource.total_units,
            "available_units": resource.available_units,
        },
    }
    try:
        import anyio

        anyio.from_thread.run(manager.broadcast, message)
    except Exception:
        pass

    return allocation


@router.get("/resources", response_model=List[ResourceSchema])
def list_resources(db: Session = Depends(get_db)):
    return db.query(Resource).all()


@router.post("/resources", response_model=ResourceSchema)
def create_resource(resource_in: ResourceCreate, db: Session = Depends(get_db)):
    resource = Resource(
        skill_type=resource_in.skill_type,
        total_units=resource_in.total_units,
        available_units=resource_in.available_units,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.post("/quotas", response_model=QuotaSchema)
def create_quota(quota_in: QuotaCreate, db: Session = Depends(get_db)):
    quota = Quota(
        team_name=quota_in.team_name,
        skill_type=quota_in.skill_type,
        trial_id=quota_in.trial_id,
        max_units=quota_in.max_units,
        start_date=quota_in.start_date,
        end_date=quota_in.end_date,
    )
    db.add(quota)
    db.commit()
    db.refresh(quota)
    return quota


@router.get("/quotas", response_model=List[QuotaSchema])
def list_quotas(db: Session = Depends(get_db)):
    return db.query(Quota).all()


@router.post("/user-quotas", response_model=UserQuotaSchema)
def create_user_quota(quota_in: UserQuotaCreate, db: Session = Depends(get_db)):
    quota = UserQuota(
        user_name=quota_in.user_name,
        skill_type=quota_in.skill_type,
        trial_id=quota_in.trial_id,
        max_units=quota_in.max_units,
        start_date=quota_in.start_date,
        end_date=quota_in.end_date,
    )
    db.add(quota)
    db.commit()
    db.refresh(quota)
    return quota


@router.get("/user-quotas", response_model=List[UserQuotaSchema])
def list_user_quotas(db: Session = Depends(get_db)):
    return db.query(UserQuota).all()


@router.post("/trials/{trial_id}/forecast")
def forecast_phase3(trial_id: int, db: Session = Depends(get_db)):
    trial = db.get(ClinicalTrial, trial_id)
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    if trial.phase != trial.phase.PHASE_2:
        raise HTTPException(status_code=400, detail="Forecasting is only available for Phase 2 trials")

    model, enc, skill_types = train_phase3_forecast_model()

    # Assume forecast starts next quarter from now
    now = datetime.utcnow()
    current_quarter = (now.month - 1) // 3 + 1
    next_quarter = current_quarter + 1 if current_quarter < 4 else 1
    start_year = now.year if current_quarter < 4 else now.year + 1

    predictions = predict_phase3_next_four_quarters(model, enc, start_year, next_quarter, skill_types)
    return {"trial_id": trial_id, "phase": "PHASE_3", "forecasts": predictions}


