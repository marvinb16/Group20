from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    posts = db.relationship('Post', backref='user', lazy=True)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref='comments')
    listing_id = db.Column(db.String(20), db.ForeignKey('farmers_market.listing_id'), nullable=False)
    farmers_market = db.relationship('FarmersMarket', backref='comments')


class FarmersMarket(db.Model):
    __tablename__ = 'farmers_market'

    listing_id = db.Column(db.String(20), primary_key=True)  # listing_id as the primary key
    listing_name = db.Column(db.String(100))
    listing_desc = db.Column(db.String(10000))
    contact_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    media_website = db.Column(db.String(200))
    media_facebook = db.Column(db.String(200))
    media_twitter = db.Column(db.String(200))
    media_instagram = db.Column(db.String(200))
    media_pinterest = db.Column(db.String(200))
    media_youtube = db.Column(db.String(200))
    media_blog = db.Column(db.String(200))
    location_address = db.Column(db.String(200))
    location_state = db.Column(db.String(50))
    location_city = db.Column(db.String(50))
    location_street = db.Column(db.String(200))
    location_zipcode = db.Column(db.String(20))

