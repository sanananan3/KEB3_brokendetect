from fastapi import FastAPI, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session
import io
import os
from damage import crud, schemas, models
from database import database
import uuid
import boto3
from PIL import Image

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

    # S3 설정
    s3_client = boto3.client('s3')
    BUCKET_NAME = 'kebbucket'

    try:
        # 이미지 파일을 읽기
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # 좌표에 맞게 크롭 (예시: (left, upper, right, lower))
        # 좌표에 맞게 크롭하는 로직을 추가해야 합니다.
        # 예를 들어, (x1, y1, x2, y2)로 지정된 영역으로 크롭
        x1, y1, x2, y2 = 100, 100, 400, 400  # 크롭할 영역의 좌표
        cropped_image = image.crop((x1, y1, x2, y2))

        # 리사이즈 (예시: 256x256으로 리사이즈)
        resized_image = cropped_image.resize((256, 256))

        # 파일 이름 설정
        filename = f"{str(uuid.uuid4())}.jpg"
        
        # 이미지 데이터를 메모리 버퍼에 저장
        buffer = io.BytesIO()
        resized_image.save(buffer, format="JPEG")
        buffer.seek(0)

        # S3에 이미지 저장
        s3_client.put_object(Bucket=BUCKET_NAME, Key=filename, Body=buffer)

        # DB에 이미지 저장
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
        db_image = crud.create_image(db=db, filename=filename, filepath=s3_url, segmentation_result=segmentation_result)

        gps = schemas.GPSCreate(latitude=latitude, longitude=longitude)
        db_gps = crud.create_gps(db=db, gps=gps, image_id=db_image.id)

        return {"image id": db_image.id}
    except Exception as e:
        return {"error": str(e)}
