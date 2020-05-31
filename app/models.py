from app import database as db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin


class Sbc(db.Model):
    __tablename__ = 'sbc'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    connected = db.Column(db.Boolean)
    description = db.Column(db.Text)
    # Foreign keys:
    logs = db.relationship('Logs', cascade="all, delete", backref='logs', lazy=True)    
    forwarding = db.relationship('Forwarding', cascade="all, delete", backref="sbc", lazy=True)


class Logs(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(32), nullable=True)
    realAddress = db.Column(db.String(39), nullable=False)
    virtualAddress = db.Column(db.String(39), nullable=False)
    sbc_id = db.Column(db.Integer, db.ForeignKey('sbc.id', ondelete='CASCADE'), nullable=False)


class Forwarding(db.Model):
    __tablename__ = 'forwarding'
    id = db.Column(db.Integer, primary_key=True)
    date_open = db.Column(db.DateTime, nullable=True)
    destination_port = db.Column(db.Integer, nullable=False)
    dedicated_port = db.Column(db.Integer, nullable=True)  # nullable = True    
    time_live = db.Column(db.Integer, nullable=True)
    pid = db.Column(db.Integer, nullable=True)    
    sbc_id = db.Column(db.Integer, db.ForeignKey('sbc.id', ondelete='CASCADE'), nullable=False)    


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)    
    username = db.Column(db.String(50), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)        
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)    
    redirect_to = db.Column(db.Integer, db.ForeignKey('forwarding.id'), nullable=True)
    forwarding = db.relationship("Forwarding")

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,  password):
        return check_password_hash(self.password_hash, password)
