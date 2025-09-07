from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
from datetime import datetime

class ResourceValidator(BaseModel):
    name: str
    area: str
    quarterly_data: Dict[str, float]
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v
    
    @validator('quarterly_data')
    def validate_quarters(cls, v):
        for quarter, value in v.items():
            if not isinstance(value, (int, float)):
                raise ValueError(f'Quarter {quarter} must have numeric value')
            if value < 0:
                raise ValueError(f'Quarter {quarter} cannot have negative value')
        return v

class TrialValidator(BaseModel):
    name: str
    area: str
    subjects: int
    start_date: str
    end_date: str
    
    @validator('subjects')
    def subjects_positive(cls, v):
        if v <= 0:
            raise ValueError('Subjects must be positive')
        return v

def validate_uploaded_data(data: Dict) -> Dict[str, Any]:
    """Validate the structure of uploaded data"""
    errors = []
    
    # Check required fields
    if 'resources' not in data:
        errors.append("Missing 'resources' field")
    if 'trials' not in data:
        errors.append("Missing 'trials' field")
    
    if errors:
        return {"valid": False, "errors": errors}
    
    # Validate each resource
    for i, resource in enumerate(data['resources']):
        try:
            ResourceValidator(**resource)
        except Exception as e:
            errors.append(f"Resource {i}: {str(e)}")
    
    # Validate each trial
    for i, trial in enumerate(data['trials']):
        try:
            TrialValidator(**trial)
        except Exception as e:
            errors.append(f"Trial {i}: {str(e)}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "resources_count": len(data.get('resources', [])),
        "trials_count": len(data.get('trials', []))
    }
