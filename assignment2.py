from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'  # Change to secure key
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://db_user:db_password@localhost/blog'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)

# User Registration
@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')

    if not email or not password or not username:
        return jsonify({'message': 'Missing email, password, or username!'}), 400

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({'message': 'Email or username already in use!'}), 409

    new_user = User(email=email, password=generate_password_hash(password, method='sha256'), username=username)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully!'}), 201

# User Login
@app.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing email or password!'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid email or password!'}), 401

    token = jwt.encode({'email': user.email, 'exp': datetime.utcnow() + timedelta(hours=1)}, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({'token': token.decode('utf-8')}), 200

# Create a New Blog Post
@app.route('/api/posts', methods=['POST'])
def create_blog_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    token = request.headers.get('Authorization')

    if not title or not content:
        return jsonify({'message': 'Missing title or content!'}), 400

    if not token:
        return jsonify({'message': 'JWT token is missing!'}), 401

    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'JWT token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid JWT token!'}), 401

    author_email = decoded['email']
    author = User.query.filter_by(email=author_email).first()

    if not author:
        return jsonify({'message': 'Author not found!'}), 401

    new_post = BlogPost(title=title, content=content, author_id=author.id)
    db.session.add(new_post)
    db.session.commit()
    
    return jsonify({'message': 'Blog post created successfully!'}), 201

# Post Comments
@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def post_comment(post_id):
    data = request.get_json()
    content = data.get('content')
    token = request.headers.get('Authorization')

    if not content:
        return jsonify({'message': 'Missing comment content!'}), 400

    if not token:
        return jsonify({'message': 'JWT token is missing!'}), 401

    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'JWT token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid JWT token!'}), 401

    author_email = decoded['email']
    author = User.query.filter_by(email=author_email).first()

    if not author:
        return jsonify({'message': 'Author not found!'}), 401

    post = BlogPost.query.get(post_id)

    if not post:
        return jsonify({'message': 'Post not found!'}), 404

    new_comment = Comment(content=content, author_id=author.id, post_id=post.id)
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({'message': 'Comment posted successfully!'}), 201

if __name__ == '__main__':
    app.run(debug=True)
