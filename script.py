import datetime

from client import get_data
from helpers import write_return_value_to_file
import json

patients = [
    {'email': 'stella-gasman@hotmail.fr', 'password': 'Doping135!', 'output_file': 'data/stella_cgm_data.jsonl'},
    {'email': 'gavavounette@gmail.com', 'password': 'jotfez-Cysna8-rezwam', 'output_file': 'data/ava_cgm_data.jsonl'},
    {'email': 'gasmandg@free.fr', 'password': 'Gégé135!', 'output_file': 'data/geraldine_cgm_data.jsonl'},
    {'email': 'emmagasman5@gmail.com', 'password': 'Stellacute55!!', 'output_file': 'data/emma_cgm_data.jsonl'},
]


def remove_duplicate_cgm_data(filepath, cgm_data):
    cgm_data_by_date = {}
    for node in cgm_data:
        cgm_timestamp = datetime.datetime.strptime(node['Timestamp'], '%m/%d/%Y %I:%M:%S %p').strftime(
            '%m/%d/%Y').replace('/0', '/')
        cgm_data_by_date.setdefault(cgm_timestamp, []).append({'cgm_data': node, 'in_file': False})

    with open(filepath, 'r') as file:
        for line in file:
            raw_data = json.loads(line)
            if raw_data['timestamp'] in cgm_data_by_date.keys():
                for entry in cgm_data_by_date[raw_data['timestamp']]:
                    if entry['cgm_data'] in raw_data['cgm_data']:
                        entry['in_file'] = True

    result_data = {}
    for date, entries in cgm_data_by_date.items():
        for entry in entries:
            if not entry['in_file']:
                result_data.setdefault(date, []).append(entry['cgm_data'])

    return result_data


for patient in patients:
    cgm_data = get_data(patient['email'], patient['password'])
    # TODO: Before writing to json get all json lines with the same data[timestamp] and remove entries
    #  with the same data[cgm_data]['timestamp']
    unique_cgm_data = remove_duplicate_cgm_data(patient['output_file'], cgm_data)
    print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
    for key, value in unique_cgm_data.items():
        data = {
            "timestamp": key,
            "cgm_data": value,
        }
        write_return_value_to_file(data, patient['output_file'])
