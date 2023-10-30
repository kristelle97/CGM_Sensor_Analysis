from glycemic_variability_indices import *
import json


def get_meal_log_from_json(filepath, date):
    meal_log = {}
    with open(filepath, 'r') as file:
        for line in file:
            raw_data = json.loads(line)
            if raw_data['day'] == date and 'Meals' in raw_data:
                for meal in raw_data['Meals']:
                    if 'Timestamp' in meal and 'Meal' in meal:
                        meal_log[meal['Timestamp']] = meal['Meal']
    return meal_log


def get_cgm_data_from_json(filepath, date):
    blood_sugar_data = []
    time_points = []
    data = {}
    with open(filepath, 'r') as file:
        for line in file:
            raw_data = json.loads(line)
            timestamp_datetime = datetime.fromtimestamp(raw_data['timestamp']).strftime('%d/%m/%Y')
            if timestamp_datetime == date:
                for node in raw_data['cgm_data']:
                    data[node['Timestamp']] = node['ValueInMgPerDl']
                    blood_sugar_data.append(node['ValueInMgPerDl'])
                    time_points.append(node['Timestamp'])
    return data, blood_sugar_data, compute_timepoints(time_points)


data, blood_sugar_data, time_points = get_cgm_data_from_json('./data/stella_cgm_data.jsonl', '29/10/2023')
# meal_log = get_meal_log_from_json('./meal_logs/ava_meal_log.jsonl', '10/25/2023')
meal_log = {}
baseline = compute_blood_sugar_baseline(blood_sugar_data)
threshold = compute_threshold(baseline, 20)

# meal_times = detect_meal_times(data, meal_log, threshold)

print(detect_meal_times(data, meal_log, threshold))


# print(blood_sugar_data)
# print(calculate_postprandial_blood_sugar_fluctuation(meal_times, baseline))

# print("AUC: ", calculate_auc(meal_times))

# compute_glycemic_variability_indices(blood_sugar_data, time_points)

# TODO: define the baseline for each individual, for now using time spent in ranges of size 5 but not accurate.
