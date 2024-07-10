from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from PIL import Image
import io
import os
from typing import List
from damage import crud, models, schemas
from database import database

app = FastAPI(
    title="KEB Project",
    description="API for Project Mobile App",
    version="1.0.0",
    contact={
        "name": "suman Oh",
        "email": "a000626@naver.com",
    },
    docs_url="/v1/docs",
    redoc_url="/v1/redoc",
    openapi_url="/v1/openapi.json",
)

# 데이터베이스 초기화
models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload", response_model=schemas.Image)
async def upload_image(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    x: int = Form(...),  # 자르기 시작 지점의 x 좌표
    y: int = Form(...),  # 자르기 시작 지점의 y 좌표
    width: int = Form(...),  # 자를 이미지의 너비
    height: int = Form(...),  # 자를 이미지의 높이
    db: Session = Depends(database.get_db)
):
    # 이미지 파일을 열기
    image = Image.open(io.BytesIO(await file.read()))
    
    # 이미지 자르기
    cropped_image = image.crop((x, y, x + width, y + height))
    
    # 자른 이미지를 저장할 경로
    file_location = f"uploads/cropped_{file.filename}"
    cropped_image.save(file_location)
    
    # 데이터베이스에 이미지 정보 저장
    segmentation_result = "segmentation_result_placeholder"
    db_image = crud.create_image(db=db, filename=file.filename, filepath=file_location, segmentation_result=segmentation_result)
    
    gps = schemas.GPSCreate(latitude=latitude, longitude=longitude)
    db_gps = crud.create_gps(db=db, gps=gps, image_id=db_image.id)
    
    return {"message": "complete"}

@app.get("/images/{image_id}", response_model=schemas.Image)
async def get_image(image_id: int, db: Session = Depends(database.get_db)):
    image = crud.get_image(db=db, image_id=image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@app.get("/images/{image_id}/file")
async def get_image_file(image_id: int, db: Session = Depends(database.get_db)):
    image = crud.get_image(db=db, image_id=image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = image.filepath
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)