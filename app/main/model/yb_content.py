from .. import db
from sqlalchemy.dialects.postgresql import UUID


class YbContent(db.Model):
    __bind_key__ = 'yeti_backend'
    __tablename__ = 'contents'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True))
    uri = db.Column(db.String(2048))