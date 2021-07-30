from .. import db
import datetime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
import enum

class SearchType(enum.Enum):
    SUBMISSION = 1
    COMMENT = 2

class RedditQuery(db.Model):
    """
    Reddit Query Model
    """
    __bind_key__ = 'yeti-python-backend'
    __tablename__ = 'reddit_query'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid4)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    search_type = db.Column(db.Enum(SearchType), nullable=False)
    search_params = db.Column(db.String(8192), nullable=False, unique=True)
    before = db.Column(db.DateTime, nullable=False)
    after = db.Column(db.DateTime, nullable=False)
    query_ = db.Column(db.String(2048), nullable=False)
    limit = db.Column(db.Integer, default=500)
    blob_uri = db.Column(db.String(2048), nullable=False)

    def __repr__(self):
        return f'<reddit_query id:{self.id} query:{self.query_} before: {self.before} after: {self.after}'
