import numpy as np
from helpers import *
from numpy import trapz
from datetime import datetime, timedelta


# The standard deviation measures the spread or variability of blood sugar values. A higher standard deviation
# indicates greater variability in blood sugar levels, which may suggest unstable blood sugar control. Input: Blood
# sugar measurements in mg/dl.
def compute_standard_deviation(data):
    return np.std(data)


# The mean blood sugar value represents the average blood sugar level over the measurement period.
# Monitoring the mean helps understand the overall blood sugar control.
# A high mean suggests consistently elevated blood sugar levels, while a low mean may indicate better control.
# Input: Blood sugar measurements in mg/dl.
def compute_mean(data):
    return np.mean(data)


# MAGE quantifies the magnitude of fluctuations in blood sugar levels.
# A higher MAGE value indicates larger and more frequent fluctuations.
# Lower MAGE values suggest more stable blood sugar control.
# Input: Blood sugar measurements in mg/dl.
def compute_mage(data):
    high = max(data)
    low = min(data)
    excursions = [high - low]  # Initialize with the first excursion
    for i in range(1, len(data)):
        excursions.append(max(data[i] - low, high - data[i]))
    return np.mean(excursions)


# CONGA measures the variability of blood sugar levels within a specified time window.
# A higher CONGA value indicates greater variability within the chosen time window.
# Useful for understanding short-term variability in blood sugar.
# Input:
#   - data (list or numpy.array): Blood sugar measurements in mg/dl.
#   - time_points (list or numpy.array): Corresponding time points in minutes.
#   - window_size (int): Size of the time window for CONGA calculation (in minutes).
def compute_conga(data, time_points, window_size=1):
    conga_values = []
    for i in range(len(data)):
        if i + window_size >= len(data):
            break
        window = data[i:i + window_size]
        conga_values.append(np.std(window))
    return np.mean(conga_values)


# MODD calculates the average difference between consecutive daily blood sugar measurements.
# A higher MODD value indicates larger daily fluctuations.
# Lower MODD values suggest more consistent blood sugar control over a day.
# Input: Blood sugar measurements in mg/dl.
def compute_modd(data):
    daily_differences = [abs(data[i] - data[i - 1]) for i in range(1, len(data))]
    return np.mean(daily_differences)


# GRADE combines the mean and standard deviation to assess overall blood sugar risk.
# A higher GRADE value suggests higher blood sugar risk.
# GRADE is a composite index that takes both central tendency and variability into account.
# Input: Blood sugar measurements in mg/dl.
def compute_grade(data):
    mean = np.mean(data)
    std_dev = np.std(data)
    grade = (mean + (2 * std_dev)) / 18.01559
    return grade


# Estimated HbA1c provides an approximation of the long-term average blood sugar levels over two to three months.
# A higher estimated HbA1c value implies poorer long-term blood sugar control.
# It can be used as a proxy for assessing the risk of diabetes complications.
# Input: Blood sugar measurements in mg/dl.
def compute_estimated_hba1c(data):
    mean_blood_sugar = np.mean(data)
    estimated_hba1c = (mean_blood_sugar + 46.7) / 28.7
    return estimated_hba1c


# Calculate the area under the blood sugar curve within a specific time range.
# Input:
#   - Blood sugar measurements in mg/dL.
#   - Time points in minutes.
#   - Start time in minutes.
#   - End time in minutes.
def calculate_auc(meals_data):
    auc_by_meal_time = []
    for meal_data in meals_data:
        auc_by_meal_time += [trapz(list(meal_data['blood_sugar_values'].values()), dx=5)]
    return auc_by_meal_time


# Compute the blood sugar baseline from CGM sensor data based on the blood sugar range a person spends the most time
# in during the day.
def compute_blood_sugar_baseline(cgm_data):
    if not cgm_data:
        raise ValueError("CGM data is empty.")

    # Range width (e.g., 10 mg/dL) to group the data into bins.
    range_width = 5

    # Stores the count of data points in each range.
    range_counts = {}

    for value in cgm_data:
        # Calculate the range to which the data point belongs.
        range_start = (value // range_width) * range_width
        range_end = range_start + range_width

        # Increment the count for that range.
        range_counts[(range_start, range_end)] = range_counts.get((range_start, range_end), 0) + 1

    # Find the range with the highest count.
    most_frequent_range = max(range_counts, key=range_counts.get)

    # Calculate the baseline as the middle of the most frequent range.
    blood_sugar_baseline = (most_frequent_range[0] + most_frequent_range[1]) / 2

    return blood_sugar_baseline


# Define the threshold for meal detection based on a percentage increase from the baseline.
def compute_threshold(baseline, percentage_increase=20):
    threshold = baseline * (1 + percentage_increase / 100)
    return threshold


# Get meal times based on meal logs inputted by the user.
def get_meal_times(data, meals_log, meals_data):
    for timestamp, meal in meals_log.items():
        # if meal not in meals_added
        start_timestamp = datetime.strptime(timestamp, '%m/%d/%Y %I:%M:%S %p') - timedelta(hours=1)
        start_time = datetime.strptime(start_timestamp.strftime('%m/%d/%Y %I:%M:%S %p'), '%m/%d/%Y %I:%M:%S %p')

        end_timestamp = datetime.strptime(timestamp, '%m/%d/%Y %I:%M:%S %p') + timedelta(hours=3)
        end_time = datetime.strptime(end_timestamp.strftime('%m/%d/%Y %I:%M:%S %p'), '%m/%d/%Y %I:%M:%S %p')

        # Get blood sugar value during meal time.
        blood_sugar_values = {ts: value for ts, value in data.items() if
                              start_time <= datetime.strptime(ts, '%m/%d/%Y %I:%M:%S %p') <= end_time}

        meals = [meal for entry in meals_data for meal in entry['meal']]

        # Check whether meal was detected by function detect_meal_times.
        if meal not in meals:
            meal_data = {'start_time': start_time.strftime('%m/%d/%Y %I:%M:%S %p'),
                         'end_time': end_time.strftime('%m/%d/%Y %I:%M:%S %p'),
                         'meal': meal, 'blood_sugar_values': blood_sugar_values}
            meals_data.append(meal_data)

    return meals_data


# Identify potential meal times based on blood sugar data and a threshold.
# The blood sugar peak is identified to create a window of 4 hours: 1 hour before the peak, 3 hours after.
# Map meal times with meals logged.
def detect_meal_times(data, meals_log, threshold, window_size=5):
    timestamps = list(data.keys())
    glucose_values = list(data.values())
    meals_data = []
    in_meal = False
    start_time = None
    end_time = None

    for i in range(1, len(timestamps)):
        current_bs = glucose_values[i]

        if current_bs > threshold and not in_meal:
            in_meal = True
            time = datetime.strptime(timestamps[i], '%m/%d/%Y %I:%M:%S %p')

            # Adjust the time range to start 1 hour before increase detected and 3 hours after meal.
            start_time = time - timedelta(hours=1)
            end_time = time + timedelta(hours=3)

            # Data is collected every day until 12am, so if someone had a late meal time (after 10pm), data will be
            # missing past 12am.
            if end_time > datetime.strptime(timestamps[len(timestamps) - 1], '%m/%d/%Y %I:%M:%S %p'):
                end_time = datetime.strptime(timestamps[len(timestamps) - 1], '%m/%d/%Y %I:%M:%S %p') - timedelta(
                    minutes=15)

        if in_meal and end_time is not None and datetime.strptime(timestamps[i], '%m/%d/%Y %I:%M:%S %p') > end_time:
            in_meal = False

            # Get blood sugar values during meal time.
            blood_sugar_values = {ts: value for ts, value in data.items() if
                                  start_time <= datetime.strptime(ts, '%m/%d/%Y %I:%M:%S %p') <= end_time}

            # Get meals eaten during each meal times from meal logs
            meals = [value for ts, value in meals_log.items() if
                     start_time <= datetime.strptime(ts, '%m/%d/%Y %I:%M:%S %p') <= end_time]

            meal_data = {'start_time': start_time.strftime('%m/%d/%Y %I:%M:%S %p'),
                         'end_time': end_time.strftime('%m/%d/%Y %I:%M:%S %p'),
                         'meal': meals, 'blood_sugar_values': blood_sugar_values}

            meals_data.append(meal_data)

    meals_data = get_meal_times(data, meals_log, meals_data)

    return meals_data


def compute_time_difference_between_meals(meals_data):
    meals_start_time = [datetime.strptime(meal_data['start_time'], '%m/%d/%Y %I:%M:%S %p') for meal_data in meals_data]
    time_difference_between_meals = [meals_start_time[i + 1] - meals_start_time[i] for i in range(len(meals_start_time) - 1)]
    return time_difference_between_meals


# Calculate blood sugar fluctuation from 1 hour to another during 4h meal time window (1hour pre-meal and 3 hours
# post-meal).
# For each 1hour window we compare the minimum and maximum glucose level in the window.
# Check for reactive hypoglycemia i.e. if there is a drop below the baseline after a meal.
# For a healthy individual the blood sugar level should be close to the baseline 2hours post meal.
def calculate_postprandial_blood_sugar_fluctuation(meals_data, baseline):
    blood_sugar_fluctuation_by_meal = []
    for meal_data in meals_data:
        blood_sugar_fluctuations = []
        time_points = compute_timepoints(meal_data['blood_sugar_values'].keys())
        blood_sugar_values = list(meal_data['blood_sugar_values'].values())
        print(blood_sugar_values)
        hours_post_meal = [0, 60, 120, 180, 240]
        for i in range(1, len(hours_post_meal)):
            t0 = min(time_points, key=lambda x: abs(x - hours_post_meal[i - 1]))
            t1 = min(time_points, key=lambda x: abs(x - hours_post_meal[i]))

            blood_sugar_in_window = blood_sugar_values[time_points.index(t0):time_points.index(t1)]
            if blood_sugar_in_window:
                min_blood_sugar_measurement = min(blood_sugar_in_window)
                max_blood_sugar_measurement = max(blood_sugar_in_window)
                blood_sugar_fluctuation = min_blood_sugar_measurement - max_blood_sugar_measurement if blood_sugar_in_window.index(
                    min_blood_sugar_measurement) < blood_sugar_in_window.index(
                    max_blood_sugar_measurement) else max_blood_sugar_measurement - min_blood_sugar_measurement
                blood_sugar_fluctuations.append(blood_sugar_fluctuation)

        # Check if there is a dip of 20ml/dl below the baseline post meal which qualifies as reactive hypoglycemia.
        reactive_hypoglycemia = True if len([bs_value for bs_value in blood_sugar_values
                                             if bs_value <= baseline - 10]) > 0 else False
        blood_sugar_fluctuation_by_meal.append({
            'meal': meal_data['meal'],
            'start_time': meal_data['start_time'],
            'end_time': meal_data['end_time'],
            'blood_sugar_increase': blood_sugar_fluctuations,
            'reactive hypoglycemia': reactive_hypoglycemia
        })
    return blood_sugar_fluctuation_by_meal


def compute_glycemic_variability_indices(blood_sugar_data, time_points):
    window_size = 3
    print("Standard Deviation:", compute_standard_deviation(blood_sugar_data))
    print("Mean:", compute_mean(blood_sugar_data))
    print("MAGE:", compute_mage(blood_sugar_data))
    print("CONGA:", compute_conga(blood_sugar_data, time_points, window_size))
    print("MODD:", compute_modd(blood_sugar_data))
    print("GRADE:", compute_grade(blood_sugar_data))
    print("Estimated HbA1c:", compute_estimated_hba1c(blood_sugar_data))
