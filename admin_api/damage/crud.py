from sqlalchemy.orm import Session
from damage import models, schemas

def get_images(db: Session) -> list[models.Image]:
    return db.query(models.Image).all()

def get_image(db: Session, image_id: int) -> models.Image:
    return db.query(models.Image).filter(models.Image.id == image_id).first()

def delete_image(db: Session, image_id: int):
    db_image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if db_image:
        db.delete(db_image)
        db.commit()
    return db_image

def get_total_images(db: Session):
    return db.query(models.Image).all()

def get_total_image_count(db: Session):
    return db.query(models.Image).count()


def create_maintenance_schedule(db: Session, schedule: schemas.MaintenanceScheduleCreate, image_id: int):
    db_schedule = models.MaintenanceSchedule(**schedule.dict(), image_id=image_id)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule