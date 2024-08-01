from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class GPSBase(BaseModel):
    latitude: float
    longitude: float

class GPS(GPSBase):
    id: int
    image_id: int

    class Config:
        from_attributes = True

class ImageBase(BaseModel):
    filename: str
    filepath: str
    segmentation_result: str

class Image(ImageBase):
    id: int
    uploaded_at: datetime
    gps: Optional[List[GPS]]

class Config:
    from_attributes = True


class MaintenanceScheduleBase(BaseModel):
    schedule_date: datetime
    details: str

class MaintenanceScheduleCreate(MaintenanceScheduleBase):
    pass

class MaintenanceSchedule(MaintenanceScheduleBase):
    id: int
    image_id: int

    class Config:
        from_attributes = True