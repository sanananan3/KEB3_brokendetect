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

        # 크롭할 영역의 좌표 정의 (예시)
        crop_areas = [
            (50, 50, 200, 200),  # 첫 번째 크롭 영역
            (250, 250, 400, 400),  # 두 번째 크롭 영역
            (100, 100, 300, 300)   # 세 번째 크롭 영역
        ]

        image_ids = []  # 저장된 이미지 ID를 위한 리스트

        for idx, area in enumerate(crop_areas):
            # 크롭 및 리사이즈
            cropped_image = image.crop(area)
            resized_image = cropped_image.resize((256, 256))

            # 파일 이름 설정
            filename = f"{str(uuid.uuid4())}_{idx}.jpg"
            
            # 이미지 데이터를 메모리 버퍼에 저장
            buffer = io.BytesIO()
            resized_image.save(buffer, format="JPEG")
            buffer.seek(0)

            # S3에 이미지 저장
            s3_client.put_object(Bucket=BUCKET_NAME, Key=filename, Body=buffer)

            # DB에 이미지 저장
            s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
            db_image = crud.create_image(db=db, filename=filename, filepath=s3_url, segmentation_result=segmentation_result)
            image_ids.append(db_image.id)

        return {"image ids": image_ids}
    except Exception as e:
        return {"error": str(e)}
