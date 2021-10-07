# Calling the FastAPI library
from fastapi import FastAPI, Response, status

# Import BaseModel module
from pydantic import BaseModel

# Import requests module
import requests

# Import sqlite3 module
import sqlite3

# Import gettempdir module
from tempfile import gettempdir

# Import FHIR Client class
from FHIRClient.Client import Client

# Import json.loads module
from json import loads

# Import base64 decode module
from base64 import b64decode

# Declaring as the main app to use FastAPI
app = FastAPI()

# Create GET method API at the Root URL when going to the localhost
@app.get('/')
async def get_version():
    return {'system': 'hospital-system-server', 'version': '1.0'}

# FHIR Server Data Model
class FHIRModel(BaseModel):
    fhir_server: str

# Create POST method API to set targeted FHIR server
@app.post('/api/fhir_server')
def fhir_server_setup(fhir_model: FHIRModel, response: Response):
    fhir_data = fhir_model.dict()
    if check_json_field(fhir_data, 'fhir_server') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, fhir_sever field is missed.'}

    if check_fhir_server_status(fhir_data['fhir_server']) is False:
        return {'error': 'fhir_server field value is invalid.'}

    store_fhir_server_setting(fhir_data['fhir_server'])

    return {'result': 'fhir_server setting is done!', 'fhir_server': fhir_data['fhir_server']}

# Create GET method API and query specific FHIR Resources by id
@app.get('/api/QueryPatient/{patient_id}')
def query_patient_resource_by_id(patient_id: str, response: Response):
    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}
    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.get_patient_resource_by_id(patient_id)
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# FHIR Server Search Params Model
class FHIRServerSearchParamsModel(BaseModel):
    search_params: str

# Create POST method API to query Patient Resources by searching params
@app.post('/api/SearchPatient')
def query_patient_resource_by_search_params(search_params_model: FHIRServerSearchParamsModel, response: Response):
    post_data = search_params_model.dict()
    if check_json_field(post_data, 'search_params') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'search_params field is missed.'}

    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.get_patient_resource_by_search(post_data['search_params'])
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

class PatientResourceModel(BaseModel):
    json_payload: str
    patient_id: str

# Create POST method API to create new Patient Resource
@app.post('/api/CreatePatient')
def create_patient_resource(patient_resource_model: PatientResourceModel, response: Response):
    post_data = patient_resource_model.dict()
    json_payload = b64decode(post_data['json_payload']).decode('utf-8')
    check_result = check_json_str(json_payload)
    if check_result is not True:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return check_result

    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.upload_patient_resource(json_payload.encode('utf-8'))
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create PUT method API to update existed Patient Resource
@app.put('/api/UpdatePatient')
def update_patient_resource(patient_resource_model: PatientResourceModel, response: Response):
    post_data = patient_resource_model.dict()
    json_payload = b64decode(post_data['json_payload']).decode('utf-8')
    if check_json_field(post_data, 'json_payload') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'json_payload field is missed.'}
    check_result = check_json_str(json_payload)
    if check_result is not True:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return check_result

    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.update_patient_resource(json_payload.encode('utf-8'), post_data['patient_id'])
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create DELETE method API to delete existed Patient Resource
@app.delete('/api/DeletePatient/{patient_id}')
def delete_patient_resource(patient_id: str, response: Response):
    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.delete_patient_resource_by_id(patient_id)
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create GET method API to get Patient Resource lists
@app.get('/api/PatientList')
def get_patient_resource(response: Response):
    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.get_patient_lists()
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

class OrganizationResourceModel(BaseModel):
    json_payload: str

# Create POST method API to create Organization Resource
@app.post('/api/CreateOrganization')
def create_organization_resource(org_resource_model: OrganizationResourceModel, response: Response):
    post_data = org_resource_model.dict()
    json_payload = b64decode(post_data['json_payload']).decode('utf-8')
    if check_json_field(post_data, 'json_payload') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'json_payload is missed.'}
    check_result = check_json_str(json_payload)
    if check_result is not True:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return check_result

    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.upload_organization_resource(json_payload.encode('utf-8'))
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create GET method API to query Organization Resource by id
@app.get('/api/GetOrganization/{organization_id}')
def get_organization_resource_by_id(organization_id: str, response: Response):
    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.get_organization_resource_by_id(organization_id)
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

class ImmunizationResourceModel(BaseModel):
    json_payload: str

# Create POST method API to create immunization resource bundle
@app.post('/api/CreateImmunization')
def create_immunization_resource(immunization_resource_model: ImmunizationResourceModel, response: Response):
    post_data = immunization_resource_model.dict()
    json_payload = b64decode(post_data['json_payload']).decode('utf-8')
    if check_json_field(post_data, 'json_payload') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'json_payload is missed.'}
    check_result = check_json_str(json_payload)
    if check_result is not True:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return check_result

    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.upload_immunization_resource(json_payload.encode('utf-8'))
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create GET method API to query Immunization Resource by id
@app.get('/api/GetImmunization/{immunization_id}')
def get_immunization_resource_by_id(immunization_id: str, response: Response):
    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.get_immunization_resource_by_id(immunization_id)
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

class CompositionResourceModel(BaseModel):
    json_payload: str

# Create POST method API to create composition resource
@app.post('/api/CreateComposition')
def create_compposition_resource(composition_resource_model: CompositionResourceModel, response: Response):
    post_data = composition_resource_model.dict()
    json_payload = b64decode(post_data['json_payload']).decode('utf-8')
    if check_json_field(post_data, 'json_payload') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'json_payload is missed.'}
    check_result = check_json_str(json_payload)
    if check_result is not True:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return check_result

    fhir_server = get_fhir_server_setting()
    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server)
    fhir_client_response = fhir_client.upload_composition_resource(json_payload.encode('utf-8'))
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

def check_fhir_server_status(fhir_server):
    try:
        requests.get(fhir_server)
    except ValueError:
        return False

    return True

def check_json_str(json_payload):
    try:
        loads(json_payload)
    except ValueError:
        return {'error': 'json_payload filed value is invalid'}

    return True

def check_json_field(post_data, key_name):
    return key_name in list(post_data.keys())

def create_fhir_server_table():
    db_conn = sqlite3.connect(gettempdir() + '/hospital_system_server.sqlite3')
    db_conn.cursor()
    db_conn.execute('''
        CREATE TABLE IF NOT EXISTS "fhir_server"(
            [ServerId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [Server] NVARCHAR(100) NOT NULL
        )
    ''')
    db_conn.commit()
    db_conn.close()
    return True

def store_fhir_server_setting(fhir_server):
    create_fhir_server_table()
    db_conn = sqlite3.connect(gettempdir() + '/hospital_system_server.sqlite3')
    db_conn.execute('INSERT INTO fhir_server(Server) VALUES (?)', [fhir_server])
    db_conn.commit()
    db_conn.close()
    return True

def get_fhir_server_setting():
    create_fhir_server_table()
    db_conn = sqlite3.connect(gettempdir() + '/hospital_system_server.sqlite3')
    db_conn.cursor()
    fetched_obj = db_conn.execute('SELECT Server FROM fhir_server ORDER BY ServerId DESC LIMIT 1')
    fetched_result = fetched_obj.fetchone()
    db_conn.close()

    if len(fetched_result) == 0:
        return False
    return fetched_result[0]
