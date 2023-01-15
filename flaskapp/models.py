from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flaskapp import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    pictures = db.relationship('Picture', backref='pictureowner', lazy=True)
    public_pictures = db.relationship('PublicPicture', backref='publicpictureowner', lazy=True)
    permissions = db.relationship('Permission', backref='owner', lazy=True)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_user_id(self):
        return self.id

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Picture('{self.image_file}'"

class PublicPicture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Picture('{self.image_file}'"

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    allowed_user_id = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"permission( allowed'{self.allowed_user_id}' by {self.user_id})"