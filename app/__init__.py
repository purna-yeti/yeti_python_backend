from flask_restx import Api
from flask import Blueprint

# from .main.controller.user_controller import api as user_ns
# from .main.controller.auth_controller import api as auth_ns
# from .main.controller.content_parser_controller import api as content_parser_ns

from .main.controller.reddit_query_controller import api as reddit_query_ns
from .main.controller.reddit_stat_controller import api as reddit_stat_ns


blueprint = Blueprint('api', __name__)
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
    blueprint,
    title='FLASK RESTPLUS(RESTX) API BOILER-PLATE WITH JWT',
    version='1.0',
    description='a boilerplate for flask restplus (restx) web service',
    authorizations=authorizations,
    security='apikey'
)

# api.add_namespace(user_ns, path='/user')
# api.add_namespace(content_parser_ns, path='/content_parser')
# api.add_namespace(auth_ns)

api.add_namespace(reddit_query_ns, path='/reddit_query')
api.add_namespace(reddit_stat_ns, path='/reddit_path')
