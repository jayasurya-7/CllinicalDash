import os
import pandas as pd
from datetime import datetime

# Directory path containing user ID folders
BASE_DIRECTORY = "C:\\Homer-Data"

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

# Helper function to calculate duration in minutes
def calculate_duration_p(start_time, stop_time):
    start = datetime.strptime(start_time, "%d-%m-%Y %H:%M:%S")
    stop = datetime.strptime(stop_time, "%d-%m-%Y %H:%M:%S")
    duration = (stop - start).total_seconds() / 60  # Convert to minutes
    return round(duration, 2)  # Round to 2 decimal places

def calculate_duration(start_time, stop_time):
    try:
        start = datetime.strptime(start_time, "%H:%M:%S")
        stop = datetime.strptime(stop_time, "%H:%M:%S")
        duration = (stop - start).total_seconds()
        if duration < 0:  # Handle next-day StopTime
            duration += 24 * 3600
        return duration
    except Exception as e:
        raise ValueError(f"Error calculating duration: {e}")

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
        config_file = os.path.join(device_path, "configdata.csv")
        session_file = os.path.join(device_path, "session.csv")
        extdata_file = os.path.join(device_path, "extdata.csv")

        if os.path.exists(config_file) and os.path.exists(session_file):
            try:
                # Load config data and get the last row
                config_df = pd.read_csv(config_file)
                if config_df.empty:
                    continue

                last_config_row = config_df.iloc[-1]

                # Load session data
                session_df = pd.read_csv(session_file)
                session_df["DateTime"] = pd.to_datetime(session_df["DateTime"], format="%d-%m-%Y %H:%M:%S", errors="coerce")
                current_date = datetime.now().strftime("%d-%m-%Y")

                # Filter for current date
                session_df = session_df[session_df["DateTime"].dt.strftime("%d-%m-%Y") == current_date]

                # Calculate total duration for each mechanism/movement
                mechanism_times = session_df.groupby("Mechanism" if DEVICE_NAME == "PLUTO" else "Movement", group_keys=False).apply(
                    lambda group: group.apply(
                        lambda row: calculate_duration_p(row["StartTime"], row["StopTime"]) if DEVICE_NAME == "PLUTO" else calculate_duration(row["StartTime"], row["StopTime"]), axis=1
                    ).sum()
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
                print(f"Error processing folder {user_id_folder}: {e}")

        if os.path.exists(session_file):
            try:
                # Load session data
                session_df = pd.read_csv(session_file)

                # Convert DateTime and validate format
                session_df["DateTime"] = pd.to_datetime(session_df["DateTime"], format="%d-%m-%Y %H:%M:%S", errors="coerce")
                if session_df["DateTime"].isna().any():
                    raise ValueError("Invalid DateTime format in some rows.")

                # Calculate GameDuration
                session_df["GameDuration"] = session_df.apply(
                    lambda row: calculate_duration_p(row["StartTime"], row["StopTime"]) if DEVICE_NAME == "PLUTO" else calculate_duration(row["StartTime"], row["StopTime"]), axis=1
                )

                # Add Date column
                session_df["Date"] = session_df["DateTime"].dt.strftime("%d-%m-%Y")

                # Calculate SessionDuration
                session_duration_df = session_df.groupby(["Date", "SessionNumber"])["GameDuration"].sum().reset_index()
                session_duration_df.rename(columns={"GameDuration": "SessionDuration"}, inplace=True)

                # Merge SessionDuration
                session_df = pd.merge(session_df, session_duration_df, on=["Date", "SessionNumber"], how="left")

                # Select and save required columns
                extdata_df = session_df[[
                    "DateTime", "SessionNumber", "SessionDuration", "GameName", "GameDuration", "Mechanism" if DEVICE_NAME == "PLUTO" else "Movement", "MoveTime"
                ]]
                extdata_df.to_csv(extdata_file, index=False)

            except Exception as e:
                print(f"Error processing session file in {user_id_folder}: {e}")

# Save output data to CSV files
if output_data_pluto:
    pd.DataFrame(output_data_pluto, columns=output_fields_p).to_csv(os.path.join(BASE_DIRECTORY, "plutoUserDetails.csv"), index=False)

if output_data_mars:
    pd.DataFrame(output_data_mars, columns=output_fields_m).to_csv(os.path.join(BASE_DIRECTORY, "marsUserDetails.csv"), index=False)
