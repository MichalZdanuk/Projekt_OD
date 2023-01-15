import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from flaskapp import app, db, mail
from flaskapp.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                              RequestResetForm, ResetPasswordForm,
                            PermissionForm, UploadPictureForm)
from flaskapp.models import User, Permission, Picture, PublicPicture
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import flaskapp.pass_strength as password_checker
import flaskapp.validate_data as validator
import bcrypt

@app.route("/")
@app.route("/home")
def home():
    session['attempt']=5
    return render_template('home.html')

@app.route("/protectedpictures")
def protectedpictures():
    user = User.query.filter_by(username=current_user.username).first()
    permissions = Permission.query.filter_by(allowed_user_id=user.get_user_id()).all()
    print(permissions)
    pictures = []
    for id in permissions:
        pictures += Picture.query.filter_by(user_id=id.user_id).all()
    

    return render_template('protectedpictures.html', pictures=pictures)

@app.route("/publicpictures")
def publicpictures():
    pictures = PublicPicture.query.all()
    return render_template('publicpictures.html', pictures=pictures)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)

@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if(validator.check_if_detected_xss_attack(form.email.data) or validator.check_if_detected_xss_attack(form.username.data) or validator.check_if_detected_xss_attack(form.password.data)):
            flash("WARNING!!! WRONG DATA", 'danger')#DETECTED POSSIBLE XSS ATTACK
            return render_template('register.html', title='Register', form=form)
        if(validator.check_if_detected_injection_attack(form.email.data) or validator.check_if_detected_injection_attack(form.username.data) or validator.check_if_detected_injection_attack(form.password.data)):
            flash("WARNING!!! WRONG DATA", 'danger')#DETECTED POSSIBLE SQL INJECTION ATTACK
            return render_template('register.html', title='Register', form=form)
        entropy = password_checker.calc_entropy(form.password.data)
        if (entropy < 30):
             message = f"Too weak password(low entropy). ENTROPY OF PASSWORD = {entropy} At least should be 50"
             flash(message, 'danger')
             return render_template('register.html', title='Register', form=form)
        if (not password_checker.check_if_safe_from_dictionary_attack(form.password.data)):
            message = f"Password is not safe! Can be attacked with dictionary!!! Please imagine another password"
            flash(message, 'danger')
            return render_template('register.html', title='Register', form=form)
        
        hashed_pw = get_hashed_password(form.password.data.encode('utf-8'))#bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        hashed_pw = hashed_pw.decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        
        db.session.add(user)
        db.session.commit()

        #adding permission to own directory
        user = User.query.filter_by(username=form.username.data).first()
        permission = Permission(allowed_user_id=user.get_user_id(), owner=user)
        db.session.add(permission)
        db.session.commit()

        flash('Your account has been created! You are now able to log in', 'success')
        flash(f'{password_checker.inform_about_password_strength(entropy)}', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        session_email = session['email']=form.email.data # added
        if(validator.check_if_detected_xss_attack(form.email.data) or validator.check_if_detected_xss_attack(form.password.data)):
            flash("WARNING!!! WRONG DATA", 'danger')
            #flash("WARNING!!! TRIED DETECTED POSSIBLE XSS ATTACK", 'danger')
            return render_template('login.html', title='Login', form=form)
        if(validator.check_if_detected_injection_attack(form.email.data) or validator.check_if_detected_injection_attack(form.password.data)):
            flash("WARNING!!! WRONG DATA", 'danger')
            #flash("WARNING!!! TRIED DETECTED POSSIBLE SQL INJECTION ATTACK", 'danger')
            return render_template('login.html', title='Login', form=form)
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password(form.password.data.encode('utf-8'), user.password.encode('utf-8')): #bcrypt.check_password_hash(user.password, form.password.data):
            session['logged_in']=True
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
                send_warning_email(user)
                return redirect(url_for('failure'))
            else:
                flash(f'Invalid login, Attempt {attempt} of 5', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):# for saving user avatar
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def own_save_picture(form_picture, username):#for saving uploaded images
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = username + '_' + random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/pictures', picture_fn)

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
        if(validator.check_if_detected_xss_attack(form.username.data) or validator.check_if_detected_xss_attack(form.email.data) or validator.check_if_detected_xss_attack(form.old_password.data) or validator.check_if_detected_xss_attack(form.new_password.data) or validator.check_if_detected_xss_attack(form.email.data)):
            flash("WARNING!!! WRONG DATA", 'danger')#DETECTED POSSIBLE XSS ATTACK
            return redirect(url_for('account'))
        if(validator.check_if_detected_injection_attack(form.username.data) or validator.check_if_detected_injection_attack(form.email.data) or validator.check_if_detected_injection_attack(form.old_password.data) or validator.check_if_detected_injection_attack(form.new_password.data) or validator.check_if_detected_injection_attack(form.email.data)):
            flash("WARNING!!! WRONG DATA", 'danger')#DETECTED POSSIBLE SQL INJECTION ATTACK
            return redirect(url_for('account'))
        entropy = password_checker.calc_entropy(form.new_password.data)
        if (form.new_password.data != '' and entropy < 30):
            message = f"Too weak password(low entropy). ENTROPY OF PASSWORD = {entropy} At least should be 50"
            flash(message, 'danger')
            return render_template('account.html', title='Account',
                            image_file=image_file, form=form)
        if (form.new_password.data != '' and not password_checker.check_if_safe_from_dictionary_attack(form.new_password.data)):
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

def send_warning_email(user):
    msg = Message('Detected 5 incorrect tries to log!!!',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''Somobody tried to log on your account:
{url_for('home', _external=True)}

This is a waring message
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        if(validator.check_if_detected_xss_attack(form.email.data)):
            flash("WARNING!!! WRONG DATA", 'danger')#DETECTED POSSIBLE XSS ATTACK
            return redirect(url_for('reset_request'))
        if(validator.check_if_detected_injection_attack(form.email.data)):
            flash("WARNING!!! WRONG DATA", 'danger')#DETECTED POSSIBLE SQL INJECTION ATTACK
            return redirect(url_for('reset_request'))
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
        if(validator.check_if_detected_xss_attack(form.password.data) or validator.check_if_detected_xss_attack(form.confirm_password.data)):
            flash("WARNING!!! WRONG DATA", 'danger')#DETECTED POSSIBLE XSS ATTACK
            return redirect(url_for('reset_request'))
        if(validator.check_if_detected_injection_attack(form.password.data) or validator.check_if_detected_injection_attack(form.confirm_password.data)):
            flash("WARNING!!! WRONG DATA", 'danger')#DETECTED POSSIBLE SQL INJECTION ATTACK
            return redirect(url_for('reset_request'))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@app.route("/failure")
def failure():
    return render_template('failure.html')

#allow other users permission form
@app.route("/permission", methods=['GET','POST'])
@login_required
def permission():
    form = PermissionForm()
    if form.validate_on_submit():
        if form.allowed_user.data:
            user = User.query.filter_by(username=form.allowed_user.data).first()
            flagUserExists = User.query.filter_by(username=form.allowed_user.data).all()
            if flagUserExists == []:
                flash('No user with this username!!!','danger')
                return redirect(url_for('permission'))
            print(user.get_user_id())
            flagPermissionExists = Permission.query.filter_by(allowed_user_id=user.get_user_id(), user_id=current_user.id).all()
            
            if flagPermissionExists != []:
                flash('User with this username already has permission!!!','danger')
                return redirect(url_for('permission'))
            if(validator.check_if_detected_xss_attack(form.allowed_user.data) or validator.check_if_detected_injection_attack(form.allowed_user.data)):
                flash("WARNING!!! WRONG DATA", 'danger')
            permission = Permission(allowed_user_id=user.get_user_id(), owner=current_user)

            db.session.add(permission)
            db.session.commit()
            flash('Permission has been added!!!','success')
            return redirect(url_for('home'))
        if form.disallowed_user.data:
            user = User.query.filter_by(username=form.disallowed_user.data).first()
            flagUserExists = User.query.filter_by(username=form.disallowed_user.data).all()
            if flagUserExists == []:
                flash('No user with this username!!!','danger')
                return redirect(url_for('permission'))
            print(user.get_user_id())
            flagPermissionExists = Permission.query.filter_by(allowed_user_id=user.get_user_id(), user_id=current_user.id).all()
            
            if flagPermissionExists == []:
                flash('User with this username already has no permission!!!','danger')
                return redirect(url_for('permission'))
            if(validator.check_if_detected_xss_attack(form.disallowed_user.data) or validator.check_if_detected_injection_attack(form.disallowed_user.data)):
                flash("WARNING!!! WRONG DATA", 'danger')
            permission = Permission.query.filter_by(allowed_user_id=user.get_user_id(), owner=current_user).first()

            db.session.delete(permission)
            db.session.commit()
            flash('Permission has been removed!!!','success')
            return redirect(url_for('home'))
    return render_template('permission.html', title='permission',
                            form=form, legend='Permissions manager')

@app.route("/upload_pictures", methods=['GET','POST'])
@login_required
def upload_pictures():
    form = UploadPictureForm()
    if form.validate_on_submit():
        if form.public_picture.data:
            if validator.is_file_hostile(form.public_picture.data):
                flash('WRONG FILE', 'danger')
                return redirect(url_for('upload_pictures'))
            picture_file =  own_save_picture(form.public_picture.data, current_user.username)

            picture = PublicPicture(image_file=picture_file, publicpictureowner=current_user)
            db.session.add(picture)
            db.session.commit()
            flash('Added new public picture!', 'success')
            return redirect(url_for('home'))
        if form.protected_picture.data:
            if validator.is_file_hostile(form.protected_picture.data):
                flash('WRONG FILE', 'danger')
                return redirect(url_for('upload_pictures'))
            picture_file =  own_save_picture(form.protected_picture.data, current_user.username)

            picture = Picture(image_file=picture_file, pictureowner=current_user)
            db.session.add(picture)
            db.session.commit()
            flash('Added new protected picture!', 'success')
            return redirect(url_for('home'))

    return render_template('upload_pictures.html', title='Picture',
                             form=form)
