import datetime
import enum
import sys
from flask_login import UserMixin

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from app import app


db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    profile_pic = db.Column(db.String, nullable=True)

    def __init__(self, id, name, email, profile_pic):
        self.id = id
        self.name = name
        self.email = email
        self.profile_pic = profile_pic


class EmbeddedIndex(db.Model):
    __tablename__ = "embedded_index"

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, id, user_id):
        self.id = id
        self.user_id = user_id


class ModelStatus(enum.Enum):
    IN_PROGRESS = "製作中"
    SUCCESS = "制作成功"
    FAILURE = "制作失敗"


class Model(db.Model):
    __tablename__ = "model"
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    status = db.Column(
        Enum(ModelStatus), default=ModelStatus.IN_PROGRESS, nullable=False
    )

    def __init__(self, id, name, user_id):
        self.id = id
        self.name = name
        self.user_id = user_id


model_embedded_index = db.Table(
    "model_embedded_index",
    db.Model.metadata,
    db.Column("model_id", db.Integer, db.ForeignKey("model.id")),
    db.Column("embedded_index_id", db.Integer, db.ForeignKey("embedded_index.id")),
)

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2 and args[1] == "init":
        with app.app_context():
            db.create_all()
    elif len(args) == 2 and args[1] == "drop":
        with app.app_context():
            db.drop_all()
