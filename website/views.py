import datetime

from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from flask_mail import Mail, Message
from .models import FarmersMarket, Comment, UserMarketVisit, ZipSearches, Post, User, PageViews
from .forms import FeedbackForm
from . import mail
from . import db
import json
from .api import get_latest_api_call, fetch_farmers_market_data, get_market_data, create_or_update_market
from .models import FarmersMarket, Comment
import requests
import time


views = Blueprint('views', __name__)

api_response = None
@views.route('/')
def index():
    recommended_market_ids = []
    if current_user.is_authenticated:
        recommended_market_ids = recommend_markets_for_user(current_user.id)
    
    recommended_markets = FarmersMarket.query.filter(FarmersMarket.listing_id.in_(recommended_market_ids)).all()
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
        try:
            # Call the API function from api.py
            api_response = fetch_farmers_market_data(zipcode, radius)
            #print("DEBUG SEARCH CALL: ", api_response)
        except Exception as e:
            flash(f"An error occurred: Please check if {zipcode} is a valid zip code.", category="error")
            api_response = {}  # Reset api_response in case of an error

        if current_user.is_authenticated:
            zip_search = ZipSearches(zip_code=zipcode, user_id=current_user.id, timestamp=datetime.datetime.now())
            db.session.add(zip_search)
            db.session.commit()


    return render_template("search.html", api_response=api_response, activeUser=current_user)

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

@views.route('/deletecomment', methods=['POST'])
def delete_comment():
    comment = json.loads(request.data)
    commentId = comment['commentId']
    comment = Comment.query.get(commentId)
    if comment:
        if comment.user_id == current_user.id:
            db.session.delete(comment)
            db.session.commit()
    
    return jsonify({})


@views.route('/market/<listing_id>', methods=['GET', 'POST'])
def market_detail(listing_id):
    # Check if the market exists, if not create it


    market = get_market_data(listing_id)
    refresh_page = False


    if market is None:
        flash("Failed to fetch market data.", category="error")
        return redirect(url_for('views.search'))

    if current_user.is_authenticated:
        ## if user has visited market
        existing_visit = UserMarketVisit.query.filter_by(user_id=current_user.id, market_id=listing_id).first()

        if not existing_visit:
            visit = UserMarketVisit(user_id=current_user.id, market_id=listing_id)
            db.session.add(visit)
            db.session.commit()

    page_views = PageViews.query.filter_by(id=listing_id).first()

    if page_views:
        page_views.views += 1
        db.session.commit()
    else:
        page_views = PageViews(id=listing_id, views=1)
        db.session.add(page_views)
        db.session.commit()

    # Fetch comments associated with the market
    comments = Comment.query.filter_by(listing_id=listing_id).all()
    if len(comments) <= 0:
        comments = None

    users_dict = {user.id: user.username for user in User.query.all()}

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

    return render_template("market_detail.html", market=market, comments=comments, activeUser = current_user, users_dict = users_dict, page_views = page_views)


@views.route('/recommendations', methods=['GET'])
@login_required
def recommendations():
    # fetch rec markets for active user
    recommended_market_ids = recommend_markets_for_user(current_user.id)

    # fetch & display market details
    recommended_markets = FarmersMarket.query.filter(FarmersMarket.listing_id.in_(recommended_market_ids)).all()
    if len(recommended_markets) <= 0:
        recommended_markets = None

    return render_template('recommendations.html', recommended_markets=recommended_markets, activeUser=current_user)


def recommend_markets_for_user(user_id):
    # recent click markets
    visited_markets = UserMarketVisit.query.filter_by(user_id=user_id).all()
    visited_market_ids = [v.market_id for v in visited_markets]

    # For recent zip searches
    recent_zip_searches = ZipSearches.query.filter_by(user_id=user_id).order_by(ZipSearches.timestamp.desc()).limit(
        5).all()
    recent_zip_codes = [z.zip_code for z in recent_zip_searches]

    # Fetch markets within the searched zip codes
    markets_in_searched_zip_codes = FarmersMarket.query.filter(
        FarmersMarket.location_zipcode.in_(recent_zip_codes)).all()

    # Combine visited markets and markets from searched ZIP codes (no duplicates)
    recommended_market_ids = list(set(visited_market_ids + [m.listing_id for m in markets_in_searched_zip_codes]))

    return recommended_market_ids

@views.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    if form.validate_on_submit():
        msg = Message("Feedback from " + form.name.data, sender=form.email.data, recipients=['marketmapperfeedback@gmail.com'])
        msg.body = form.feedback.data
        mail.send(msg)
        flash('Your feedback has been sent!')
        return redirect(url_for('auth.login'))  # Adjust as necessary
    return render_template('feedback2.html', form=form, activeUser=current_user)
