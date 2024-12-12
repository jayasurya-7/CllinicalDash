
import os
import pandas as pd
from datetime import datetime

# Directory path containing user ID folders
BASE_DIRECTORY = "C:\\Users\\Admin\\Desktop\\ClinicalDash\\1012CD\\CllinicalDash\\CllinicalDash\\pythonScrips and datafoler\\Homer-Data"

# Device-specific configurations
PLUTO = ["WFE", "WURD", "FPS", "HOC", "FME1", "FME2"]
MARS = ["SFE", "SABDU", "ELFE"]
DEVICES = ['MARS', 'PLUTO']

# Output fields for devices
output_fields_p = [
    "Date", "HospitalID", "Name", "Status",
    "ConfigWFE", "ConfigWURD", "ConfigFPS", "ConfigHOC", "ConfigFME1", "ConfigFME2",
    "UsedWFE", "UsedWURD", "UsedFPS", "UsedHOC", "UsedFME1", "UsedFME2"
]

output_fields_m = [
    "Date", "HospitalID", "Name", "Status",
    "ConfigSFE", "ConfigSABDU", "ConfigELFE",
    "UsedSFE", "UsedSABDU", "UsedELFE",
]



# Prepare the output data
output_data_mars = []
output_data_pluto = []

# Traverse through each ID folder
for user_id_folder in os.listdir(BASE_DIRECTORY):
    user_path = os.path.join(BASE_DIRECTORY, user_id_folder)

    # Skip if not a folder
    if not os.path.isdir(user_path):
        continue

    for device in DEVICES:
        DEVICE_NAME = device
        output_file = os.path.join(BASE_DIRECTORY, "PlutoUserDetails.csv" if DEVICE_NAME == "PLUTO" else "MarsUserDetails.csv")
        device_path = os.path.join(user_path, device)
        date_folder = os.path.join(device_path, "Dates")
        os.makedirs(date_folder, exist_ok=True)
        config_file = os.path.join(device_path, "configdata.csv")
        session_file = os.path.join(device_path, "session.csv")
        extdata_file = os.path.join(device_path, "extdata.csv")
        


       
        if os.path.exists(config_file) and os.path.exists(session_file):
            try:
                print("Exists")

                # Load config data and get the last row
                config_df = pd.read_csv(config_file)
                if config_df.empty:
                    continue

                last_config_row = config_df.iloc[-1]

                # Load session data
                session_df = pd.read_csv(session_file)
                session_df["DateTime"] = pd.to_datetime(session_df["DateTime"], format="%d-%m-%Y %H:%M:%S", errors="coerce")
                print(config_df['hospno'])
                current_date = datetime.now().strftime("%d-%m-%Y")

                # Filter for current date
                session_df = session_df[session_df["DateTime"].dt.strftime("%d-%m-%Y") == current_date]

                # Calculate total duration for each mechanism/movement
                mechanism_times = session_df.groupby("Mechanism" if DEVICE_NAME == "PLUTO" else "Movement", group_keys=False).apply(
                 lambda group: round(group["MoveTime"].sum() / 60, 2)
                ).to_dict()

                # Prepare user data for the output
                user_data = {
                    "Date": current_date,
                    "HospitalID": last_config_row.get("hospno", ""),
                    "Name": last_config_row.get("name", ""),
                }

                # Add Config values to user data
                for key in MARS if DEVICE_NAME == "MARS" else PLUTO:
                    user_data[f"Config{key}"] = float(last_config_row.get(key, 0))

                # Add Used values to user data and calculate Status
                status = "Done"
                for key in MARS if DEVICE_NAME == "MARS" else PLUTO:
                    user_data[f"Used{key}"] = mechanism_times.get(key, 0)
                    if user_data[f"Used{key}"] < user_data[f"Config{key}"]:
                        status = "InComplete"
                user_data["Status"] = status

                # Append to output data
                if DEVICE_NAME == "MARS":
                    output_data_mars.append(user_data)
                else:
                    output_data_pluto.append(user_data)

            except Exception as e:
                print(f"Error processing folder1 {user_id_folder}: {e}")

        if os.path.exists(session_file):
            print("Exists")
            try:
                # Load session data
                session_df = pd.read_csv(session_file)

                # Convert DateTime and validate format
                session_df["DateTime"] = pd.to_datetime(session_df["DateTime"], format="%d-%m-%Y %H:%M:%S", errors="coerce")
                if session_df["DateTime"].isna().any():
                    raise ValueError("Invalid DateTime format in some rows.")

                # Calculate GameDuration
                session_df["GameDuration"] = round(session_df["MoveTime"]/60, 2)

                # Add Date column
                session_df["Date"] = session_df["DateTime"].dt.strftime("%d-%m-%Y")
                if DEVICE_NAME== "MARS":
                    print("Sessions")

                # Calculate SessionDuration
                session_duration_df = session_df.groupby(["Date", "SessionNumber"])["GameDuration"].sum().reset_index()
                session_duration_df.rename(columns={"GameDuration": "SessionDuration"}, inplace=True)

                # Merge SessionDuration
                session_df = pd.merge(session_df, session_duration_df, on=["Date", "SessionNumber"], how="left")

                # Select and save required columns
                extdata_df = session_df[[
                    "DateTime", "SessionNumber", "SessionDuration", "GameName", "GameDuration", "Mechanism" if DEVICE_NAME == "PLUTO" else "Movement", "MoveTime"
                ]]
                # Ensure DateTime is formatted as dd-mm-yyyy hh:mm:ss before saving
                extdata_df["DateTime"] = extdata_df["DateTime"].dt.strftime("%d-%m-%Y %H:%M:%S")
                extdata_df.to_csv(extdata_file, index=False)
                
                # Group session data by Date, SessionNumber, Mechanism, and GameName, summing GameDuration
                grouped_session_df = session_df.groupby(["Date", "SessionNumber", "Mechanism" if DEVICE_NAME == "PLUTO" else "Movement", "GameName"], as_index=False).agg({
                    "GameDuration": "sum"
                })

                for date, date_group in grouped_session_df.groupby("Date"):
                    output_date_file_path = os.path.join(date_folder, f"{date}.csv")
                    print(output_date_file_path)
                    date_group[["SessionNumber","Mechanism" if DEVICE_NAME == "PLUTO" else "Movement", "GameName", "GameDuration"]].to_csv(output_date_file_path, index=False)
                    # print(f"Created {output_date_file_path} successfully for user {user_id_folder}.")


            except Exception as e:
                print(f"Error processing session file in2 {user_id_folder}:{session_file}: {e}")

# Save output data to CSV files
if output_data_pluto:
    pd.DataFrame(output_data_pluto, columns=output_fields_p).to_csv(os.path.join(BASE_DIRECTORY, "plutoUserDetails.csv"), index=False)

if output_data_mars:
    pd.DataFrame(output_data_mars, columns=output_fields_m).to_csv(os.path.join(BASE_DIRECTORY, "marsUserDetails.csv"), index=False)
