from flask_restx import Namespace, fields


# class UserDto:
#     api = Namespace('user', description='user related operations')
#     user = api.model('user', {
#         'email': fields.String(required=True, description='user email address'),
#         'username': fields.String(required=True, description='user username'),
#         'password': fields.String(required=True, description='user password'),
#         'public_id': fields.String(description='user Identifier')
#     })


# class AuthDto:
#     api = Namespace('auth', description='authentication related operations')
#     user_auth = api.model('auth_details', {
#         'email': fields.String(required=True, description='The email address'),
#         'password': fields.String(required=True, description='The user password '),
#     })

# class ContentParserDto:
    # api = Namespace('content_parser', description='content parser related operations')


class RedditQueryDto:
    api = Namespace('reddit_query', description='reddit_query related operations')
    search_params = api.model('search_params', {
        'query': fields.String(required=True),
        'before': fields.DateTime(required=True),
    })
    message = api.model('message', {
        'message': fields.String(required=True)
    })

class RedditStatDto:
    api = Namespace('reddit_stat', description='reddit_stat related operations')

    
