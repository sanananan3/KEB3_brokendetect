from sqlalchemy.orm import Session
from damage import models, schemas

def create_image(db: Session, filename: str, filepath: str, segmentation_result: str):
    db_image = models.Image(filename=filename, filepath=filepath, segmentation_result=segmentation_result)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def create_gps(db: Session, gps: schemas.GPSCreate, image_id: int):
    db_gps = models.GPS(**gps.dict(), image_id=image_id)
    db.add(db_gps)
    db.commit()
    db.refresh(db_gps)
    return db_gps

def get_images(db: Session) -> list[models.Image]:
    return db.query(models.Image).all()

def get_image(db: Session, image_id: int) -> models.Image:
    return db.query(models.Image).filter(models.Image.id == image_id).first()