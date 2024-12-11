from flask import Flask, render_template, request, jsonify
import csv
import os
import json
import pandas as pd
from datetime import datetime, timedelta
import boto3

bucketName = 'homer-data'
keysFilePath = "C:/homer_accessKeys.csv"
path_r= "C:\\Homer-Data"
pathCsv= os.path.join(path_r, "PlutoUserDetails.csv")
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_userId', methods=['POST'])
def get_hospital_ids():
    hospital_info = []  # List to store hospital info with ID and Status
    device_name = request.form["search_term"]
    global DEVICE_NAME
    DEVICE_NAME = device_name
    pathCsv= os.path.join(path_r, device_name.lower()+"UserDetails.csv")
    with open(pathCsv, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            hospital_id = row['HospitalID']
            status = row['Status']  
            hospital_info.append({
                'HospitalID': hospital_id,
                'Status': status
            })
    return jsonify({'hospital_info': hospital_info})

@app.route('/get_user_data', methods=['POST'])
def getUserData():
    user_name = request.form.get('Name')
    device_name = request.form.get('devicename')
    if not user_name or not device_name:
        return jsonify({"status": "error", "message": "Name or device name parameter is missing"}), 400

    # Construct the file path safely
   
    file_path = os.path.join(path_r, user_name, device_name, "configdata.csv")
    
    if not os.path.exists(file_path):
        return jsonify({"status": "error", "message": "CSV file not found"}), 404

    if user_name:
        try:
            header = []
            last_row = []
            with open(file_path, "r") as file:
                csvreader = csv.reader(file)
                header = next(csvreader) 
                for row in csvreader:
                    last_row = row    
            response = {
                "status": "success",
                "message": f"Data received for user {user_name}",
                "data": {
                    "header": header,
                    "last_row": last_row
                }
            }
            return jsonify(response), 200  # Return JSON response with HTTP 200
        except Exception as e:
            print(f"Error processing CSV file: {e}")
            return jsonify({"status": "error", "message": "Failed to process CSV file"}), 500
    else:
        return jsonify({"status": "error", "message": "Name parameter is missing"}), 400
    
@app.route('/update_data_in_aws', methods=['POST'])
def uploadUpdatedData(): 
    data = request.form.getlist('updatedData[]')
    user_name = request.form.get('userName')
    device_name = request.form.get('deviceName')
    print(device_name)
    file_path = os.path.join(path_r, user_name, device_name, "configdata.csv")
    if device_name == "MARS":
        device_name = "MarsData"
    else:
        device_name = "plutoData"
    objectname = f"{user_name}/{device_name}/configdata.csv" 
    accessKey,secretKey = loadAwsKeys(keysFilePath)
    data_list = list(data)
    try:
        uploadToAws(file_path, bucketName, objectname, accessKey, secretKey, data_list)
        response = {
            "status": "success",
            "message": "Data uploaded successfully to AWS."
        }
        return jsonify(response), 200 

    except Exception as e:
        response = {
            "status": "error",
            "message": f"Failed to upload data to AWS. Error: {str(e)}"
        }
        return jsonify(response), 500 
    

def uploadToAws(filePath,bucketName, objectName, accessKey, secretKey, data):
    try:
        with open(filePath, "a", newline="",encoding="utf-8") as file:
           csvwriter = csv.writer(file)
           csvwriter.writerow(data)
        uploader = boto3.client(
            's3',
            aws_access_key_id=accessKey,
            aws_secret_access_key=secretKey
        )
        uploader.upload_file(filePath, bucketName, objectName)
        print(f"Successfully uploaded: {filePath} to {objectName}")
    except FileNotFoundError:
        print(f"File not found")
    except Exception as e:
        print(f"Failed to upload{e}")

def loadAwsKeys(keysFilePath):
    try:
        with open(keysFilePath, mode='r') as file:
            csvReader = csv.reader(file)
            for rows in csvReader:
                keys = rows
            return keys[0], keys[1] 
    except FileNotFoundError:
        # logging.error(f"Keys file not found")
       print("file not found")
    except Exception as e:
        # logging.error(f"Error reading keys file")
       print("error reading keys file")

@app.route('/get_hospital_details/<hospital_id>', methods=['GET'])
def get_hospital_details(hospital_id):
    try:
        config_file = os.path.join(path_r, hospital_id,DEVICE_NAME , "configdata.csv")
        session_file = os.path.join(path_r, hospital_id,DEVICE_NAME, "session.csv")
        if not os.path.exists(config_file) or not os.path.exists(session_file):
            return jsonify({"error": "Data not found for the given Hospital ID"}), 404

        # Load config data
        config_df = pd.read_csv(config_file)
        if config_df.empty:
            return jsonify({"error": "Config data is empty"}), 404

        start_date = pd.to_datetime(config_df.iloc[-1]["startdate"], format="%d-%m-%Y")
        end_date = pd.to_datetime(config_df.iloc[-1]["end "], format="%d-%m-%Y")
        total_days = (end_date - start_date).days + 1

        # Load session data
        session_df = pd.read_csv(session_file)
        session_df["DateTime"] = pd.to_datetime(session_df["DateTime"], format="%d-%m-%Y %H:%M:%S")
        total_usage_days = session_df["DateTime"].dt.date.nunique()
        session_df = session_df[(session_df["DateTime"].dt.date >= start_date.date()) &
                                    (session_df["DateTime"].dt.date <= end_date.date())]
        # Calculate unique usage days within the range
        usage_days = session_df["DateTime"].dt.date.nunique() 
        return jsonify({
            "start_date": start_date.strftime("%d-%m-%Y"),
            "end_date": end_date.strftime("%d-%m-%Y"),
            "total_days": total_days,
            "usage_days": usage_days,
            "total_usage_days":total_usage_days
        })
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)