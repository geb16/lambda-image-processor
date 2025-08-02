# AWS Lambda Image Processor (Python + CDK)

This serverless application automatically resizes `.jpg` images uploaded to an S3 bucket. It saves the resized images to another `S3 bucket`, `logs` `metadata` to `DynamoDB`, and sends an email notification using Amazon `SNS`.

---

## Features

-  **S3 Trigger**: Automatically processes `.jpg` uploads
-  **Image Resizing**: Converts image to 256x256 using [Pillow](https://python-pillow.org)
-  **DynamoDB Logging**: Stores metadata of original + resized images
-  **SNS Notification**: Sends email alert after each processed image
-  **Deployable with AWS CDK V2**

---

## 📁 Project Structure

```text
lambda-image-processor/
│
├── app/                          # Lambda Function code
│   ├── __init__.py
│   └── handler.py                # Main Lambda logic
│
├── lambda_image_processor/      # CDK resources: S3, Lambda, DynamoDB, SNS
│   ├── __init__.py
│   └── lambda_image_processor_stack.py
│
├── tests/
│   └── test_handler.py          # Local unit test for image processor
│
├── cdk.json
├── requirements.txt
├── app.py                        # CDK App Entrypoint
├── setup.py                      
├── README.md
└── LICENSE                       # MIT License
```
---
## Deployment Instructions
### 1. Install Dependencies

#### Create and activate a virtual environment
```python
python3 -m venv .venv
source .venv/bin/activate        # In Windows: .venv\Scripts\activate
```

#### Install CDK and dependencies
```python
pip install -r requirements.txt
```

### 2. Bootstrap CDK
   * Only required on first deploy per AWS environment:
```python
cdk bootstrap aws://YOUR_ACCOUNT_ID/YOUR_REGION
```
##### Example: `cdk bootstrap aws://123456789012/eu-west-2`

### 3. Deploy the Stack

```python
cdk deploy
```
   -  After deployment, check your email and confirm the SNS subscription to receive notifications.

### 4. Uploading Images
Upload .jpg images to the upload bucket (name printed in `cdk deploy output`). The Lambda function will:

   - Resize to 256x256
   - Upload to processed bucket
   - Store metadata in DynamoDB
   - Send SNS email notification

### 5. Testing the Lambda
In AWS Lambda Console:
   1. Go to the deployed Lambda function
   2. Create a test event with the following sample S3 trigger event:
      
   
   ```json
      {
      "Records": [
         {
            "s3": {
            "bucket": {
               "name": "your-upload-bucket"
            },
            "object": {
               "key": "sample.jpg"
            }
            }
         }
      ]
      }

```

### 6. Tech Stack
   - Language: Python 3.12+
   - IaC: AWS CDK v2
   - Storage: Amazon S3
   - Compute: AWS Lambda
   - Database: Amazon DynamoDB
   - Notification: Amazon SNS

### 7. Environment Variables (Auto-injected by CDK)
   - `PROCESSED_BUCKET`
   - `DDB_TABLE`
   - `SNS_TOPIC_ARN`

### 8. Future Improvements
   - Add presigned URL support for uploads
   - Automatically archive original images after post-processing
   - Add CloudWatch dashboards for monitoring
   - Enable multi-region failover for resilience

### 9. .gitignore
.gitignore is provided in [.gitignore](https://github.com/geb16/lambda-image-processor/blob/main/.gitignore)
### License
Please refer to [License](https://github.com/geb16/lambda-image-processor/blob/main/LICENSE)

