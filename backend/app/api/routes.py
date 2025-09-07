from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict, Any
import json
import re
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Clinical Trials"])

# In-memory storage for demo (replace with database later)
current_data = {}

class QuarterlyDataProcessor:
    """Handles the dynamic quarterly header problem"""
    
    def __init__(self):
        self.current_quarters = []
        
    def detect_quarter_columns(self, data: Dict) -> List[str]:
        """Detect quarter columns like Q3-2025, Q4-2025, etc."""
        quarter_pattern = r'Q[1-4]-20[0-9]{2}'
        quarters = []
        
        if isinstance(data, dict) and 'resources' in data:
            for resource in data['resources']:
                for key in resource.keys():
                    if re.match(quarter_pattern, key) and key not in quarters:
                        quarters.append(key)
        
        # Sort quarters chronologically
        quarters.sort(key=lambda x: (x.split('-')[1], int(x.split('-')[0][1])))
        self.current_quarters = quarters
        return quarters

processor = QuarterlyDataProcessor()

@router.get("/dashboard-summary")
async def get_dashboard_summary():
    """Get summary data for main dashboard"""
    if not current_data:
        return {
            "total_resources": 0,
            "total_trials": 0,
            "therapeutic_areas": [],
            "quarters": [],
            "overall_utilization": 0
        }
    
    # Extract quarters from first resource
    quarters = processor.detect_quarter_columns(current_data)
    
    # Get unique therapeutic areas
    areas = []
    if current_data.get('resources'):
        areas = list(set(r.get('area', '') for r in current_data['resources']))
    
    # Calculate overall utilization
    total_supply = 0
    if current_data.get('resources'):
        for resource in current_data['resources']:
            for quarter in quarters:
                total_supply += resource.get(quarter, 0.0)
    
    total_demand = 0
    if current_data.get('trials'):
        total_demand = sum(t['subjects']/650.0 for t in current_data['trials'])
    
    utilization = (total_demand / total_supply * 100) if total_supply > 0 else 0
    
    return {
        "total_resources": len(current_data.get('resources', [])),
        "total_trials": len(current_data.get('trials', [])),
        "therapeutic_areas": areas,
        "quarters": sorted(quarters),
        "overall_utilization": round(utilization, 1)
    }

@router.post("/load-sample-data")
async def load_sample_data(data: dict):
    """Load sample data directly without file upload"""
    global current_data
    
    try:
        current_data = data
        
        return {
            "message": "Sample data loaded successfully",
            "resources_count": len(data.get('resources', [])),
            "trials_count": len(data.get('trials', []))
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing data: {str(e)}")

@router.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    """Upload and process quarterly data file"""
    global current_data
    
    logger.info(f"Received file upload: {file.filename}")
    
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        content = await file.read()
        data = json.loads(content.decode('utf-8'))
        
        # Validate required fields
        if 'resources' not in data or 'trials' not in data:
            raise HTTPException(status_code=400, detail="Missing required fields: 'resources' or 'trials'")
        
        current_data = data
        logger.info(f"Successfully loaded data with {len(data.get('resources', []))} resources")
        
        return {
            "message": "Data uploaded successfully",
            "resources_count": len(data.get('resources', [])),
            "trials_count": len(data.get('trials', []))
        }
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in uploaded file")
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
@router.get("/trials")
async def get_trials():
    """Get all clinical trials"""
    return current_data.get('trials', [])

@router.get("/resources")
async def get_resources():
    """Get all resources/people"""
    return current_data.get('resources', [])

@router.get("/quarters")
async def get_current_quarters():
    """Get current quarter columns"""
    if not current_data:
        return {"quarters": []}
    quarters = processor.detect_quarter_columns(current_data)
    return {"quarters": quarters}

@router.get("/bottlenecks")
async def get_bottlenecks():
    """Calculate and return bottleneck analysis"""
    if not current_data:
        raise HTTPException(status_code=404, detail="No data loaded")
    
    # Simple bottleneck calculation
    bottlenecks = []
    quarters = processor.detect_quarter_columns(current_data)
    
    # Group by therapeutic area
    areas = {}
    for resource in current_data.get('resources', []):
        area = resource.get('area', 'Unknown')
        if area not in areas:
            areas[area] = {'supply': {}, 'people': []}
        areas[area]['people'].append(resource)
        
        for quarter in quarters:
            if quarter not in areas[area]['supply']:
                areas[area]['supply'][quarter] = 0.0
            areas[area]['supply'][quarter] += resource.get(quarter, 0.0)
    
    # Calculate demand from trials
    trial_demand = {}
    for trial in current_data.get('trials', []):
        area = trial.get('area', 'Unknown')
        if area not in trial_demand:
            trial_demand[area] = 0.0
        trial_demand[area] += trial['subjects'] / 650.0  # FTE conversion
    
    for area, area_data in areas.items():
        for quarter in quarters:
            supply = area_data['supply'][quarter]
            demand = trial_demand.get(area, 0.0)
            ntsa = supply * 0.2  # Assume 20% for non-trial activities
            bottleneck_value = supply - ntsa - demand
            
            status = "balanced"
            if bottleneck_value < -0.2:
                status = "overloaded"
            elif bottleneck_value > 0.5:
                status = "underutilized"
            
            bottlenecks.append({
                'therapeutic_area': area,
                'quarter': quarter,
                'supply': supply,
                'demand': demand,
                'ntsa': ntsa,
                'bottleneck': bottleneck_value,
                'status': status
            })
            
    return {"bottlenecks": bottlenecks}