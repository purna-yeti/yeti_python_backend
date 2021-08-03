from app.main import db
from app.main.model.reddit_query import RedditQuery, SearchType
from typing import Dict, Tuple
from flask import current_app
from app.main.util.gcp import GcpStorage, PubSub
from app.main.util.helper import get_first_day_of_month
from app.main.util.reddit_psaw import PSAW
from dateutil.relativedelta import relativedelta
from urllib.parse import urlencode, parse_qsl
from base64 import b64decode
import pdb


def save_new_reddit_query(data: Dict[str, str]) -> Tuple[Dict[str, str], int]:
  # adjust before after status to first day of the month
  # check if reddit query entry already exist for SUBMISSION and COMMENT, 
  # if NOT exist, then create new one
  # if both exist, return error 409
  prefix = "save_new_reddit_query:: "
  current_app.logger.info(f'{prefix} start')
  before = get_first_day_of_month(data['before'])
  after = before - relativedelta(months=1)
  if after < current_app.config.get('REDDIT_QUERY_EARLIEST'):
    return dict(
      status='success',
      message='after date is beyond earliest'
    ), 201
  
  success = False
  for search_type in SearchType.__members__:
    search_params = dict(
      before=before,
      after=after,
      query_=data['query'],
      search_type=search_type,
      limit=current_app.config.get('REDDIT_QUERY_PARAM_LIMIT')
    )
    search_params_encode = urlencode(search_params)
    reddit_query = (RedditQuery
      .query
      .with_entities(RedditQuery.id)
      .filter_by(search_params=search_params_encode)
      .first())

    if not reddit_query:
      search_result = PSAW().search(**search_params)
      resp = GcpStorage().create_json(search_result, f"{search_params_encode}.json")
      new_reddit_query = RedditQuery(
        search_params=search_params_encode,
        blob_uri=f"{current_app.config.get('GOOGLE_CLOUD_STORAGE_HOST')}/{current_app.config.get('YETI_REDDIT_QUERY_BUCKET_NAME')}/{search_params_encode}",        
        **search_params
      )
      db.session.add(new_reddit_query)
      success = True
  if not success:
    current_app.logger.info(f'{prefix} end')
    return dict(
      status='fail',
      message='Reddit query already exists.',
    ), 409
  db.session.commit()
  current_app.logger.info(f'{prefix} end')
  return {}, 201


def handle_reddit_query_pubsub(message: str) -> Tuple[Dict[str, str], int]:
  prefix = "handle_reddit_query_pubsub:: "
  current_app.logger.info(f'{prefix} start')
  data = dict(parse_qsl(b64decode(message['data']).decode('utf-8')))
  _, status = save_new_reddit_query(data)
  before = get_first_day_of_month(data['before'])
  after = before - relativedelta(months=1)
  if after < current_app.config.get('REDDIT_QUERY_EARLIEST'):
    current_app.logger.info(f'{prefix} end')
    return dict(
      status='success',
      message='after date is beyond earliest'
    ), 201
  resp = PubSub(current_app.config.get('YETI_REDDIT_QUERY_TOPIC')).send_messages(
    [urlencode(dict(
      query=data['query'],
      before=after
    ))]
  )
  current_app.logger.info(f'{prefix} end')

  return {}, 201


def save_changes(data: RedditQuery) -> None:
  db.session.add(data)
  db.session.commit()