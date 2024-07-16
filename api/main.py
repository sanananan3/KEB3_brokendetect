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

# 업로드 디렉토리 경로 설정
UPLOAD_DIRECTORY = "/app/uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    segmentation_result: str = Form(...),
    db: Session = Depends(database.get_db)
):
     # 이미지 파일을 열기
    image = Image.open(io.BytesIO(await file.read()))
    
    # 이미지를 저장할 경로
    file_location = os.path.join(UPLOAD_DIRECTORY, f"original_{file.filename}")
    image.save(file_location)

    # 추가적인 모델을 활용한 분류
    
    # 데이터베이스에 이미지 정보 저장
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


@app.delete("/images/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(database.get_db)):
    db_image = crud.get_image(db=db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    file_path = db_image.filepath
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db_image = crud.delete_image(db=db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return {"message" : "delete complete"}

@app.get("/imagesCount/totalCount")
async def get_total_images(db: Session = Depends(database.get_db)):
    count = crud.get_total_images(db=db)
    return {"count": count}