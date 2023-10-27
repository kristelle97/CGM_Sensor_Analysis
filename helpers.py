from datetime import datetime
import json

def compute_timepoints(timestamps):
    # Define the datetime format for your timestamps
    datetime_format = "%m/%d/%Y %I:%M:%S %p"

    # Convert timestamps to datetime objects
    datetime_objects = [datetime.strptime(timestamp, datetime_format) for timestamp in timestamps]

    # Calculate time differences in minutes relative to the first measurement
    time_points = [(dt - datetime_objects[0]).total_seconds() / 60 for dt in datetime_objects]

    return time_points

def write_return_value_to_file(data, output_file):
    try:
        # Open the file in write mode and write the result to it
        with open(output_file, 'a') as file:
            # Check if the file is empty, and if not, add a comma and a newline
            if file.tell() > 0:
                file.write("\n")

            json_data = json.dumps(data)
            file.write(json_data)

        print(f'Result written to {output_file}')
    except Exception as e:
        print(f'An error occurred: {str(e)}')


