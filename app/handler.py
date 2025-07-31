# lambda-image-processor/app/handler.py
"""
handler.py
==========

AWS Lambda handler for image processing pipeline using Pillow and Boto3.

This script performs the following tasks when triggered by an S3 upload event:
---------------------------------------------------------------------------
1. Downloads the uploaded `.jpg` image from the source S3 bucket.
2. Resizes the image to 256x256 pixels using Pillow.
3. Uploads the resized image to a destination S3 bucket (`PROCESSED_BUCKET`).
4. Stores metadata (original and processed paths) in a DynamoDB table (`DDB_TABLE`).
5. Sends an optional SNS notification to a subscribed topic (`SNS_TOPIC_ARN`).

Environment Variables:
-----------------------
- `PROCESSED_BUCKET`: Target S3 bucket for storing resized images.
- `DDB_TABLE`: DynamoDB table name used for storing image metadata.
- `SNS_TOPIC_ARN`: Optional SNS topic ARN to notify upon successful image processing.

Key Functions:
--------------
- `resize_image(image_bytes)`: Resizes the image to 256x256 JPEG format.
- `lambda_handler(event, context)`: AWS Lambda entry point for processing S3 event records.

Note:
-----
- Handles individual record errors gracefully and continues processing.
- Image resizing is done entirely in-memory using `BytesIO` for performance.
- Logs are printed for observability and debugging via CloudWatch.

Author:
-------
Generated for the Lambda Image Processor project (Python, AWS Lambda, CDK).
"""

import os
import uuid
from PIL import Image
import boto3
from io import BytesIO

# Initialize AWS clients
s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

# Environment variables
PROCESSED_BUCKET = os.environ["PROCESSED_BUCKET"]
DDB_TABLE = os.environ["DDB_TABLE"]
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")

def resize_image(image_bytes):
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        print(f"[DEBUG] Original size: {img.size}")
        img = img.resize((256, 256))
        print(f"[DEBUG] Resized size: {img.size}")
        output = BytesIO()
        img.save(output, format="JPEG")
        output.seek(0)
        return output
    except Exception as e:
        print(f"[ERROR] Failed to resize image: {e}")
        return None

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(f"[INFO] Processing image: s3://{bucket}/{key}")

        try:
            obj = s3.get_object(Bucket=bucket, Key=key)
            image_data = obj['Body'].read()
        except Exception as e:
            print(f"[ERROR] Failed to read object from S3: {e}")
            continue

        resized_image = resize_image(image_data)
        if resized_image is None:
            continue

        new_key = f"resized-{uuid.uuid4().hex}.jpg"

        try:
            s3.upload_fileobj(
                resized_image,
                PROCESSED_BUCKET,
                new_key,
                ExtraArgs={"ContentType": "image/jpeg"}
            )
            print(f"[INFO] Uploaded resized image: s3://{PROCESSED_BUCKET}/{new_key}")
        except Exception as e:
            print(f"[ERROR] Failed to upload resized image: {e}")
            continue

        try:
            table = dynamodb.Table(DDB_TABLE)
            table.put_item(Item={
                "image_id": new_key,
                "original_bucket": bucket,
                "original_key": key,
                "processed_bucket": PROCESSED_BUCKET,
            })
            print(f"[INFO] Logged metadata in DynamoDB: {new_key}")
        except Exception as e:
            print(f"[ERROR] Failed to log metadata: {e}")

        try:
            response =sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="Image Processed",
                Message=f"Your image '{key}' has been resized and saved as '{new_key}'."
            )
            print(f"[INFO] SNS notification sent:", response)
        except Exception as e:
            print(f"[ERROR] Failed to publish to SNS: {e}")

    return {"status": "done"}
