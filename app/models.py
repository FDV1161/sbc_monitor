from app import database as db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), nullable=False, unique=True)
    # email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,  password):
        return check_password_hash(self.password_hash, password)


class Sbc(db.Model):
    __tablename__ = 'sbc'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    connected = db.Column(db.Boolean)
    description = db.Column(db.Text)
    logs = db.relationship('Logs', cascade="all, delete", backref=db.backref('logs', lazy=True))
    forwarding = db.relationship('Forwarding', cascade="all, delete", backref=db.backref('forwarding', lazy=True))


class Logs(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(32), nullable=True)
    realAddress = db.Column(db.String(39), nullable=False)
    virtualAddress = db.Column(db.String(39), nullable=False)
    sbc_id = db.Column(db.Integer, db.ForeignKey('sbc.id'), nullable=False)
    

# Forwarding

class Forwarding(db.Model):
    __tablename__ = 'forwarding'
    id = db.Column(db.Integer, primary_key=True)
    date_open = db.Column(db.DateTime, nullable=True)
    destination_port = db.Column(db.Integer, nullable=False)
    dedicated_port = db.Column(db.Integer, nullable=True) # nullable = True
    sbc_id = db.Column(db.Integer, db.ForeignKey('sbc.id'), nullable=False)
    
    time_live = db.Column(db.Integer, nullable=True)
    pid = db.Column(db.Integer, nullable=True)



# class Sbc(object):
# 	pass
# def loadSession():
# 	engine = create_engine('mysql+pymysql://root:root@localhost:8080/test', echo=True)
# 	metadata = MetaData(engine)
# 	sbc_eng = Table('sbc', metadata,
# 		Column('id', Integer, primary_key=True),
# 		Column('name', String(255)),
# 		Column('description', Text)
# 	)
# 	mapper(Sbc, sbc_eng)
# 	Session = sessionmaker(bind=engine)
# 	session = Session()
# 	return session


# id = db.Column(db.Integer, primary_key=True)
