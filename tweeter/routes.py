import secrets, os
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from tweeter import app, db, bcrypt
from tweeter.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateTweet
from tweeter.models import User, Tweet
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    tweets = Tweet.query.order_by(Tweet.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('index.html', tweets=tweets)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashpw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashpw)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created {form.username.data}!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'You are logged in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash(f'Invalid Email or Password!', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

def save_picture(form_pic):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pic.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)

    i = Image.open(form_pic)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('You account is updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='/profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form)

@app.route('/tweet/new', methods=['GET', 'POST'])
@login_required
def new_tweet():
    form = CreateTweet()
    if form.validate_on_submit():
        tweet = Tweet(text=form.tweet.data, user_id=current_user.id)
        db.session.add(tweet)
        db.session.commit()
        flash('Tweet has been published!', 'success')
        return redirect(url_for('index'))
    return render_template('create_tweet.html', form=form)

@app.route('/tweet/<int:id>', methods=['GET', 'POST'])
def tweet(id):
    tweet = Tweet.query.get_or_404(id)
    return render_template('tweet.html', tweet=tweet)

@app.route('/tweet/<int:id>/update', methods=['GET', 'POST'])
@login_required
def tweet_update(id):
    tweet = Tweet.query.get_or_404(id)
    if tweet.author != current_user:
        abort(403)
    form = CreateTweet()
    if form.validate_on_submit():
        tweet.text = form.tweet.data
        db.session.commit()
        flash('Tweet has been Updated!', 'success')
        return redirect(url_for('tweet', id=id))
    form.tweet.data = tweet.text
    return render_template('update_tweet.html', form=form)

@app.route('/tweet/<int:id>/delete', methods=['POST'])
@login_required
def tweet_delete(id):
    tweet = Tweet.query.get_or_404(id)
    if tweet.author != current_user:
        abort(403)
    db.session.delete(tweet)
    db.session.commit()
    flash('Tweet has been Deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/user/<string:username>')
def user_tweets(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    tweets = Tweet.query.filter_by(author=user)\
        .order_by(Tweet.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_post.html', tweets=tweets, user=user)