# Import requests module
import requests


class Client:
    def __init__(self, fhir_server=None):
        self.fhir_server = fhir_server
        self.content_type_header = 'application/fhir+json'
        self.accept_header = 'application/fhir+json'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
        }

    def upload_patient_resource(self, json_payload):
        self.headers['Accept'] = self.accept_header
        self.headers['Content-Type'] = self.content_type_header
        fhir_server = self.fhir_server + '/Patient'
        response = requests.post(fhir_server, headers=self.headers, data=json_payload)
        self.status_code_handler(response, 'upload_patient_resource')

        return response

    def get_patient_resource_by_id(self, patient_id):
        self.headers['Accept'] = self.accept_header
        path = '/Patient/' + patient_id
        fhir_server = self.fhir_server + path
        response = requests.get(fhir_server, headers=self.headers)
        self.status_code_handler(response, 'get_patient_resource_by_id')

        return response

    def get_patient_resource_by_search(self, search_param):
        self.headers['Accept'] = self.accept_header
        query_path = '/Patient?' + search_param
        fhir_server = self.fhir_server + query_path
        response = requests.get(fhir_server, headers=self.headers)
        self.status_code_handler(response, 'get_patient_resource_by_search')

        return response

    def update_patient_resource(self, json_payload, patient_id):
        self.headers['Accept'] = self.accept_header
        self.headers['Content-Type'] = self.content_type_header
        fhir_server = self.fhir_server + '/Patient/' + patient_id
        response = requests.put(fhir_server, headers=self.headers, data=json_payload)
        self.status_code_handler(response, 'update_patient_resource')

        return response

    def delete_patient_resource_by_id(self, patient_id):
        self.headers['Accept'] = self.accept_header
        fhir_server = self.fhir_server + '/Patient/' + patient_id
        response = requests.delete(fhir_server, headers=self.headers)
        self.status_code_handler(response, 'delete_patient_resource_by_id')

        return response

    def get_patient_lists(self):
        self.headers['Accept'] = self.accept_header
        fhir_server = self.fhir_server + '/Patient'
        response = requests.get(fhir_server, headers=self.headers)
        self.status_code_handler(response, 'get_patient_lists')

        return response

    def upload_organization_resource(self, json_payload):
        self.headers['Accept'] = self.accept_header
        self.headers['Content-Type'] = self.content_type_header
        fhir_server = self.fhir_server + '/Organization'
        response = requests.post(fhir_server, headers=self.headers, data=json_payload)
        self.status_code_handler(response, 'upload_organization_resource')

        return response

    def get_organization_resource_by_id(self, organization_id):
        self.headers['Accept'] = self.accept_header
        fhir_server = self.fhir_server + '/Organization/' + organization_id
        response = requests.get(fhir_server, headers=self.headers)
        self.status_code_handler(response, 'get_organization_resource_by_id')

        return response

    def upload_immunization_resource(self, json_payload):
        self.headers['Accept'] = self.accept_header
        self.headers['Content-Type'] = self.content_type_header
        fhir_server = self.fhir_server + '/Immunization'
        response = requests.post(fhir_server, headers=self.headers, data=json_payload)
        self.status_code_handler(response, 'upload_immunization_resource')

        return response

    def get_immunization_bundle_resource_by_id(self, immunization_bundle_id):
        self.headers['Accept'] = self.accept_header
        fhir_server = self.fhir_server + '/Bundle/' + immunization_bundle_id
        response = requests.get(fhir_server, headers=self.headers)
        self.status_code_handler(response, 'get_immunization_bundle_resource_by_id')

        return response

    def get_composition_resource_by_id(self, composition_id):
        self.headers['Accept'] = self.accept_header
        fhir_server = self.fhir_server + '/Composition/' + composition_id
        response = requests.get(fhir_server, headers=self.headers)
        self.status_code_handler(response, 'get_composition_resource_by_id')

        return response

    def upload_composition_resource(self, json_payload):
        self.headers['Accept'] = self.accept_header
        self.headers['Content-Type'] = self.content_type_header
        fhir_server = self.fhir_server + '/Composition'
        response = requests.post(fhir_server, headers=self.headers, data=json_payload)
        self.status_code_handler(response, 'upload_composition_resource')

        return response

    def upload_observation_resource(self, json_payload):
        self.headers['Accept'] = self.accept_header
        self.headers['Content-Type'] = self.content_type_header
        fhir_server = self.fhir_server + '/Observation'
        response = requests.post(fhir_server, headers=self.headers, data=json_payload)
        self.status_code_handler(response, 'upload_observation_resource')

        return response

    def get_observation_resource_by_id(self, observation_id):
        self.headers['Accept'] = self.accept_header
        fhir_server = self.fhir_server + '/Observation/' + observation_id
        response = requests.get(fhir_server, headers=self.headers)
        self.status_code_handler(response, 'get_observation_resource_by_id')

        return response

    def upload_bundle_resource(self, json_payload, bundle_name):
        self.headers['Accept'] = self.accept_header
        self.headers['Content-Type'] = self.content_type_header
        fhir_server = self.fhir_server + '/Bundle'
        response = requests.post(fhir_server, headers=self.headers, data=json_payload)
        self.status_code_handler(response, 'upload_bundle_resource(%s)' % bundle_name)

        return response

    def status_code_handler(self, response, method_name):
        if response.status_code != 200 and response.status_code != 201:
            print('Error response when doing ' + method_name + ': ')
            print(response.text)
