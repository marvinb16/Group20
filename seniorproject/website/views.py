from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Post
from . import db
import json

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

@views.route('/search')
def search():
    return render_template("search.html", activeUser = current_user)

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