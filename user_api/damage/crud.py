from sqlalchemy.orm import Session
from damage import models, schemas
from fastapi import HTTPException

def create_image(db: Session, filename: str, filepath: str, segmentation_result: str):
    try:
        db_image = models.Image(filename=filename, filepath=filepath, segmentation_result=segmentation_result)
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        return db_image
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def create_gps(db: Session, gps: schemas.GPSCreate, image_id: int):
    try:
        db_gps = models.GPS(**gps.dict(), image_id=image_id)
        db.add(db_gps)
        db.commit()
        db.refresh(db_gps)
        return db_gps
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

