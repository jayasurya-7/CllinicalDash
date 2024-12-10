import boto3
import os

# AWS S3 setup
bucket_name = "homer-data"
key = "MarsData/Gokul/configdata.csv"  # S3 object key (file path in the bucket)
local_file_path = "D:/MARS-HOMER/Assets/data/configdata.csv"  # Path to your local file to upload

def download_and_rewrite_s3_file():
    # Initialize S3 client
  

    # Temporary download file path
    temp_file_path = "temp_downloaded_file.csv"

    try:
        # Step 1: Download the file from S3
        print("Downloading file from S3...")
        s3_client.download_file(bucket_name, key, temp_file_path)
        print(f"File downloaded to {temp_file_path}")

        # Step 2: Replace the downloaded file with the local file
        print(f"Replacing with local file: {local_file_path}")
        os.replace(local_file_path, temp_file_path)

        # Step 3: Upload the updated file back to S3
        print("Uploading updated file to S3...")
        s3_client.upload_file(temp_file_path, bucket_name, key)
        print("File uploaded successfully.")

        # Step 4: Clean up temporary file
        os.remove(temp_file_path)
        print("Temporary file removed.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
download_and_rewrite_s3_file()
