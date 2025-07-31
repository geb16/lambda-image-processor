# lambda_image_processor/lambda_image_processor_stack.py
"""
LambdaImageProcessorStack
==========================

This AWS CDK stack defines a serverless image processing pipeline using Python.

Key Components:
---------------
- **S3 Upload Bucket**: Triggers the pipeline on `.jpg` file upload.
- **S3 Processed Bucket**: Stores resized image outputs.
- **AWS Lambda Function**: Resizes uploaded images to 256x256 using Pillow.
- **DynamoDB Table**: Logs metadata about original and processed images.
- **SNS Topic**: Sends email notifications after successful processing.

Functionality:
--------------
When a `.jpg` file is uploaded to the **Upload Bucket**, it triggers the Lambda function which:
1. Resizes the image.
2. Stores it in the **Processed Bucket**.
3. Logs metadata to **DynamoDB**.
4. Publishes a notification to **SNS**.

The Pillow dependency is included via a Lambda layer. CDK resources are configured with automatic cleanup on stack deletion via `RemovalPolicy.DESTROY`.

Environment variables are injected into the Lambda to enable access to other services:
- `PROCESSED_BUCKET`
- `DDB_TABLE`
- `SNS_TOPIC_ARN`

Note:
-----
- Make sure to replace the SNS subscription email (`sample@example.com`) with a verified address.
- Adjust the Lambda layer ARN to match your AWS region and Python version.

Author:
-------
Generated for the AWS Lambda Image Processor project (Python + CDK).
"""

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_iam as iam,
    aws_s3_notifications as s3n,
    Duration,
    RemovalPolicy
)
from constructs import Construct
import os



class LambdaImageProcessorStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Upload Bucket (Trigger Source)
        upload_bucket = s3.Bucket(
            self, "UploadBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Processed Output Bucket
        processed_bucket = s3.Bucket(
            self, "ProcessedBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # DynamoDB Table for Metadata
        metadata_table = dynamodb.Table(
            self,
            "ImageMetadata",
            partition_key=dynamodb.Attribute(
                name="image_id", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        # SNS Topic for Notifications
        sns_topic = sns.Topic(self, "ImageProcessedTopic")

        pillow_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "PillowLayer",
            "arn:aws:lambda:eu-west-2:770693421928:layer:Klayers-p312-pillow:2"   # Adjust the ARN based on your region and Python version
        )

        # Lambda Function
        lambda_fn = _lambda.Function(
            self,
            "ImageProcessorFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            architecture=_lambda.Architecture.X86_64,  # or .ARM_64 depending on code
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("app"),
            layers=[pillow_layer],
            environment={
                "PROCESSED_BUCKET": processed_bucket.bucket_name,
                "DDB_TABLE": metadata_table.table_name,
                "SNS_TOPIC_ARN": sns_topic.topic_arn,
            },
            timeout=Duration.seconds(10),
        )

        # Permissions
        upload_bucket.grant_read(lambda_fn)
        processed_bucket.grant_write(lambda_fn)
        metadata_table.grant_write_data(lambda_fn)
        sns_topic.grant_publish(lambda_fn)

        # SNS Email Subscription
        sns_topic.add_subscription(
            subs.EmailSubscription("sample@example.com") # Replace with your email address
        )


        # Setup S3 to Lambda Notification
        notification = s3n.LambdaDestination(lambda_fn)
        upload_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            notification,
            s3.NotificationKeyFilter(suffix=".jpg")  # Optional: restrict to images
        )

        # Allow S3 to Invoke Lambda
        lambda_fn.add_permission(
            "AllowS3Invoke",
            principal=iam.ServicePrincipal("s3.amazonaws.com"),
            source_arn=upload_bucket.bucket_arn,
            source_account=self.account
        )
