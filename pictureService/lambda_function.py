import os
import boto3
from PIL import Image
from io import BytesIO

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Triggered by S3 event. For each newly added image:
      1) Download from S3
      2) Resize or compress
      3) Overwrite the same object with the compressed version
    """
    try:
        # 1) Parse S3 event
        records = event['Records']
        for record in records:
            # S3 info
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']

            # 2) Download the image from S3 to memory
            original_obj = s3_client.get_object(Bucket=bucket, Key=key)
            img_data = original_obj['Body'].read()

            # 3) Open the image with PIL
            # (Ensure your Lambda includes Pillow or use a layer that has it)
            img = Image.open(BytesIO(img_data))

            # 4) Optionally compress or resize
            # e.g., let's resize it to max width=800 while preserving aspect ratio
            img.thumbnail((800, 800))

            # 5) Convert back to bytes (JPEG compression, e.g. quality=75)
            compressed_buffer = BytesIO()
            img.save(compressed_buffer, format="JPEG", optimize=True, quality=75)
            compressed_buffer.seek(0)

            # 6) Overwrite the same object in S3
            s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=compressed_buffer,
                ContentType='image/jpeg'
            )

            print(f"[SUCCESS] Compressed {key} in {bucket}")
        
        return {"statusCode": 200, "body": "Images compressed successfully."}

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return {"statusCode": 500, "body": str(e)}

