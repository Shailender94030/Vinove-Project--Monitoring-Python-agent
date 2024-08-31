import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
print("S3_BUCKET_NAME:", os.getenv('S3_BUCKET_NAME'))
print("AWS_REGION:", os.getenv('AWS_REGION'))
print("AWS_ACCESS_KEY_ID:", os.getenv('AWS_ACCESS_KEY_ID'))
print("AWS_SECRET_ACCESS_KEY:", os.getenv('AWS_SECRET_ACCESS_KEY'))
# AWS S3 Configuration
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Initialize the S3 client
s3 = boto3.client('s3',
                         region_name=AWS_REGION,
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def list_and_download_objects(bucket_name, download_dir):
    """List objects in an S3 bucket and download each object to the specified directory.

    :param bucket_name: string
    :param download_dir: string, local directory to download objects to
    """
   

    try:
        # Ensure the download directory exists
        os.makedirs(download_dir, exist_ok=True)

        # List objects in the specified S3 bucket
        response = s3.list_objects_v2(Bucket=bucket_name)

        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                download_path = os.path.join(download_dir, key)
               
                # Create any necessary directories for the object
                os.makedirs(os.path.dirname(download_path), exist_ok=True)
               
                # Download the object
                print(f"Downloading {key} to {download_path}...")
                s3.download_file(bucket_name, key, download_path)
                print(f"Successfully downloaded {key} to {download_path}.")
        else:
            print("No objects found in the bucket.")
    except NoCredentialsError:
        print("Error: No AWS credentials found.")
    except Exception as e:
        print(f"Client error: {e}")

if __name__ == "__main__":
    bucket_name = 'monitoring-agent-vinove'  # Replace with your bucket name
    download_dir = 'C:\\Users\\raghvendra.pandey\\p'
   
    list_and_download_objects(bucket_name, download_dir)