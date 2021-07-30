from google.cloud import storage
import json
from flask import current_app
from typing import Dict


class GcpStorage:
    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(
            current_app.config.get('YETI_REDDIT_QUERY_BUCKET_NAME'))

    def create_json(self, json_object: Dict, filename: str) -> Dict[str, str]:
        blob = self.bucket.blob(filename)
        resp = blob.upload_from_string(
            data=json.dumps(json_object),
            content_type='application/json'
        )
        return resp
        
    def get_json(self, filename: str) -> Dict[str, str]:
        blob = self.bucket.get_blob(filename)
        return json.loads(blob.download_as_string())

