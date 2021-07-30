from .. import db
import datetime
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

class RedditStat(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'reddit_stat'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid4)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    
    query_ = db.Column(db.String(2048), nullable=False, unique=True)
    stat = db.Column(db.JSON, default={})

    def __repr__(self):
        return f'<reddit_stat id:{self.id} query:{self.query_}'
