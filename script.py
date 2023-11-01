import datetime

from client import get_data
from helpers import write_return_value_to_file

patients = [
    {'email': 'stella-gasman@hotmail.fr', 'password': 'Doping135!', 'output_file': 'data/stella_cgm_data.jsonl'},
    {'email': 'gavavounette@gmail.com', 'password': 'jotfez-Cysna8-rezwam', 'output_file': 'data/ava_cgm_data.jsonl'},
    {'email': 'gasmandg@free.fr', 'password': 'Gégé135!', 'output_file': 'data/geraldine_cgm_data.jsonl'},
]

for patient in patients:
    cgm_data = get_data(patient['email'], patient['password'])
    data = {
        "timestamp": datetime.datetime.strptime(cgm_data[0]['Timestamp'], '%m/%d/%Y %I:%M:%S %p').strftime('%m/%d/%Y'),
        "cgm_data": cgm_data,
    }
    # TODO: Before writing to json get all json lines with the same data[timestamp] and remove entries
    #  with the same data[cgm_data]['timestamp']
    write_return_value_to_file(data, patient['output_file'])