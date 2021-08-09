from urllib.parse import urlencode
from google.cloud import storage
import json
from flask import current_app
from typing import Dict, List
from google.cloud import pubsub_v1
from concurrent import futures
import google.auth
from base64 import b64decode
import os
from copy import deepcopy
from pathlib import Path
from tqdm import tqdm
import time
import pdb

credentials, project = google.auth.default()

# print(f"GOOGLE CREDENTIALS {credentials}")
# print(f"GOOGLE PROJECT {project}")

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

  def save_reddit_query(self, json_object: Dict, search_params: Dict[str, str]):
    parameters = deepcopy(search_params)
    query = parameters['query_']
    del parameters['query_']
    fn = f'{ urlencode({"query_": query}) }/{ urlencode(parameters) }.json'
    self.create_json(json_object, fn)

    return fn
      

  def download_batch(self, query: str, gcloud_cli: bool=False):
    enc_folder = urlencode({'query_': query})
    pattern = f"{ enc_folder }/"
    tmp_dir = f"{current_app.config.get('YETI_REDDIT_QUERY_TEMP_FOLDER')}/{enc_folder}"
    Path(tmp_dir).mkdir(parents=True, exist_ok=True)
    
    if gcloud_cli:
      source_dir = f"gs://{ current_app.config.get('YETI_REDDIT_QUERY_BUCKET_NAME') }/{ pattern }"
      download_command = f"""
      gsutil -m rsync -r -d '{source_dir}' '{tmp_dir}'
      """
      current_app.logger.info(download_command)
      os.system(download_command)
    else:
      blobs = self.bucket.list_blobs(prefix=pattern)
      for blob in tqdm(blobs):
        target_path = f"{ tmp_dir }/{ blob.name.split('/')[1] }"
        if not Path(target_path).is_file():
          blob.download_to_filename(target_path)
    return tmp_dir


class PubSub:
  def __init__(self, topic_id):
    self.publisher = pubsub_v1.PublisherClient()
    self.topic_path = self.publisher.topic_path(current_app.config.get('PROJECT_ID'), topic_id)

  def send_messages(self, messages: List[str]):
    publish_futures = []

    def get_callback(publish_future, data):
      def callback(publish_future):
        try:
          # Wait 60 seconds for the publish call to succeed.
          print(publish_future.result(timeout=60))
        except futures.TimeoutError:
          print(f"Publishing {data} timed out.")
      return callback
    
    for data in messages:
      # When you publish a message, the client returns a future.
      publish_future = self.publisher.publish(self.topic_path, data.encode("utf-8"))
      # Non-blocking. Publish failures are handled in the callback function.
      publish_future.add_done_callback(get_callback(publish_future, data))
      publish_futures.append(publish_future)

    # Wait for all the publish futures to resolve before exiting.
    return futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)
    
  def decode(data: Dict[str, str]) -> str:
    if current_app.config.get('ENV') == 'local':
      return
    data['message']['data'] = b64decode(data['message']['data']).decode('utf-8')
