import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from flaskapp import app, db, bcrypt, mail
from flaskapp.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm)
from flaskapp.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import flaskapp.pass_strength
import flaskapp.validate_data

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    session['attempt']=5
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if(flaskapp.validate_data.check_if_detected_xss_attack(form.email.data) or flaskapp.validate_data.check_if_detected_xss_attack(form.username.data) or flaskapp.validate_data.check_if_detected_xss_attack(form.password.data)):
            flash("WARNING!!! TRIED DETECTED POSSIBLE XSS ATTACK", 'danger')
            return render_template('register.html', title='Register', form=form)
        entropy = flaskapp.pass_strength.calc_entropy(form.password.data)
        if (entropy < 30):
             message = f"Too weak password(low entropy). ENTROPY = {entropy} At least should be 50"
             flash(message, 'danger')
             return render_template('register.html', title='Register', form=form)
        if (not flaskapp.pass_strength.check_if_safe_from_dictionary_attack(form.password.data)):
            message = f"Password is not safe! Can be attacked with dictionary!!! Please imagine another password"
            flash(message, 'danger')
            return render_template('register.html', title='Register', form=form)
        
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        flash(f'Entropy of created password: {entropy}', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        session_email = session['email']=form.email.data # added
        if(flaskapp.validate_data.check_if_detected_xss_attack(form.email.data) or flaskapp.validate_data.check_if_detected_xss_attack(form.password.data)):
            flash("WARNING!!! TRIED DETECTED POSSIBLE XSS ATTACK", 'danger')
            return render_template('login.html', title='Login', form=form)
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['logged_in']=True # added
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            attempt = session.get('attempt')
            attempt -= 1
            session['attempt']=attempt
            if attempt==1:
                flash(f'This is you last attempt, {session_email} will be blocked','danger')
            elif attempt==0:
                return redirect(url_for('failure'))
            else:
                flash(f'Invalid login, Attempt {attempt} of 5', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        if(flaskapp.validate_data.check_if_detected_xss_attack(form.username.data) or flaskapp.validate_data.check_if_detected_xss_attack(form.email.data) or flaskapp.validate_data.check_if_detected_xss_attack(form.old_password.data) or flaskapp.validate_data.check_if_detected_xss_attack(form.email.data)):
            flash("WARNING!!! TRIED DETECTED POSSIBLE XSS ATTACK", 'danger')
            return redirect(url_for('account'))
        entropy = flaskapp.pass_strength.calc_entropy(form.new_password.data)
        if (entropy < 30):
            message = f"Too weak password(low entropy). ENTROPY = {entropy} At least should be 50"
            flash(message, 'danger')
            return render_template('account.html', title='Account',
                            image_file=image_file, form=form)
        if (not flaskapp.pass_strength.check_if_safe_from_dictionary_attack(form.new_password.data)):
            message = f"Password is not safe! Can be attacked with dictionary!!! Please imagine another password"
            flash(message, 'danger')
            return render_template('account.html', title='Account',
                            image_file=image_file, form=form)

        if form.picture.data:
            picture_file =  save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        if(not bcrypt.check_password_hash(current_user.password, form.old_password.data)):
            flash('Incorrect Password. Cannot make changes!!!', 'danger')
            return redirect(url_for('account'))

        if (form.old_password.data and form.new_password.data): 
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                            image_file=image_file, form=form)

@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                            form=form, legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                            form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/failure")
def failure():
    return render_template('failure.html')