#!/usr/bin/env python3
# lambda-image-processor/app.py

"""
Entry point for the AWS CDK application.

This script initializes and synthesizes the `LambdaImageProcessorStackV1`, which provisions
a serverless image processing pipeline using AWS Lambda, S3, DynamoDB, and SNS.

Environment:
- CDK_DEFAULT_ACCOUNT: AWS account ID (automatically picked from the AWS CLI context)
- CDK_DEFAULT_REGION: AWS region where the stack will be deployed

Usage:
    Run `cdk deploy` after this script to deploy the synthesized stack to AWS.
"""
import os
import aws_cdk as cdk
from lambda_image_processor.lambda_image_processor_stack import LambdaImageProcessorStack

app = cdk.App()

# Best practice: Use explicit environment from current CLI credentials
LambdaImageProcessorStack(
    app,
    "LambdaImageProcessorStackV1",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION"),
    ),
)

app.synth()
