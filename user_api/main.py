from fastapi import FastAPI, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
import io
import os
from damage import crud, schemas, models
from database import database
import uuid
import boto3

app = FastAPI(
    title="KEB Project",
    description="user API for Project Web App",
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

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    segmentation_result: str = Form(...),
    db: Session = Depends(database.get_db)):

    print("Error")

    # 저장소 설정
    s3_client = boto3.client('s3')
    BUCKET_NAME = 'kebbucket'

    try:
        # 이미지 파일을 읽기
        image = await file.read()
        filename = f"{str(uuid.uuid4())}.jpg"
        #s3공용 저장소에 이미지 저장
        s3_client.put_object(Bucket=BUCKET_NAME, Key=filename, Body=image)
        
        #db에 이미지 저장
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
        db_image = crud.create_image(db=db, filename=filename, filepath=s3_url, segmentation_result="segmentation_result")

        gps = schemas.GPSCreate(latitude=latitude, longitude=longitude)
        db_gps = crud.create_gps(db=db, gps=gps, image_id=db_image.id)

        return {"image id" : db_image.id}
    except Exception as e:
        return {"error": str(e)}
    