from flask import Flask, render_template, request, redirect, url_for, flash, session
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import os

# Add parent directory to path to import scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import the interaction functions
from scripts.interact import (
    get_all_posts, get_post, create_post, vote_post, 
    get_user_reputation, has_user_voted, update_user_sentiment
)
from sentiment import analyze_sentiment, determine_user_sentiment

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# Mock user database for demo (in a real app, use a proper database)
users = {}

# Routes
@app.route('/')
def index():
    posts = get_all_posts()
    # Sort posts by timestamp (newest first)
    posts.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Format timestamps
    for post in posts:
        post['formatted_time'] = datetime.datetime.fromtimestamp(post['timestamp']).strftime('%Y-%m-%d %H:%M')
    
    return render_template('index.html', posts=posts, current_user=session.get('user_address'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_address = request.form.get('user_address')
        
        if username in users:
            flash("Username already taken")
            return redirect(url_for('register'))
        
        # In a real app, validate the Ethereum address
        users[username] = {
            'password_hash': generate_password_hash(password),
            'user_address': user_address
        }
        
        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username]['password_hash'], password):
            session['username'] = username
            session['user_address'] = users[username]['user_address']
            flash("Login successful")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_address', None)
    flash("You have been logged out")
    return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'username' not in session:
        flash("Please login to create a post")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        is_news = 'is_news' in request.form
        
        if is_news:
            # Analyze sentiment for news posts
            sentiment, polarity = analyze_sentiment(content)
            flash(f"Post sentiment analysis: {sentiment.capitalize()} (Score: {polarity:.2f})")
        
        # Get the logged-in user's address
        user_address = session.get('user_address')
        
        # Create post on blockchain - IMPORTANT: Pass the user's address explicitly
        post_id, _ = create_post(title, content, is_news, user_address=user_address)
        
        if post_id:
            flash("Post created successfully")
            return redirect(url_for('post_detail', post_id=post_id))
        else:
            flash("Failed to create post")
    
    return render_template('create_post.html')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = get_post(post_id)
    post['formatted_time'] = datetime.datetime.fromtimestamp(post['timestamp']).strftime('%Y-%m-%d %H:%M')
    
    # Get author reputation
    author_reputation = get_user_reputation(post['author'])
    
    # Check if current user has voted
    has_voted = False
    is_upvote = False
    
    if 'user_address' in session:
        has_voted, is_upvote = has_user_voted(post_id, session['user_address'])
    
    return render_template(
        'post_detail.html', 
        post=post, 
        author_reputation=author_reputation,
        has_voted=has_voted,
        is_upvote=is_upvote,
        current_user=session.get('user_address')
    )

@app.route('/vote/<int:post_id>/<vote_type>')
def vote(post_id, vote_type):
    if 'username' not in session:
        flash("Please login to vote")
        return redirect(url_for('login'))
    
    is_upvote = vote_type == 'up'
    user_address = session.get('user_address')
    
    # Submit vote to blockchain - Pass the user's address explicitly
    success, message = vote_post(post_id, is_upvote, user_address=user_address)
    
    if success:
        flash("Vote recorded successfully")
        
        # Update post author's sentiment if this is a news post
        post = get_post(post_id)
        if post['isNews']:
            user_posts = [p for p in get_all_posts() if p['author'] == post['author']]
            sentiment_tag = determine_user_sentiment(user_posts)
            update_user_sentiment(post['author'], sentiment_tag, from_address=user_address)
    else:
        flash(message)
    
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/user/<user_address>')
def user_profile(user_address):
    # Get user reputation
    reputation = get_user_reputation(user_address)
    
    # Get user posts
    all_posts = get_all_posts()
    user_posts = [p for p in all_posts if p['author'].lower() == user_address.lower()]
    
    # Format timestamps
    for post in user_posts:
        post['formatted_time'] = datetime.datetime.fromtimestamp(post['timestamp']).strftime('%Y-%m-%d %H:%M')
    
    return render_template(
        'user_profile.html',
        user_address=user_address,
        reputation=reputation,
        posts=user_posts
    )

if __name__ == '__main__':
    app.run(debug=True)