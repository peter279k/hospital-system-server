# Import requests module
import requests


class Client:
    def __init__(self, fhir_server):
        self.fhir_server = fhir_server
        self.content_type_header = 'application/fhir+json'
        self.accept_header = 'application/fhir+json'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
        }

    def upload_patient_resource(self, json_payload):
        self.headers['Accept'] = self.accept_header
        self.headers['Content-Type'] = self.content_type_header
        response = requests.post(self.fhir_server, headers=self.headers, data=json_payload)

        return response.text

    def get_patient_resource_by_id(self, patient_id):
        self.headers['Accept'] = self.accept_header
        path = '/Patient/' + patient_id
        fhir_server = self.fhir_server + path
        response = requests.get(fhir_server, headers=self.headers)

        return response.text

    def get_patient_resource_by_search(self, search_param):
        self.headers['Accept'] = self.accept_header
        query_path = '/Patient?' + search_param
        fhir_server = self.fhir_server + query_path
        response = requests.get(fhir_server, headers=self.headers)

        return response.text

    def status_code_handler(self, response):
        if response.status_code != 200:
            print('Error response: ')
            print(response.text)

        return response
