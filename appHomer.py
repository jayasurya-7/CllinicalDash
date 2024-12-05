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

if __name__ == '__main__':
    app.run(debug=True)