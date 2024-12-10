import os
import pandas as pd
from datetime import datetime

base_dir = "D:\\Data2\\HomerDataManipulation"  
output_file_path = os.path.join(base_dir, "user_details.csv")

output_columns = [
    "Date", "HospitalID", "Name", "Status",
    "Config_WFE", "Config_WURD", "Config_FPS", "Config_HOC", "Config_FME1", "Config_FME2",
    "Used_WFE", "Used_WURD", "Used_FPS", "Used_HOC", "Used_FME1", "Used_FME2"
]
user_data_list = []

# Traverse through each user ID folder
for user_folder in os.listdir(base_dir):
    user_folder_path = os.path.join(base_dir, user_folder)
    date_folder = os.path.join(user_folder_path, "Dates")

    if not os.path.isdir(user_folder_path):
        continue
    
    os.makedirs(date_folder, exist_ok=True)

    config_file_path = os.path.join(user_folder_path, "configdata.csv")
    session_file_path = os.path.join(user_folder_path, "Sessions.csv")
    extdata_file_path = os.path.join(user_folder_path, "extdata.csv")

    if os.path.exists(config_file_path) and os.path.exists(session_file_path):
        try:
            config_df = pd.read_csv(config_file_path)
            if config_df.empty:
                continue
            last_config_row = config_df.iloc[-1]

            session_df = pd.read_csv(session_file_path)
            session_df["DateTime"] = pd.to_datetime(session_df["DateTime"], format="%d-%m-%Y %H:%M:%S")

            today_date = datetime.now().strftime("%d-%m-%Y")
            session_df = session_df[session_df["DateTime"].dt.strftime("%d-%m-%Y") == today_date]

            mechanism_times = session_df.groupby("Mechanism", group_keys=False).apply(
                lambda group: round(group["MoveTime"].sum() / 60, 2)  # Sum the MoveTime for the group and convert to minutes
            ).to_dict()

            user_info = {
                "Date": today_date,
                "HospitalID": last_config_row.get("hospno", ""),
                "Name": last_config_row.get("name", ""),
            }

            for config_key in ["WFE", "WURD", "FPS", "HOC", "FME1", "FME2"]:
                user_info[f"Config_{config_key}"] = float(last_config_row.get(config_key, 0))

            status = "Done"
            for config_key in ["WFE", "WURD", "FPS", "HOC", "FME1", "FME2"]:
                user_info[f"Used_{config_key}"] = mechanism_times.get(config_key, 0)

                if user_info[f"Used_{config_key}"] < user_info[f"Config_{config_key}"]:
                    status = "Incomplete"
            user_info["Status"] = status

            user_data_list.append(user_info)

        except Exception as e:
            print(f"Error processing folder {user_folder}: {e}")


    if os.path.exists(session_file_path):
        try:
            
            session_df = pd.read_csv(session_file_path)
            session_df["GameDuration"] = round(session_df["MoveTime"] / 60, 2)

            session_df["Date"] = session_df["DateTime"].apply(lambda x: datetime.strptime(x, "%d-%m-%Y %H:%M:%S").strftime("%d-%m-%Y"))

            session_duration_df = session_df.groupby(["Date", "SessionNumber"])["GameDuration"].sum().reset_index()
            session_duration_df.rename(columns={"GameDuration": "SessionDuration"}, inplace=True)

            session_df = pd.merge(session_df, session_duration_df, on=["Date", "SessionNumber"], how="left")

            extdata_df = session_df[[
                "DateTime", "SessionNumber", "SessionDuration", "GameName", "GameDuration", "Mechanism", "MoveTime"
            ]]

            extdata_df.to_csv(extdata_file_path, index=False)
            print(f"Created {extdata_file_path} successfully.")

            # Group session data by Date, SessionNumber, Mechanism, and GameName, summing GameDuration
            grouped_session_df = session_df.groupby(["Date", "SessionNumber", "Mechanism", "GameName"], as_index=False).agg({
                "GameDuration": "sum"
            })

            for date, date_group in grouped_session_df.groupby("Date"):
                output_date_file_path = os.path.join(date_folder, f"{date}.csv")

                date_group[["SessionNumber", "Mechanism", "GameName", "GameDuration"]].to_csv(output_date_file_path, index=False)
                print(f"Created {output_date_file_path} successfully for user {user_folder}.")

        except Exception as e:
            print(f"Error processing folder {user_folder}: {e}")

user_data_df = pd.DataFrame(user_data_list, columns=output_columns)
user_data_df.to_csv(output_file_path, index=False)

print(f"user_details.csv has been created successfully at {output_file_path}.")
