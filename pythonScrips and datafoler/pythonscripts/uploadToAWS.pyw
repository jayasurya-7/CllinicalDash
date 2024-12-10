import boto3
import csv
import logging
import os
from botocore.exceptions import NoCredentialsError
from datetime import datetime
import shutil

# AWS Configuration
bucketName = 'homer-data'
userName = "Gokul"
deviceName = "MarsData"

# Paths
keysFilePath = "C:/homer_accessKeys.csv"
gameAssertPath = "D:/MARS-HOMER/Assets"
awsLogFilePath = f"{gameAssertPath}/awsUploaderLog.txt"
dataFolderPath = f"{gameAssertPath}/data"
uploadStatusFile =f"{gameAssertPath}/uploadStatus.txt"
awsConfigFilePath = f"{userName}/{deviceName}/configdata.csv"  
localConfigFilePath = f"{gameAssertPath}/data/configdata.csv"
with open(localConfigFilePath)as file:
    csvreader = csv.reader(file)
    for row in csvreader:
        lastrow = row
    userName = f"{lastrow[2]}"
    print(userName)
def initializeLogging():
    logging.basicConfig(
        filename=awsLogFilePath,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def loadAwsKeys(keysFilePath):
    try:
        with open(keysFilePath, mode='r') as file:
            csvReader = csv.reader(file)
            for rows in csvReader:
                keys = rows
            return keys[0], keys[1] 
    except FileNotFoundError:
        logging.error(f"Keys file not found")
       
    except Exception as e:
        logging.error(f"Error reading keys file")
       
def readUploadStatus(statusFilePath):
    if os.path.exists(statusFilePath):
        with open(statusFilePath, mode="r") as file:
            return file.read().strip()
    else:
        logging.error(f"Upload status file not found")

def updateUploadStatus(statusFilePath, newStatus):
    try:
        with open(statusFilePath, mode="w") as file:
            file.write(newStatus)
    except Exception as e:
        logging.error(f"Failed to update upload status")
       
def uploadToAws(filePath, bucketName, objectName, accessKey, secretKey):
    try:
        uploader = boto3.client(
            's3',
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey
        )
        uploader.upload_file(filePath, bucketName, objectName)
        logging.info(f"Successfully uploaded: {filePath} to {objectName}")
    except FileNotFoundError:
        logging.error(f"File not found")
    except NoCredentialsError:
        logging.error("AWS credentials not available")
    except Exception as e:
        logging.error(f"Failed to upload")

def downloadConfigFile(bucketName,accessKey, secretKey):
    download = boto3.client(
            's3',
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey
        )
    tempFilePath = "tempDownloadedFile.csv"

    try:
        logging.info("downloading configFile form aws s3")
        download.download_file(bucketName, awsConfigFilePath, tempFilePath)
        shutil.copy2(localConfigFilePath, tempFilePath)
        logging.info("ConfigFile updated succesfully")
      
    except Exception as e:
        logging.error(f"An error occurred: {e}")
      
#To get all file from the folder
def uploadFolderToS3(dataFolderPath, bucketName, accessKey, secretKey):
    currentDatetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix = f"{userName}/{deviceName}/{currentDatetime}/"
    for root, dir, files in os.walk(dataFolderPath):
        if "applog" in dir:
            dir.remove("applog")
        for file in files:
            if file.endswith('.meta'):
                continue
            if "configdata.csv" in files:
                localFilePath = os.path.join(root, file)
                s3ObjectName = f"{userName}/{deviceName}/" + os.path.relpath(localFilePath, dataFolderPath)
                uploadToAws(localFilePath, bucketName, s3ObjectName, accessKey, secretKey)
                continue
            localFilePath = os.path.join(root, file)
            s3ObjectName = prefix + os.path.relpath(localFilePath, dataFolderPath)
            uploadToAws(localFilePath, bucketName, s3ObjectName, accessKey, secretKey)

   
def main():
    try:
        initializeLogging()
        logging.info("Script started")

        # Load AWS credentials
        accessKey, secretKey = loadAwsKeys(keysFilePath)
        # Check upload status
        downloadConfigFile(bucketName,accessKey,secretKey)
        status = readUploadStatus(uploadStatusFile)
        if status == "upload_needed":
            logging.info("Upload required. Starting upload process...")
            uploadFolderToS3(dataFolderPath, bucketName, accessKey, secretKey)
            updateUploadStatus(uploadStatusFile, "no_upload")
            logging.info("Upload process completed and status updated.")
        else:
            logging.info("No upload needed. Exiting script.")

    except Exception as e:
        logging.error("An error occurred")

if __name__ == "__main__":
    main()
