# Calling the FastAPI library
from fastapi import FastAPI, Response, Form, status

# Add CORS middleware module
from fastapi.middleware.cors import CORSMiddleware

# Import BaseModel module
from pydantic import BaseModel

# Import optional body params module
from typing import Optional

# Import requests module
import requests

# Import random module
import random

# Import secrets.token_hex module
from secrets import token_hex

# Import sqlite3 module
import sqlite3

# Import sha3 module
from hashlib import sha3_384

# Import sha3 module
from hashlib import sha256

# Import gettempdir module
from tempfile import gettempdir

# Import FHIR Client class
from FHIRClient.Client import Client

# Import TWCA Client class
from TWCAClient.Client import Client as TWCAClient

# Import json.loads module
from json import loads

# Import base64 decode module
from base64 import b64decode, b64encode

# Import datetime module
from datetime import datetime

# Import qrcode module
import qrcode

# Import ByteIO function
from io import BytesIO

# Import isfile function
from os.path import isfile

# Import uuid4 function
from uuid import uuid4

# Import dumps function
from json import dumps

# Declaring as the main app to use FastAPI
app = FastAPI()

origins = [
    '*',
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['*'], allow_headers=['*'])

# Create GET method API at the Root URL when going to the localhost
@app.get('/')
async def get_version():
    return {'system': 'hospital-system-server', 'version': '1.0'}

# FHIR Server Data Model
class FHIRModel(BaseModel):
    fhir_server: str
    fhir_token: Optional[str] = None

# Create POST method API to set targeted FHIR server
@app.post('/api/fhir_server')
def fhir_server_setup(fhir_model: FHIRModel, response: Response):
    fhir_data = fhir_model.dict()
    if check_json_field(fhir_data, 'fhir_server') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, fhir_sever field is missed.'}

    if check_fhir_server_status(fhir_data['fhir_server']) is False:
        return {'error': 'fhir_server field value is invalid.'}

    store_fhir_server_setting(fhir_data['fhir_server'], fhir_data['fhir_token'])

    if fhir_data['fhir_token'] is not None:
        return {'result': 'fhir_server setting is done!', 'fhir_server': fhir_data['fhir_server'], 'fhir_token': fhir_data['fhir_token']}

    return {'result': 'fhir_server setting is done!', 'fhir_server': fhir_data['fhir_server']}

# Create GET method API to get targeted FHIR server URL
@app.get('/api/fhir_server')
def fhir_server_setup(response: Response):
    fhir_server_info = get_fhir_server_setting()
    if fhir_server_info is False:
        response.status_code = status.HTTP_410_GONE
        return {'error': 'FHIR Server URL is not found or defined. Please use POST /api/fhir_server API firstly.'}

    return {'result': 'Get fhir_server setting is done!', 'fhir_server': fhir_server_info[0], 'fhir_token': fhir_server_info[1]}

# Create GET method API and query specific FHIR Resources by id
@app.get('/api/QueryPatient/{patient_id}')
def query_patient_resource_by_id(patient_id: str, response: Response):
    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}
    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
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

    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.get_patient_resource_by_search(post_data['search_params'])
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

class PatientResourceModel(BaseModel):
    json_payload: str
    patient_id: str

class CreatePatientResourceModel(BaseModel):
    json_payload: str

# Create POST method API to create new Patient Resource
@app.post('/api/CreatePatient')
def create_patient_resource(patient_resource_model: CreatePatientResourceModel, response: Response):
    post_data = patient_resource_model.dict()
    json_payload = b64decode(post_data['json_payload']).decode('utf-8')
    check_result = check_json_str(json_payload)
    if check_result is not True:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return check_result

    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
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

    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.update_patient_resource(json_payload.encode('utf-8'), post_data['patient_id'])
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create DELETE method API to delete existed Patient Resource
@app.delete('/api/DeletePatient/{patient_id}')
def delete_patient_resource(patient_id: str, response: Response):
    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.delete_patient_resource_by_id(patient_id)
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create GET method API to get Patient Resource lists
@app.get('/api/PatientList')
def get_patient_resource(response: Response):
    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
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

    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.upload_organization_resource(json_payload.encode('utf-8'))
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create GET method API to query Organization Resource by id
@app.get('/api/GetOrganization/{organization_id}')
def get_organization_resource_by_id(organization_id: str, response: Response):
    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
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

    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.upload_immunization_resource(json_payload.encode('utf-8'))
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create GET method API to query Immunization Resource by id
@app.get('/api/GetImmunization/{immunization_id}')
def get_immunization_resource_by_id(immunization_id: str, response: Response):
    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.get_immunization_resource_by_id(immunization_id)
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create GET method API to query Composition Resource by id
@app.get('/api/GetComposition/{composition_id}')
def get_composition_resource_by_id(composition_id: str, response: Response):
    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.get_composition_resource_by_id(composition_id)
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

    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.upload_composition_resource(json_payload.encode('utf-8'))
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create GET method API to query Observation Bundle Resource by id
@app.get('/api/GetObservationBundle/{observation_bundle_id}')
def get_observation_bundle_resource_by_id(observation_bundle_id: str, response: Response):
    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.get_observation_bundle_resource_by_id(observation_bundle_id)
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create GET method API to query Observation Resource by id
@app.get('/api/GetObservation/{observation_id}')
def get_observation_resource_by_id(observation_id: str, response: Response):
    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.get_observation_resource_by_id(observation_id)
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

class ObservationResourceModel(BaseModel):
    json_payload: str

# Create POST method API to create composition resource
@app.post('/api/CreateObservation')
def create_observation_resource(observation_resource_model: ObservationResourceModel, response: Response):
    post_data = observation_resource_model.dict()
    json_payload = b64decode(post_data['json_payload']).decode('utf-8')
    if check_json_field(post_data, 'json_payload') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'json_payload is missed.'}
    check_result = check_json_str(json_payload)
    if check_result is not True:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return check_result

    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.upload_observation_resource(json_payload.encode('utf-8'))
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

class BundleResourceModel(BaseModel):
    json_payload: str

# Create POST method API to create immunization or observation bundle resource
@app.post('/api/CreateBundle/{bundle_name}')
def create_bundle_resource(bundle_name, bundle_resource_model: BundleResourceModel, response: Response):
    post_data = bundle_resource_model.dict()
    json_payload = b64decode(post_data['json_payload']).decode('utf-8')
    if check_json_field(post_data, 'json_payload') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'json_payload is missed.'}
    check_result = check_json_str(json_payload)
    if check_result is not True:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return check_result

    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.upload_bundle_resource(json_payload.encode('utf-8'), bundle_name)
    response.status_code = fhir_client_response.status_code
    return loads(fhir_client_response.text)

# Create POST method API to query Immunization bundle:
'''
1. By patient id
2. By patient id and date
3. By organization id and date
'''
@app.post('/api/SearchImmunization')
def query_immunization_resource(search_params_model: FHIRServerSearchParamsModel, response: Response):
    post_data = search_params_model.dict()
    if check_json_field(post_data, 'search_params') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'search_params field is missed.'}

    fhir_server_info = get_fhir_server_setting()
    fhir_server = fhir_server_info[0]
    fhir_token = fhir_server_info[1]
    is_required_auth = fhir_token_existence(fhir_token)

    if fhir_server is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Bad Request, FHIR Server setting is not found. Please use /api/fhir_server API firstly.'}

    fhir_client = Client(fhir_server, is_required_auth, fhir_token)
    fhir_client_response = fhir_client.get_immunization_resource_by_search(post_data['search_params'])
    response.status_code = fhir_client_response.status_code

    return loads(fhir_client_response.text)

# Create GET method API to read hospital list CSV file and get hospital list JSON
@app.get('/api/GetHospitalLists')
def get_hospital_lists():
    file_handler = open('./hospital.csv', 'r')
    line_of_contents = file_handler.readline()
    line_of_contents = file_handler.readline()
    response_json = {
        'hospital_name': [],
        'hospital_number': [],
    }
    while line_of_contents != '':
        line_of_contents = line_of_contents[0:-1].split(',')
        response_json['hospital_number'].append(line_of_contents[0])
        response_json['hospital_name'].append(line_of_contents[1])
        line_of_contents = file_handler.readline()

    file_handler.close()

    return response_json

class RequestRecordModel(BaseModel):
    identifier_number: str
    ip_address: str

# Create POST method API to query Database by specific hashed identifier number
@app.post('/api/GetDatabaseRecord')
def get_database_record(request_record_model: RequestRecordModel, response: Response):
    post_data = request_record_model.dict()
    if check_json_field(post_data, 'identifier_number') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'identifier_number field is missed.'}
    hashed_identifier_number = sha3_384_hash(post_data['identifier_number'])
    query_result = query_database_by_hashed_identified_number(hashed_identifier_number)
    if query_result is False:
        response.status_code = status.HTTP_410_GONE
        return {'error': 'cannot find immunization record'}

    if check_expired_token(query_result[3]) is True:
        query_result = list(query_result)
        query_result[3] = int(datetime.now().timestamp())
        random.seed()
        query_result[4] = sha3_384_hash(str(random.random()) + str(query_result[3]))
        store_fhir_passport_token(query_result)

    return {
        'DoseNumberPositiveInt': query_result[0],
        'lastOccurrenceDate': query_result[1],
        'hashedIdentifierNumber': query_result[2],
        'createdTokenDateTime': query_result[3],
        'Token': query_result[4],
        'base64EncodedImage': generate_qr_code_image(post_data['ip_address'], query_result[4]),
    }

class InsertPassportTokenModel(BaseModel):
    dose_number_positive_int: int
    last_occurrence_date: int
    identifier_number: str
    immunization_id: str

# Create POST method API to insert passport token table
@app.post('/api/InsertDatabaseRecord')
def insert_immunization_record(insert_passport_token_model: InsertPassportTokenModel, response: Response):
    post_data = insert_passport_token_model.dict()
    if check_json_field(post_data, 'dose_number_positive_int') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'dose_number_positive_int field is missed.'}
    if check_json_field(post_data, 'last_occurrence_date') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'last_occurrence_date field is missed.'}
    if check_json_field(post_data, 'identifier_number') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'identifier_number field is missed.'}
    if check_json_field(post_data, 'immunization_id') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'immunization_id field is missed.'}

    hashed_identifier_number = sha3_384_hash(post_data['identifier_number'])
    record = [
        post_data['dose_number_positive_int'],
        post_data['last_occurrence_date'],
        hashed_identifier_number,
        int(datetime.now().timestamp()),
        sha3_384_hash(post_data['immunization_id']),
    ]
    store_fhir_passport_token(record)

    return {'result': 'inserting immunization record is done!'}

# Create POST method API to generate QRCode image with validation URL by identifier number
@app.post('/api/GenerateQRCode')
def generate_qr_code(request_payload_model: RequestRecordModel, response: Response):
    post_data = request_payload_model.dict()
    if check_json_field(post_data, 'identifier_number') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'identifier_number field is missed.'}

    hashed_identifier_number = sha3_384_hash(post_data['identifier_number'])
    query_result = query_database_by_hashed_identified_number(hashed_identifier_number)

    if len(query_result) == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'no record found by this identifier number on this table.'}

    return {
        'dose_number_positive_int': query_result[0],
        'last_occurrence_date': query_result[1],
        'hashed_identifier_number': query_result[2],
        'created_token_date_time': query_result[3],
        'token': query_result[4],
        'base64_encoded_image': generate_qr_code_image(post_data['ip_address'], query_result[4]),
    }

class TokenPayloadModel(BaseModel):
    token: str

# Create POST method API to validate QRCode image token
@app.post('/api/ValidateQRCode')
def validate_qr_code(token_payload_model: TokenPayloadModel, response: Response):
    post_data = token_payload_model.dict()
    if check_json_field(post_data, 'token') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'token field is missed.'}

    query_result = query_database_by_token(post_data['token'])

    if query_result is False:
        response.status_code = status.HTTP_410_GONE
        return {'error': 'no record found by this token on this table.'}

    if check_expired_token(query_result[3]) is True:
        response.status_code = status.HTTP_410_GONE
        return {'error': 'Token is expired.'}

    return {
        'validation_result': 'Success',
    }

class VaccineRegisterModel(BaseModel):
    vaccinePersonName: str
    vaccinePersonEnFirstName: Optional[str] = None
    vaccinePersonEnLastName: Optional[str] = None
    countryName: Optional[str] = None
    identityNumber: str
    doseInputList: str

# Create POST method API to create vaccine register list
@app.post('/api/RegisterVaccine')
def register_vaccine(vaccine_register_model: VaccineRegisterModel, response: Response):
    post_data = vaccine_register_model.dict()
    if check_json_field(post_data, 'vaccinePersonName') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'vaccinePersonName field is missed.'}
    if check_json_field(post_data, 'identityNumber') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'identityNumber field is missed.'}
    if check_json_field(post_data, 'doseInputList') is False:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'doseInputList field is missed.'}

    dose_json_str = b64decode(post_data['doseInputList']).decode('utf-8')
    check_result = check_json_str(dose_json_str)
    if check_result is not True:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return check_result

    dose_list_id = token_hex()
    hashed_identity_number = sha3_384_hash(post_data['identityNumber'])
    user_info = [
        post_data['vaccinePersonName'],
        post_data['vaccinePersonEnFirstName'],
        post_data['vaccinePersonEnLastName'],
        post_data['countryName'],
        hashed_identity_number,
        dose_list_id,
    ]
    fetched_result = query_vaccine_register_exists(hashed_identity_number)
    if fetched_result is not False:
        dose_list_id = fetched_result[0]

    vaccine_record = []
    dose_json_obj = loads(dose_json_str)
    for dose_list in dose_json_obj:
        vaccine_record.append([
            dose_list['doseManufactureName'],
            dose_list['doseNumber'],
            dose_list['vaccinateDateStr'],
            dose_list_id,
        ])

    store_vaccine_register(user_info, vaccine_record, fetched_result)

    return {'result': '成功註冊疫苗紀錄！'}

# Create POST method API to get verified result from TWID Portal
@app.post('/api/VerifyResult')
def verify_result(
        BusinessNo: str = Form(...),
        ApiVersion: str = Form(...),
        HashKeyNo: str = Form(...),
        VerifyNo: str = Form(...),
        MemberNoMapping: str = Form(...),
        Token: str = Form(...),
        CAType: str = Form(...),
        ResultCode: str = Form(...),
        ReturnCode: str = Form(...),
        ReturnCodeDesc: str = Form(...),
        IdentifyNo: str = Form(...),
    ):
    return {
        'BusinessNo': BusinessNo,
        'ApiVersion': ApiVersion,
        'HashKeyNo': HashKeyNo,
        'VerifyNo': VerifyNo,
        'MemberNoMapping': MemberNoMapping,
        'Token': Token,
        'CAType': CAType,
        'ResultCode': ResultCode,
        'ReturnCode': ReturnCode,
        'ReturnCodeDesc': ReturnCodeDesc,
        'IdentifyNo': IdentifyNo,
    }

class LoginTWIDPortalModel(BaseModel):
    member_no: str
    action: str
    plain_text: str
    ca_type: str
    assign_cert_password: str
    operator: str
    msisdn: str
    birthday: str
    return_url: str

# Create POST method API to login TWID Portal
@app.post('/api/LoginTWIDPortal')
def login_twid_portal(login_twid_portal_model: LoginTWIDPortalModel, response: Response):
    portal_server = 'https://midonlinetest.twca.com.tw/IDPortal/Login'
    twca_client = TWCAClient(portal_server)
    twca_config = get_twca_config()
    if 'error' in twca_config.keys():
        response.status_code = status.HTTP_400_BAD_REQUEST

        return twca_config

    post_data = login_twid_portal_model.dict()
    input_params = {
        'MemberNo': post_data['member_no'],
        'Action': post_data['action'],
        'Plaintext': post_data['member_no'],
        'CAType': post_data['ca_type'],
        'AssignCertPassword': post_data['assign_cert_password'],
        'MIDInputParams': {
            'Platform': '2',
            'MIDwInputParams': {
                'Operator': post_data['operator'],
                'Msisdn': post_data['msisdn'],
                'Birthday': post_data['birthday'],
            },
        },
    }
    verify_no = get_verify_no()
    return_params = ''
    api_version = '1.0'
    plain_text = twca_config['business_no'] + api_version + twca_config['hash_key_no'] + verify_no + return_params + dumps(input_params) + twca_config['hash_key']
    payload = {
        'BusinessNo': twca_config['business_no'],
        'ApiVersion': '1.0',
        'HashKeyNo': twca_config['hash_key_no'],
        'VerifyNo': verify_no,
        'ReturnURL': post_data['return_url'],
        'ReturnParams': '',
        'IdentifyNo': identify_generator(plain_text),
        'InputParams': dumps(input_params),
    }

    token_response = twca_client.login_portal(payload)
    if token_response['ReturnCode'] != '0':
        return token_response

    output_params = loads(token_response['OutputParams'])
    token = output_params['Token']
    plain_text = twca_config['business_no'] + api_version + twca_config['hash_key_no'] + verify_no + token + twca_config['hash_key']
    token_response['IdentifyNo'] = sha256(plain_text).hexdigest()

    return token_response

def generate_qr_code_image(ip_address, hashed_token):
    validation_url = ip_address + '/validate?token=' + hashed_token
    image = qrcode.make(validation_url)
    output_binary = BytesIO()
    image.save(output_binary, format='PNG')

    return b64encode(output_binary.getvalue())

def check_expired_token(created_token_time):
    return (int(datetime.now().timestamp()) - int(created_token_time)) > 180

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

def create_vaccine_register_table():
    db_conn = sqlite3.connect(gettempdir() + '/hospital_system_server.sqlite3')
    db_conn.cursor()
    db_conn.execute('''
        CREATE TABLE IF NOT EXISTS "vaccine_register"(
            [RegisterId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [VaccinePersonName] NVARCHAR(100) NOT NULL,
            [VaccinePersonFirstName] NVARCHAR(100) NULL,
            [VaccinePersonLastName] NVARCHAR(100) NULL,
            [CountryName] NVARCHAR(100) NULL,
            [IdentityNumber] NVARCHAR(100) NOT NULL,
            [DoseListId] NVARCHAR(100) NOT NULL
        )
    ''')
    db_conn.commit()

    db_conn.execute('''
        CREATE TABLE IF NOT EXISTS "vaccine_dose_lists"(
            [ListId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [DoseManufactureName] NVARCHAR(50) NOT NULL,
            [DoseNumber] INT NOT NULL,
            [VaccineDate] NVARCHAR(50) NOT NULL,
            [DoseListId] NVARCHAR(100) NOT NULL,
            CONSTRAINT fk_dose_list_id
                FOREIGN KEY (DoseListId)
                REFERENCES vaccine_register(DoseListId)
        )
    ''')
    db_conn.commit()
    db_conn.close()
    return True

def create_fhir_server_table():
    db_conn = sqlite3.connect(gettempdir() + '/hospital_system_server.sqlite3')
    db_conn.cursor()
    db_conn.execute('''
        CREATE TABLE IF NOT EXISTS "fhir_server"(
            [ServerId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [Server] NVARCHAR(100) NOT NULL,
            [Token] NVARCHAR(100) NULL
        )
    ''')
    db_conn.commit()
    db_conn.close()
    return True

def create_fhir_passport_table():
    db_conn = sqlite3.connect(gettempdir() + '/healthy_passport.sqlite3')
    db_conn.cursor()
    db_conn.execute('''
        CREATE TABLE IF NOT EXISTS "passport_token"(
            [PassportId] INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            [DoseNumberPositiveInt] TINYINT NOT NULL,
            [lastOccurrenceDate] NVARCHAR(15) NOT NULL,
            [hashedIdentifierNumber] NVARCHAR(150) NOT NULL,
            [createdTokenDateTime] INT NOT NULL,
            [Token] NVARCHAR(200) NULL
        )
    ''')
    db_conn.commit()
    db_conn.close()
    return True

def store_fhir_passport_token(record):
    create_fhir_passport_table()
    db_conn = sqlite3.connect(gettempdir() + '/healthy_passport.sqlite3')
    db_conn.cursor()
    db_conn.execute(
        '''
            DELETE FROM passport_token WHERE hashedIdentifierNumber = ?
        ''',
        [record[2]]
    )
    db_conn.execute(
        '''
        INSERT INTO passport_token
        (
            DoseNumberPositiveInt,
            lastOccurrenceDate,
            hashedIdentifierNumber,
            createdTokenDateTime,
            Token
        )
        VALUES (?, ?, ?, ?, ?)
        ''',
        record
    )
    db_conn.commit()
    db_conn.close()
    return True

def store_fhir_server_setting(fhir_server, fhir_token=None):
    create_fhir_server_table()
    db_conn = sqlite3.connect(gettempdir() + '/hospital_system_server.sqlite3')
    db_conn.cursor()

    db_conn.execute('DELETE FROM fhir_server')
    db_conn.commit()

    if fhir_token is None:
        db_conn.execute('INSERT INTO fhir_server(Server) VALUES (?)', [fhir_server])
    else:
        db_conn.execute('INSERT INTO fhir_server(Server, Token) VALUES (?, ?)', [fhir_server, fhir_token])
    db_conn.commit()
    db_conn.close()
    return True

def query_vaccine_register_exists(identity_number):
    create_vaccine_register_table()
    db_conn = sqlite3.connect(gettempdir() + '/hospital_system_server.sqlite3')
    db_conn.cursor()
    fetched_obj = db_conn.execute('''
        SELECT DoseListId FROM vaccine_register WHERE
        IdentityNumber = ?
    ''', [identity_number])
    fetched_result = fetched_obj.fetchone()
    db_conn.close()

    if fetched_result is None:
        return False

    return fetched_result

def store_vaccine_register(user_info, vaccine_records, fetched_result):
    create_vaccine_register_table()
    db_conn = sqlite3.connect(gettempdir() + '/hospital_system_server.sqlite3')
    db_conn.cursor()
    if fetched_result is False:
        db_conn.execute('''
            INSERT INTO vaccine_register(
                VaccinePersonName,
                VaccinePersonFirstName,
                VaccinePersonLastName,
                CountryName,
                IdentityNumber,
                DoseListId
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', user_info)
        db_conn.commit()

    for vaccine_record in vaccine_records:
        db_conn.execute('''
            INSERT INTO vaccine_dose_lists(
                DoseManufactureName, DoseNumber, VaccineDate, DoseListId
            ) VALUES (?, ?, ?, ?)
        ''', vaccine_record)
        db_conn.commit()

    db_conn.close()
    return True

def query_database_by_token(token):
    create_fhir_passport_table()
    db_conn = sqlite3.connect(gettempdir() + '/healthy_passport.sqlite3')
    db_conn.cursor()
    fetched_obj = db_conn.execute(
        '''
        SELECT
            DoseNumberPositiveInt,
            lastOccurrenceDate,
            hashedIdentifierNumber,
            createdTokenDateTime,
            Token
        FROM passport_token WHERE Token=? ORDER BY PassportId DESC LIMIT 1
        ''', [token])
    fetched_result = fetched_obj.fetchone()
    db_conn.close()

    if fetched_result is None:
        return False

    return fetched_result

def query_database_by_hashed_identified_number(hashed_identifier_number):
    create_fhir_passport_table()
    db_conn = sqlite3.connect(gettempdir() + '/healthy_passport.sqlite3')
    db_conn.cursor()
    fetched_obj = db_conn.execute(
        '''
        SELECT
            DoseNumberPositiveInt,
            lastOccurrenceDate,
            hashedIdentifierNumber,
            createdTokenDateTime,
            Token
        FROM passport_token WHERE hashedIdentifierNumber=? ORDER BY PassportId DESC LIMIT 1
        ''', [hashed_identifier_number])
    fetched_result = fetched_obj.fetchone()
    db_conn.close()

    if fetched_result is None:
        return False

    return fetched_result

def get_fhir_server_setting():
    create_fhir_server_table()
    db_conn = sqlite3.connect(gettempdir() + '/hospital_system_server.sqlite3')
    db_conn.cursor()
    fetched_obj = db_conn.execute('SELECT Server,Token FROM fhir_server ORDER BY ServerId DESC LIMIT 1')
    fetched_result = fetched_obj.fetchone()
    db_conn.close()

    if fetched_result is None:
        return False
    return fetched_result

def fhir_token_existence(fhir_token):
    return fhir_token is not None

def sha3_384_hash(identifier_number):
    return sha3_384(str(identifier_number).encode('utf-8')).hexdigest()

def get_twca_config():
    default_config_path = './config.txt'
    if isfile(default_config_path) is False:
        return {
            'error': 'config.txt file is not found',
        }

    with open(default_config_path, 'r') as file_handler:
        contents = file_handler.read().split('\n')
        business_no = contents[0].split(':')[1]
        hash_key = contents[1].split(':')[1]
        hash_key_no = contents[2].split(':')[1]

    return {
        'business_no': business_no,
        'hash_key': hash_key,
        'hash_key_no': hash_key_no,
    }

def get_verify_no():
    return str(uuid4())

def store_verify_no(verify_no):
    return True

def identify_generator(plain_text):
    encoded = plain_text.encode('utf-16le')
    hashed = sha256(encoded)

    return hashed.hexdigest()
