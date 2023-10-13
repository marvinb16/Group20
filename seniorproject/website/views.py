import datetime

from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Post
from . import db
import json
from .api import get_latest_api_call, fetch_farmers_market_data, get_market_data, create_or_update_market
from .models import FarmersMarket, Comment


views = Blueprint('views', __name__)

api_response = None
@views.route('/')
def index():
    
    return render_template("index.html", activeUser = current_user)

@views.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if request.method == 'POST':
        post = request.form.get('post')

        if len(post) < 10:
            flash('Posts must be atleast 10 characters', category = "error")
        else:
            new_post = Post(text=post, userId=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            flash("Post successful.", category="success")
    return render_template("post.html", activeUser = current_user)

@views.route('/search', methods=['GET', 'POST'])
def search():
    global api_response

    if request.method == 'POST':
        zipcode = request.form.get('zipcode')
        radius = request.form.get('radius')

        # Check if zipcode is empty
        if not zipcode or not zipcode.isdigit() or len(zipcode) != 5:
            flash("Please enter a valid zipcode.", category="error")
            return render_template("search.html", activeUser=current_user)

        # Call the API function from api.py
        api_response = fetch_farmers_market_data(zipcode, radius)



    return render_template("search.html", api_response=api_response, activeUser=current_user)

@views.route('/feedback')
@login_required
def feedback():
    return render_template("feedback.html", activeUser = current_user)

@views.route('/deletepost', methods=['POST'])
def delete_post():
    post = json.loads(request.data)
    postId = post['postId']
    post = Post.query.get(postId)
    if post:
        if post.userId == current_user.id:
            db.session.delete(post)
            db.session.commit()
    
    return jsonify({})

@views.route('/market/<listing_id>', methods=['GET', 'POST'])
def market_detail(listing_id):
    # Check if the market exists, if not create it
    api_data = get_market_data(listing_id)
    #print(api_data)

    if api_data is None:
        flash("Failed to fetch market data.", category="error")
        return redirect(url_for('views.search'))  # Redirect to the search page


    # Create or update the market based on the API data
    market = create_or_update_market(api_data)
    #print(market)
    # Fetch comments associated with the market
    comments = Comment.query.filter_by(listing_id=listing_id).all()
    if len(comments) <= 0:
        comments = None


    if request.method == 'POST':
        comment_text = request.form.get('comment_text')
        if comment_text:
            new_comment = Comment(text=comment_text, user_id=current_user.id, listing_id=listing_id)
            db.session.add(new_comment)
            db.session.commit()
            flash("New comment added.", category="success")
            comments = Comment.query.filter_by(listing_id=listing_id).all()
            if len(comments) <= 0:
                comments = None

    return render_template("market_detail.html", market=market, comments=comments, activeUser = current_user)