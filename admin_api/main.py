from fastapi import FastAPI, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import os
from damage import crud, schemas, models
from database import database
from datetime import datetime
import boto3

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

os.environ['AWS_ACCESS_KEY_ID'] = ''
os.environ['AWS_SECRET_ACCESS_KEY'] = ''

models.Base.metadata.create_all(bind=database.engine)

# 저장소 설정
s3_client = boto3.client('s3')
BUCKET_NAME = 'kebbucket'

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/maintenance-schedule")
async def create_schedule(
    image_id: int = Form(...),
    schedule_date: datetime = Form(...),
    details: str = Form(...),
    db: Session = Depends(database.get_db)
):
    schedule = schemas.MaintenanceScheduleCreate(schedule_date=schedule_date, details=details)
    db_schedule = crud.create_maintenance_schedule(db=db, schedule=schedule, image_id=image_id)
    return db_schedule

@app.get("/images/total")
async def get_total_images(db: Session = Depends(database.get_db)):
    total_images = crud.get_total_images(db=db)
    if total_images is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        # S3 버킷에서 모든 객체 가져오기
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' not in response:
            return {'total_images': total_images, 's3_images': []}

        # 모든 이미지 URL 생성
        image_urls = [
            f"https://{BUCKET_NAME}.s3.amazonaws.com/{item['Key']}"
            for item in response['Contents']
        ]
        return {'total_images': total_images, 's3_images': image_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching images from S3: {str(e)}")


@app.get("/images/{image_id}", response_model=schemas.Image)
async def get_image(image_id: int, db: Session = Depends(database.get_db)):
    image = crud.get_image(db=db, image_id=image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@app.get("/images/get/{image_id}")
async def get_image_file(image_id: int, db: Session = Depends(database.get_db)):
    image = crud.get_image(db=db, image_id=image_id)
    
    if image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    # S3에서 파일 가져오기
    try:
        s3_client.download_file(BUCKET_NAME, image.filename, f"/tmp/{image.filename}")
        file_path = f"/tmp/{image.filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching file from S3: {str(e)}")

    # 파일 반환
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)

@app.delete("/images/{image_id}")
async def delete_image(image_id: int, db: Session = Depends(database.get_db)):
    db_image = crud.get_image(db=db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")

    # S3에서 파일 삭제
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=db_image.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file from S3: {str(e)}")
    
    # 로컬 파일 삭제
    file_path = db_image.filepath
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 데이터베이스에서 이미지 정보 삭제
    db_image = crud.delete_image(db=db, image_id=image_id)
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return {"message" : "delete complete"}

@app.get("/imagesCount/totalCount")
async def get_total_images(db: Session = Depends(database.get_db)):
    count = crud.get_total_image_count(db=db)
    return {"count": count}