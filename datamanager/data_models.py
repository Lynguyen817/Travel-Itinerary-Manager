from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    """Create a user table."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    favorites = db.relationship('Destination', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Destination(db.Model):
    """Create a itinerary table."""
    __tablename__ = 'destination'
    id = db.Column(db.Integer, primary_key=True)
    des_name = db.Column(db.String(120), nullable=False)
    poster_url = db.Column(db.String(200))
    activities = db.Column(db.String(200), nullable=True)
    accommodations = db.Column(db.String(200), nullable=True)
    transportation = db.Column(db.String(200), nullable=True)
    user_id =db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def __repr__(self):
        return f'<Destination {self.des_name}'

