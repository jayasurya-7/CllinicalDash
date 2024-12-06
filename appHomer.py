from flask import Flask, render_template, request, jsonify
import csv
import os
import json
import pandas as pd
from datetime import datetime, timedelta

path_r= 'D:\\Data2\\HomerDataManipulation'
pathCsv= os.path.join(path_r, "userDetails.csv")
app = Flask(__name__)

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

@app.route('/get_hospital_details/<hospital_id>', methods=['GET'])
def get_hospital_details(hospital_id):
    try:
        config_file = os.path.join(path_r, hospital_id, "configdata.csv")
        session_file = os.path.join(path_r, hospital_id, "Sessions.csv")
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

if __name__ == '__main__':
    app.run(debug=True)