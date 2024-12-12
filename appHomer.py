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
global DEVICE_NAME
DEVICE_NAME = "PLUTO"
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_hosID', methods=['GET'])
def get_all_hospital_ids():
    hospital_info = []  # List to store hospital info with ID and Status

    with open(pathCsv, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            hospital_id = row['HospitalID']
            status = row['Status']  # Assuming the status is in the CSV

            # You can apply any logic to determine the status if not already in the CSV
            # For example, if status is calculated based on some criteria, use that logic here
            # Example: status = "Done" if row['SomeCondition'] == "True" else "Undone"

            # Add HospitalID and Status to the hospital_info list
            hospital_info.append({
                'HospitalID': hospital_id,
                'Status': status
            })

    # Return the hospital IDs along with their statuses as a JSON response
    return jsonify({'hospital_info': hospital_info})

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
        print(config_file, session_file)
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
    


@app.route('/chart-data/<hospital_id>', methods=['GET'])
def get_chart_data(hospital_id):
    try:
        # Construct file paths
        config_file = os.path.join(path_r, hospital_id, DEVICE_NAME, "configdata.csv")
        ext_file = os.path.join(path_r, hospital_id, DEVICE_NAME, "extdata.csv")

        # Load CSV files
        ext_data = pd.read_csv(ext_file)
        config_data = pd.read_csv(config_file)

        # Parse dates using the correct format
        start_date = datetime.strptime(config_data['startdate'].iloc[-1], '%d-%m-%Y')
        end_date = datetime.strptime(config_data['end '].iloc[-1], '%d-%m-%Y')

        # Debugging: Print parsed dates
        print(f"Start Date: {start_date}, End Date: {end_date}")

        # Create a list of dates spanning the range specified in configdata.csv
        date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        # Convert the DateTime column to datetime in extdata.csv with the correct format
        ext_data['DateTime'] = pd.to_datetime(ext_data['DateTime'], format='%d-%m-%Y %H:%M:%S')
        ext_data['Date'] = ext_data['DateTime'].dt.date

        # Aggregate session durations by date
        session_duration_by_date = ext_data.groupby('Date')['MoveTime'].sum() / 60 
        print(session_duration_by_date)
        # Ensure all dates in date_range are included, even if they are missing in ext_data
        labels = [date.strftime('%Y-%m-%d') for date in date_range]
        line_data = [
            session_duration_by_date.get(date.date(), 0)  # Fill with 0 if date is missing
            for date in date_range
        ]
        print("lD :" ,line_data)
        # Prepare bubble data with session durations greater than 0
        bubble_data = [
            {"x": date.strftime('%Y-%m-%d'), "y": session_duration_by_date.get(date.date(), 0), "r": 10}
            for date in date_range  # Include all dates, even those with 0 session duration
        ]
        print(bubble_data)
        # Prepare chart data for response
        chart_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "Session Duration",
                    "data": line_data,
                    "borderColor": "blue",
                    "backgroundColor": "rgba(0, 0, 255, 0.1)",
                    "type": "line",
                    "fill": False,
                },
                {
                    "label": "Session Bubble",
                    "data": bubble_data,
                    "backgroundColor": "rgba(255, 0, 0, 0.6)",
                    "hoverBackgroundColor": "rgba(255, 0, 0, 0.8)",
                    "type": "bubble",
                }
            ]
        }
        
        
        return jsonify(chart_data)

    except FileNotFoundError as fnf_error:
        print(f"File not found: {fnf_error}")
        return jsonify({"error": "Configuration or data file missing."}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/fetch-mechanism-data/<hospital_id>/<selected_date>', methods=['GET'])
def fetch_mechanism_data(hospital_id, selected_date):
    try:
        # Construct the file path for the selected date
        print("Selected date:", selected_date)
        date_file = os.path.join(path_r, hospital_id, DEVICE_NAME, "Dates", f"{selected_date}.csv")
        print(DEVICE_NAME)
        # Load the CSV file for the selected date
        date_data = pd.read_csv(date_file)
        data = "Mechanism" if DEVICE_NAME == "PLUTO" else "Movement"
        print(data)
        # Group by Mechanism and sum GameDuration
        mechanism_duration = date_data.groupby("Mechanism" if DEVICE_NAME == "PLUTO" else "Movement")['GameDuration'].sum().reset_index()

        # Prepare data for frontend
        mechanisms = mechanism_duration["Mechanism" if DEVICE_NAME == "PLUTO" else "Movement"].tolist()
        durations = mechanism_duration['GameDuration'].tolist()

        # Static mechanism lists based on device type
        if DEVICE_NAME == "PLUTO":
            static_mechanisms = ["WFE", "WURD", "FPS", "HOC", "FME1", "FME2"]
        elif DEVICE_NAME == "MARS":
            static_mechanisms = ["SFE", "SABDU", "ELFE"]
        else:
            return jsonify({"error": "Invalid device type"}), 400

        # Ensure all mechanisms (PLUTO/MARS) are present, even if they don't exist in the data (fill with 0 if necessary)
        final_mechanisms = static_mechanisms
        final_durations = [durations[mechanisms.index(mechanism)] if mechanism in mechanisms else 0 for mechanism in static_mechanisms]

        # Prepare chart data
        chart_datax = {
            'mechanisms': final_mechanisms,
            'durations': final_durations
        }
        print(chart_datax)
        return jsonify(chart_datax)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/fetch-session-data/<hospital_id>/<selected_date>', methods=['GET'])
def fetch_session_data(hospital_id, selected_date):
    try:
        # Construct the file path for the selected date
        date_file = os.path.join(path_r, hospital_id, DEVICE_NAME, "Dates", f"{selected_date}.csv")
        date_data = pd.read_csv(date_file)

        # Group by SessionNumber and Mechanism, summing the GameDuration
        session_data = date_data.groupby(['SessionNumber', "Mechanism" if DEVICE_NAME == "PLUTO" else "Movement"])['GameDuration'].sum().reset_index()

        # Structure the data for each session
        sessions = []
        for session_number in session_data['SessionNumber'].unique():
            session_df = session_data[session_data['SessionNumber'] == session_number]
            sessions.append({
                "SessionNumber": int(session_number),
                "Mechanisms": session_df["Mechanism" if DEVICE_NAME == "PLUTO" else "Movement"].tolist(),
                "GameDurations": session_df['GameDuration'].astype(int).tolist()
            })

        return jsonify({"sessions": sessions})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)