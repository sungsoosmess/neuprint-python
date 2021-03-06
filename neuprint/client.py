import os
import json
import requests
import pandas as pd


class Client:
    def __init__(self, server, token=None):
        if token is None:
            token = os.environ.get('NEUPRINT_APPLICATION_CREDENTIALS')
        
        if token is None:
            raise RuntimeError("No token provided.  Please provide one or set NEUPRINT_APPLICATION_CREDENTIALS")

        if ':' in token:
            try:
                token = json.loads(token)['token']
            except Exception:
                raise RuntimeError("Did not understand token.  Please provide the entire JSON document or (only) the complete token string")
            
        token = token.replace('"', '')

        if '://' not in server:
            server = 'https://' + server
        elif server.startswith('http://'):
            raise RuntimeError("Server must be https, not http")
        elif not server.startswith('https://'):
            raise RuntimeError(f"Unknown protocol: {server.split('://')[0]}")

        self.server = server
        self.session = requests.Session()        
        self.session.headers.update({ "Authorization": "Bearer " + token,
                                      "Content-type": "application/json"} )
    
    def _fetch_raw(self, url, json=None):
        r = self.session.get(url, json=json)
        r.raise_for_status()
        return r.content

    
    def _fetch_json(self, url, json=None):
        r = self.session.get(url, json=json)
        r.raise_for_status()
        return r.json()


    def fetch_help(self):
        return self._fetch_json(f"{self.server}/api/help")


    def fetch_version(self):
        return self._fetch_json(f"{self.server}/api/version")


    def fetch_available(self):
        return self._fetch_json(f"{self.server}/api/available")
    

    def fetch_database(self):
        return self._fetch_json(f"{self.server}/api/dbmeta/database")


    def fetch_datasets(self):
        return self._fetch_json(f"{self.server}/api/dbmeta/datasets")


    def fetch_custom(self, cypher, format='pandas'):
        assert format in ('json', 'pandas')
        result = self._fetch_json(f"{self.server}/api/custom/custom", json={"cypher": cypher})
        if format == 'json':
            return result
        
        df = pd.DataFrame(result['data'], columns=result['columns'])
        return df

