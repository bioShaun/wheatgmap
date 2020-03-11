from app.exetensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask import current_app

Column = db.Column


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = Column(db.Integer, primary_key=True)
    username = Column(db.String(80), nullable=False, unique=True)
    password_hash = Column(db.String(128))
    email = Column(db.String(50), unique=True)
    phone = Column(db.String(11))
    institute = Column(db.String(80))
    create_at = Column(db.DateTime)
    is_active = Column(db.Boolean)
    is_admin = Column(db.Boolean)

    def __init__(self,
                 username,
                 email,
                 password,
                 phone,
                 institute,
                 is_active=False,
                 is_admin=False,
                 create_at=datetime.now()):
        self.username = username
        self.email = email
        self.institute = institute
        self.phone = phone
        self.is_active = is_active
        self.is_admin = is_admin
        self.create_at = create_at
        if password:
            self.password_hash = generate_password_hash(password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})


    @classmethod
    def confirm(cls, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        user = cls.query.filter_by(id=data.get('confirm', '')).first()
        return user

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

    @property
    def password(self):
        raise AttributeError('password is not readable!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<user: {}>'.format(self.username)


'''
class Snptable(db.Model):
    id = Column(db.Integer, primary_key=True)
    tablename = Column(db.String(45))
    tabletype = Column(db.String(45))
    owner = Column(db.String(80))

    def __repr__(self):
        return '<snp table {}>'.format(self.id)
'''

class Data(db.Model):
    __tablename__ = 'data'
    id = Column(db.Integer, primary_key=True)
    tc_id = Column(db.String(10), nullable=False)
    provider = Column(db.String(45), nullable=False)
    sample_name = Column(db.String(45), nullable=False)
    scientific_name = Column(db.String(45))
    variety_name = Column(db.String(45))
    high_level_tissue = Column(db.Text)
    high_level_age = Column(db.Text)
    treatments = Column(db.Text)
    tissue = Column(db.Text)
    age = Column(db.Text)
    stress_disease = Column(db.Text)
    dol = Column(db.Text)
    bulked_segregant = Column(db.Text)
    mixed_sample = Column(db.Text)
    mutant_transgenosis = Column(db.Text)
    other_inf = Column(db.Text)
    type = Column(db.String(5))
    opened = Column(db.Boolean)
    sign = Column(db.Boolean)
    create_time = Column(db.DateTime)
    def __init__(self,
                 tc_id,
                 provider,
                 sample_name,
                 type,
                 opened=False,
                 sign=False,
                 create_time=datetime.now()):
        self.tc_id = tc_id
        self.provider = provider
        self.sample_name = sample_name
        self.type = type
        self.opened = opened
        self.sign = sign
        self.create_time = create_time
    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

    def __repr__(self):
        return '<data: {}>'.format(self.id)


class Variety(db.Model):
    __tablename__ = 'variety'
    id = Column(db.Integer, primary_key=True)
    variety_name = Column(db.String(45))
    content = Column(db.Text)
    create_time = Column(db.DateTime)
    provider = Column(db.String(45))


    def __init__(self, content ,variety_name, provider, create_time=datetime.now()):
        self.content = content
        self.variety_name = variety_name
        self.provider = provider
        self.create_time =create_time

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

    def __repr__(self):
        return '<variety: {}>'.format(self.id)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = Column(db.Integer, primary_key=True)
    parent_id = Column(db.Integer, nullable=False)
    content = Column(db.Text)
    provider = Column(db.String(45))
    create_time = Column(db.DateTime)

    def __init__(self, parent_id, content, provider, create_time=datetime.now()):
        self.parent_id = parent_id
        self.content = content
        self.provider = provider
        self.create_time =create_time

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

    def __repr__(self):
        return '<comment: {}>'.format(self.id)

class VarietyDetail(db.Model):
    __tablename__ = 'varietyDetail'
    id = Column(db.Integer, primary_key=True)
    variety_name = Column(db.String(45))
    variety_type = Column(db.String(12))
    geographic = Column(db.String(100))
    country = Column(db.String(45))
    province = Column(db.String(45))
    affiliation = Column(db.String(45))
    create_time = Column(db.DateTime)
    provider = Column(db.String(45))


    def __init__(self, content ,variety_name, provider, create_time=datetime.now()):
        self.content = content
        self.variety_name = variety_name
        self.provider = provider
        self.create_time =create_time

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

    def __repr__(self):
        return '<variety: {}>'.format(self.id)

