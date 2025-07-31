# lambda-image-processor/tests/test_handler.py

import os

# Set required env vars to dummy values for testing
os.environ["PROCESSED_BUCKET"] = "dummy-bucket"
os.environ["DDB_TABLE"] = "dummy-table"
os.environ["SNS_TOPIC_ARN"] = "dummy-topic-arn"

import sys
from io import BytesIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.handler import resize_image

def test_resize_image():
    test_image_path = "F:\\Users\\sample.jpg" # Replace with your actual test image path
    # Or better, use a relative path to your repo test data:
    # test_image_path = os.path.join(os.path.dirname(__file__), "data", "sample.jpg") # Adjust as needed with your test data directory

    with open(test_image_path, "rb") as img:
        image_bytes = img.read()
    
    resized = resize_image(image_bytes)
    
    assert resized is not None, "resize_image returned None"
    assert isinstance(resized, BytesIO), "resize_image did not return a BytesIO object"
    
    # Move pointer to start before reading
    resized.seek(0)
    resized_bytes = resized.read()
    assert isinstance(resized_bytes, bytes), "Resized output is not bytes"
    assert len(resized_bytes) > 0, "Resized output is empty"
