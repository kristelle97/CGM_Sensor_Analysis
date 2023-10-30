import requests as requests

BASE_URL = "https://api-fr.libreview.io"  # or "https://api-eu.libreview.io" for Europe
HEADERS = {
    'accept-encoding': 'gzip',
    'cache-control': 'no-cache',
    'connection': 'Keep-Alive',
    'content-type': 'application/json',
    'product': 'llu.android',
    'version': '4.7'
}


# Log in and retrieve JWT token.
def login(email, password):
    endpoint = "/llu/auth/login"
    payload = {
        "email": email,
        "password": password
    }

    response = requests.post(BASE_URL + endpoint, headers=HEADERS, json=payload)
    response.raise_for_status()
    data = response.json()
    token = data.get('data', []).get("authTicket", []).get("token", [])  # Access the "token" key from the response JSON
    return token


# Get connections of patient.
def get_patient_connections(token):
    endpoint = "/llu/connections"
    headers = {**HEADERS, 'Authorization': f"Bearer {token}"}

    response = requests.get(BASE_URL + endpoint, headers=headers)
    response.raise_for_status()
    return response.json()


# Retrieve CGM data for a specific patient.
def get_cgm_data(token, patient_id):
    endpoint = f"/llu/connections/{patient_id}/graph"
    headers = {**HEADERS, 'Authorization': f"Bearer {token}"}

    response = requests.get(BASE_URL + endpoint, headers=headers)
    response.raise_for_status()
    return response.json()


# Get data from the CGM sensor through API.
def get_data(email, password):

    token = login(email, password)
    patient_data = get_patient_connections(token)

    patient_id = patient_data['data'][0]["patientId"]
    cgm_data = get_cgm_data(token, patient_id)

    return cgm_data['data']['graphData']