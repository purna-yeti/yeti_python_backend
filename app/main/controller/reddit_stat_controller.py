from app.main.model.reddit_query import SearchType
from flask import request
from flask_restx import Resource

from ..util.dto import RedditStatDto
from typing import Dict, Tuple
from ..service.reddit_stat_service import (
    query_reddit_stat, handle_reddit_stat_pubsub
)
api = RedditStatDto.api
message = RedditStatDto.message
search_params = RedditStatDto.search_params
reddit_stat = RedditStatDto.reddit_stat

@api.route('/pubsub')
class Pubsub(Resource):
  @api.expect(message, validate=False)
  @api.response(201, 'Reddit Stat pubsub responded')
  @api.doc('Reddit stat pubsub handler')
  def post(self):
    """ Pubsub receiver for reddit stat """
    return handle_reddit_stat_pubsub(request.json)

@api.route('/stat')
class Pubsub(Resource):

  @api.expect(search_params, validate=False)
  @api.marshal_with(reddit_stat)
  @api.response(201, 'Reddit Stat responded')
  @api.doc('Reddit stat query')
  def post(self):
    """ Query reddit stat """
    return query_reddit_stat(request.json)