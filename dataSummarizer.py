import os
import pandas as pd
import csv
import json
from datetime import datetime


source_dirs = ['D:/DEMO/mars', 'D:/DEMO/mobbo', 'D:/DEMO/hypercube', 'D:/DEMO/R2']
destination_dir = "D:\\DEMO\\DESTINATION"
PATIENTS_CSV = os.path.join(destination_dir, 'patients.csv')

def load_existing_patients():
    if not os.path.exists(PATIENTS_CSV):
        return {}
    with open(PATIENTS_CSV, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV file does not contain any headers")
        if 'uniqueid' not in reader.fieldnames or 'name' not in reader.fieldnames:
            raise ValueError(f"CSV file headers: {reader.fieldnames} do not contain the required headers 'uniqueid' and 'name'")
        return {row['uniqueid']: row['name'] for row in reader}

def save_patient(uniqueid, name):
    existing_patients = load_existing_patients()
    if uniqueid not in existing_patients:
        file_exists = os.path.exists(PATIENTS_CSV)
        with open(PATIENTS_CSV, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['uniqueid', 'name'])
            writer.writerow([uniqueid, name])

def process_sessions_data(df):
    df['StartTime'] = pd.to_datetime(df['StartTime'], format='%d-%m-%Y %H:%M:%S')
    df['StopTime'] = pd.to_datetime(df['StopTime'], format='%d-%m-%Y %H:%M:%S')
    df['Duration'] = (df['StopTime'] - df['StartTime']).dt.total_seconds()

    df['Date'] = df['StartTime'].dt.strftime('%d-%m-%Y')
    df['SessionDuration'] = df.groupby('SessionNumber')['Duration'].transform('sum')

    summary = df.groupby('Date').agg(
        TotalSessionsInDay=('SessionNumber', 'nunique'),
        TotalDuration=('Duration', 'sum'),
        AssessmentDuration=('Duration', lambda x: x[df['Assessment'] == 1].sum()),
        CalibrationDuration=('Duration', lambda x: x[df['GameName'] == 'CALIBRATION'].sum())
    ).reset_index()

    game_durations = df.groupby(['Date', 'SessionNumber', 'GameName']).agg(
        GameDuration=('Duration', 'sum'),
        SessionDuration=('SessionDuration', 'first')
    ).reset_index()

    return summary, game_durations

def save_to_destination(unique_id, device_name, summary, game_durations, sessions_df, patient_data):
    unique_id_dir = os.path.join(destination_dir, unique_id)
    os.makedirs(unique_id_dir, exist_ok=True)

    id_json_path = os.path.join(unique_id_dir, f'{unique_id}.json')
    with open(id_json_path, 'w') as json_file:
        json.dump(patient_data, json_file)

    device_dir = os.path.join(unique_id_dir, device_name)
    os.makedirs(device_dir, exist_ok=True)

    summary_file = os.path.join(device_dir, 'sessiondata.csv')
    sessions_file = os.path.join(device_dir, 'Sessions.csv')
    summary.to_csv(summary_file, index=False)
    sessions_df.to_csv(sessions_file, index=False)

    dates_dir = os.path.join(device_dir, 'Dates')
    os.makedirs(dates_dir, exist_ok=True)
    for date, group in game_durations.groupby('Date'):
        date_file = os.path.join(dates_dir, f'{date}.csv')
        group = group[['SessionNumber', 'SessionDuration', 'GameName', 'GameDuration']]
        group.to_csv(date_file, index=False)

    # Create devicename.csv with fields 'date' and 'minutes'
    device_summary = summary[['Date', 'TotalDuration']].copy()
    device_summary['minutes'] = device_summary['TotalDuration']   # Convert seconds to minutes
    device_summary = device_summary[['Date', 'minutes']]
    device_summary_file = os.path.join(device_dir, f'{device_name}.csv')
    device_summary.to_csv(device_summary_file, index=False)

def aggregate_data():
    aggregate_dict = {}

    for id_folder in os.listdir(destination_dir):
        id_path = os.path.join(destination_dir, id_folder)
        if os.path.isdir(id_path):
            for device_folder in os.listdir(id_path):
                device_path = os.path.join(id_path, device_folder)
                if os.path.isdir(device_path):
                    session_file_path = os.path.join(device_path, 'sessiondata.csv')
                    if os.path.exists(session_file_path):
                        df = pd.read_csv(session_file_path)
                        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')

                        for _, row in df.iterrows():
                            date = row['Date'].strftime('%d-%m-%Y')
                            duration = row['TotalDuration']
                            unique_id = id_folder
                            device = device_folder

                            if unique_id not in aggregate_dict:
                                aggregate_dict[unique_id] = {}

                            if date not in aggregate_dict[unique_id]:
                                aggregate_dict[unique_id][date] = {'mars': 0, 'pluto': 0, 'mobbo': 0, 'R2': 0}

                            if device in aggregate_dict[unique_id][date]:
                                aggregate_dict[unique_id][date][device] += duration
                            else:
                                aggregate_dict[unique_id][date][device] = duration

    # Create DataFrame and save separate summary.csv for each unique_id
    for unique_id, dates in aggregate_dict.items():
        summary_rows = []
        for date, devices in dates.items():
            summary_row = {'date': date, 'mars': devices['mars'], 'pluto': devices['pluto'], 'mobbo': devices['mobbo'], 'R2': devices['R2']}
            summary_rows.append(summary_row)

        summary_df = pd.DataFrame(summary_rows)
        summary_dir = os.path.join(destination_dir, unique_id)
        os.makedirs(summary_dir, exist_ok=True)
        summary_df.to_csv(os.path.join(summary_dir, 'summary.csv'), index=False)

def main():
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    for source_dir in source_dirs:
        for id_folder in os.listdir(source_dir):
            id_path = os.path.join(source_dir, id_folder)
            if os.path.isdir(id_path):
                session_file_path = os.path.join(id_path, 'Sessions.csv')
                json_file_path = os.path.join(id_path, 'patient.json')
                if os.path.exists(session_file_path) and os.path.exists(json_file_path):
                    try:
                        with open(json_file_path, 'r') as json_file:
                            patient_data = json.load(json_file)
                    except json.JSONDecodeError as e:
                        print(f"Error reading JSON file {json_file_path}: {e}")
                        continue

                    unique_id = id_folder
                    patient_name = patient_data.get('name', 'Unknown')

                    save_patient(unique_id, patient_name)

                    df = pd.read_csv(session_file_path)
                    summary, game_durations = process_sessions_data(df)
                    device_name = os.path.basename(source_dir)  # Use the source directory name as the device name
                    save_to_destination(unique_id, device_name, summary, game_durations, df, patient_data)

    aggregate_data()

if __name__ == "__main__":
    main()
