# Optional allows the variable to contain 'none' as a value but you can set the data type
from typing import Optional

# Calling the FastAPI library
from fastapi import FastAPI

# Import BaseModel module
from pydantic import BaseModel

# Import FHIR Client
from FHIRClient import Client

# Declaring as the main app to use FastAPI
app = FastAPI()

# Create GET method API at the Root URL when going to the localhost
@app.get('/')
def get_version():
    return {'system': 'hospital-system-server', 'version': '1.0'}

# FHIR Server Data Model
class FHIRModel(BaseModel):
    fhir_server: str

# Create POST method API to set targeted FHIR server
@app.post('/api/fhir_server')
def create_resource(fhir_model: FHIRModel):
    fhir_data = fhir_model.dict()
    print(fhir_data)
    return {}

# Create GET method API and query specific FHIR Resources by id
@app.get('/api/{resource_name}/{unique_id}')
def query_resource_by_id(resource_name: str, unique_id: str):
    return {'resource_name': resource_name, 'unique_id': unique_id}
