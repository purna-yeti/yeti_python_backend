from flask import request
from flask_restx import Resource

from ..util.dto import RedditQueryDto
from ..service.reddit_query_service import (
    save_new_reddit_query, handle_reddit_query_pubsub
)
from typing import Dict, Tuple
from ..model.reddit_query import RedditQuery
from ..model.yb_content import YbContent

api = RedditQueryDto.api
search_params = RedditQueryDto.search_params
message = RedditQueryDto.message

@api.route('/')
class RedditQueryResource(Resource):
    
  @api.expect(search_params, validate=True)
  @api.response(201, 'Reddit Query created')
  @api.doc('Creating new reddit query by query and before')
  def post(self):
    """ Respond reddit query event """
    return save_new_reddit_query(request.json)

  def get(self):
    return "YAY"        

@api.route('/pubsub')
class Pubsub(Resource):
  @api.expect(message, validate=False)
  @api.response(201, 'Reddit Query pubsub responded')
  @api.doc('Reddit query pubsub handler')
  def post(self):
    """ Respond reddit query event """
    # 1. create new reddit query
    # 2. send the next pubsub by moving back the reddit query by a month prior, check if its earlier than EARLIEST 
    return handle_reddit_query_pubsub(request.json['message'])


@api.route('/old')
class RedditQueryOld(Resource):
  def get(self):
    a =  RedditQuery.query.first()
    if a:
      return a.id
    return "EMPTY"

@api.route('/new')
class RedditQueryOld(Resource):
  def get(self):
    a = YbContent.query.first()
    if a:
      return a.id
    return "EMPTY"
