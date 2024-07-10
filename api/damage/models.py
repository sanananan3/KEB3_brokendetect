from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    filepath = Column(String(255), index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow())
    segmentation_result = Column(String(255), index=True)

    gps = relationship("GPS", back_populates="image")

class GPS(Base):
    __tablename__ = 'gps'

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
    image_id = Column(Integer, ForeignKey('images.id'))

    image = relationship("Image", back_populates="gps")
