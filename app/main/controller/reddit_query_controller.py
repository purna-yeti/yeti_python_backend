from flask import request
from flask_restx import Resource

from ..util.dto import RedditQueryDto
from ..service.reddit_query_service import save_new_reddit_query
from typing import Dict, Tuple


api = RedditQueryDto.api
search_params = RedditQueryDto.search_params


@api.route('/')
class RedditQuery(Resource):
    
    @api.expect(search_params, validate=True)
    @api.response(201, 'Reddit Query responded')
    @api.doc('Reddit query handler')
    def post(self):
        """ Respond reddit query event """
        return save_new_reddit_query(request.json)
        

