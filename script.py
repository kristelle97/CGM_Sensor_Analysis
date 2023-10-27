from client import get_data
from helpers import write_return_value_to_file
import time

patients = [
    {'email': 'stella-gasman@hotmail.fr', 'password': 'Doping135!', 'output_file': 'data/stella_cgm_data.jsonl'},
    {'email': 'kristellefeghali@gmail.com', 'password': 'CGMsensor!97', 'output_file': 'data/kristelle_cgm_data.jsonl'},
    {'email': 'gavavounette@gmail.com', 'password': 'jotfez-Cysna8-rezwam', 'output_file': 'data/ava_cgm_data.jsonl'},
    {'email': 'gasmandg@free.fr', 'password': 'Gégé135!', 'output_file': 'data/geraldine_cgm_data.jsonl'},
]

for patient in patients:
    cgm_data = get_data(patient['email'], patient['password'])
    data = {
        "timestamp": time.time(),
        "cgm_data": cgm_data,
    }
    write_return_value_to_file(data, patient['output_file'])
