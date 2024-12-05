
from flask import Flask, render_template, request, jsonify
import csv
import os
import json
import pandas as pd
from datetime import datetime, timedelta

path_r= 'D:/DEMO/DESTINATION'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    search_term = request.form['search_term']
    suggestions = []

    with open('D:/DEMO/DESTINATION/patients.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if search_term.lower() in row['uniqueid'].lower():
                suggestions.append({'UniCode': row['uniqueid'], 'Name': row['name']})

    return jsonify({'suggestions': suggestions})



@app.route('/get_json_data', methods=['POST'])
def get_json_data():
    unicode_code = request.form['unicode']
    print(unicode_code)
    json_path = os.path.join(path_r, unicode_code, unicode_code + '.json') 
    
    json_data = []

    print("JSON Path:", json_path)
    if os.path.exists(json_path):
        print("File exists")
        with open(json_path, 'r') as json_file:
            print("File opened successfully")
            json_data.append(json.load(json_file))
            print(json_data)  
    else:
        print("File does not exist")

    return jsonify({'json_data': json_data})

@app.route('/get_individual_dates', methods=['POST'])
def get_individual_dates():
    unicode_code = request.form['unicode']
    device = request.form['device']
    unicode_path = os.path.join(path_r, unicode_code, device) 

    individual_dates = []

    if os.path.exists(unicode_path):
        individual_dates = os.listdir(unicode_path)

    return jsonify({'individual_dates': individual_dates})  
 

@app.route('/fetch_summary_csv', methods=['POST'])
def fetch_summary_csv():
    unicode_code = request.form['unicode']
    start_date = request.form.get('start_date') 
    end_date = request.form.get('end_date')     
    summary_csv_path = os.path.join(path_r, unicode_code, 'summary.csv')

    if os.path.exists(summary_csv_path):
        df = pd.read_csv(summary_csv_path)

        if start_date and end_date:
            # Convert start and end dates to datetime
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')


            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')


            full_date_range = pd.date_range(start=start_date_obj, end=end_date_obj)
            df.set_index('date', inplace=True)
            df = df.reindex(full_date_range, fill_value=0).reset_index()


            df.rename(columns={'index': 'date'}, inplace=True)
            df['date'] = df['date'].dt.strftime('%d-%m-%Y') 

            json_data = df.to_json(orient='records')
        else:
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df = df.sort_values('date')

            first_date = df['date'].iloc[0]

            if len(df) < 20:
                num_missing_dates = 20 - len(df)
                missing_dates = [first_date - timedelta(days=i) for i in range(1, num_missing_dates + 1)]
                missing_dates.reverse()  

                missing_dates_df = pd.DataFrame({
                    'date': missing_dates,
                    'mars': [0] * num_missing_dates,
                    'pluto': [0] * num_missing_dates,
                    'mobbo': [0] * num_missing_dates,
                    'R2': [0] * num_missing_dates
                })

                df = pd.concat([missing_dates_df, df], ignore_index=True)

            df['date'] = df['date'].dt.strftime('%d-%m-%Y')  
            json_data = df.to_json(orient='records')

        return jsonify({'summary_data': json_data})
    else:
        return jsonify({'error': 'Summary CSV file not found'})
    

@app.route('/fetch_data_from_date_folder', methods=['POST'])
def fetch_data_from_date_folder():
    unicode_code = request.form['unicode']
    device = request.form['device']
    print(device)
    date = request.form['date']
    print(date)
    date_folder_path = os.path.join(path_r, unicode_code, device,"Dates",date+'.csv')
    print(date_folder_path)
    if os.path.exists(date_folder_path):
        df = pd.read_csv(date_folder_path)
        data= df.to_dict(orient='records')
        return jsonify({'data': data})
        
    else:
        return jsonify({'error': 'date CSV file not found'})

if __name__ == '__main__':
    app.run(debug=True)
