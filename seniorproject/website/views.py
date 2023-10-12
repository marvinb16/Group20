from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Post
from . import db
import json
from .api import get_latest_api_call, fetch_farmers_market_data

views = Blueprint('views', __name__)
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
    api_response = None
    zipcode = request.form.get('zipcode')
    radius = request.form.get('radius')

    # Call the API function from api.py
    if zipcode != None:
        fetch_farmers_market_data(int(zipcode), int(radius))
        api_response = get_latest_api_call()

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