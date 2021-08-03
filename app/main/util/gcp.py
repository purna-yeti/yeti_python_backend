from google.cloud import storage
import json
from flask import current_app
from typing import Dict, List
from google.cloud import pubsub_v1
from concurrent import futures
import google.auth
import pdb

credentials, project = google.auth.default()

print(f"GOOGLE CREDENTIALS {credentials}")
print(f"GOOGLE PROJECT {project}")

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
    
    