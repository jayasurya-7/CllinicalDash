import os
import pandas as pd
from datetime import datetime

# Directory path containing user ID folders
base_directory = "D:\\Data2\\HomerDataManipulation"  # Replace with your actual base directory
output_file = os.path.join(base_directory, "userDetails.csv")

# Fields to include in the final output
output_fields = [
    "Date", "HospitalID", "Name", "Status",
    "ConfigWFE", "ConfigWURD", "ConfigFPS", "ConfigHOC", "ConfigFME1", "ConfigFME2",
    "UsedWFE", "UsedWURD", "UsedFPS", "UsedHOC", "UsedFME1", "UsedFME2"
]

# Helper function to calculate duration in minutes with two decimal places
def calculate_duration(start_time, stop_time):
    start = datetime.strptime(start_time, "%d-%m-%Y %H:%M:%S")
    stop = datetime.strptime(stop_time, "%d-%m-%Y %H:%M:%S")
    duration = (stop - start).total_seconds() / 60  # Convert to minutes
    return round(duration, 2)  # Round to 2 decimal places


# Prepare the output DataFrame
output_data = []

# Traverse through each ID folder
for user_id_folder in os.listdir(base_directory):
    user_path = os.path.join(base_directory, user_id_folder)
    
    # Skip if not a folder
    if not os.path.isdir(user_path):
        continue

    config_file = os.path.join(user_path, "configdata.csv")
    session_file = os.path.join(user_path, "Sessions.csv")
    extdata_file = os.path.join(user_path, "extdata.csv")
    # Check if both files exist
    if os.path.exists(config_file) and os.path.exists(session_file):
        try:
            # Load config data and get the last row
            config_df = pd.read_csv(config_file)
            if config_df.empty:
                continue
            last_config_row = config_df.iloc[-1]

            # Load session data
            session_df = pd.read_csv(session_file)
            session_df["DateTime"] = pd.to_datetime(session_df["DateTime"], format="%d-%m-%Y %H:%M:%S")

            # Filter session data for the current date
            current_date = datetime.now().strftime("%d-%m-%Y")
            session_df = session_df[session_df["DateTime"].dt.strftime("%d-%m-%Y") == current_date]
            # Calculate total duration for each mechanism
            mechanism_times = session_df.groupby("Mechanism", group_keys=False).apply(
                lambda group: group.apply(
                    lambda row: calculate_duration(row["StartTime"], row["StopTime"]), axis=1
                ).sum()
            ).to_dict()


            # Prepare user data for the output
            user_data = {
                "Date": current_date,
                "HospitalID": last_config_row.get("hospno", ""),
                "Name": last_config_row.get("name", ""),
            }

            # Add Config values to user data
            for key in ["WFE", "WURD", "FPS", "HOC", "FME1", "FME2"]:
                user_data[f"Config{key}"] = float(last_config_row.get(key, 0))

            # Add Used values to user data and calculate Status
            status = "Done"
            for key in ["WFE", "WURD", "FPS", "HOC", "FME1", "FME2"]:
                user_data[f"Used{key}"] = mechanism_times.get(key, 0)

                if user_data[f"Used{key}"] < user_data[f"Config{key}"]:
                    status = "InComplete"
            user_data["Status"] = status

            # Append to output data
            output_data.append(user_data)

        except Exception as e:
            print(f"Error processing folder {user_id_folder}: {e}")
     # Check if Sessions.csv exists
    if os.path.exists(session_file):
        try:
            # Load session data
            session_df = pd.read_csv(session_file)

            # Calculate GameDuration for each entry
            session_df["GameDuration"] = session_df.apply(
                lambda row: calculate_duration(row["StartTime"], row["StopTime"]), axis=1
            )

            # Add a Date column for grouping by day
            session_df["Date"] = session_df["DateTime"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y %H:%M:%S").strftime("%d-%m-%Y"))

            # Calculate SessionDuration (total time played for each session on a given day)
            session_duration_df = session_df.groupby(["Date", "SessionNumber"])["GameDuration"].sum().reset_index()
            session_duration_df.rename(columns={"GameDuration": "SessionDuration"}, inplace=True)

            # Merge the session durations back into the main DataFrame
            session_df = pd.merge(session_df, session_duration_df, on=["Date", "SessionNumber"], how="left")

            # Select and rename the required columns
            extdata_df = session_df[[
                "DateTime", "SessionNumber", "SessionDuration", "GameName", "GameDuration", "Mechanism", "MoveTime"
            ]]

            # Save to extdata.csv in the current user's folder
            extdata_df.to_csv(extdata_file, index=False)

            print(f"Created {extdata_file} successfully.")
        except Exception as e:
            print(f"Error processing folder {user_id_folder}: {e}")

# Save all output data to a CSV file
output_df = pd.DataFrame(output_data, columns=output_fields)
output_df.to_csv(output_file, index=False)

print(f"userDetails.csv has been created successfully at {output_file}.")
