import os
from app.exetensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask import current_app
import random
from settings import basedir

Column = db.Column
VA_IMG_DIR = os.path.join(basedir, 'app', 'static/images/variety')


class dbCRUD:

    __tablename__ = ''

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
        return f'<{self.__tablename__}: {self.id}>'


class User(UserMixin, dbCRUD, db.Model):
    __tablename__ = 'user'
    id = Column(db.Integer, primary_key=True)
    username = Column(db.String(80), nullable=False, unique=True)
    password_hash = Column(db.String(128))
    email = Column(db.String(50), unique=True)
    phone = Column(db.String(20))
    pub_phone = Column(db.Boolean)
    institute = Column(db.String(80))
    photo = Column(db.String(300))
    research = Column(db.String(300))
    profile = Column(db.String(1000))
    create_at = Column(db.DateTime)
    is_active = Column(db.Boolean)
    is_admin = Column(db.Boolean)

    def __init__(self,
                 username,
                 email,
                 password,
                 phone,
                 pub_phone,
                 photo,
                 institute,
                 research,
                 profile,
                 is_active=False,
                 is_admin=False,
                 create_at=datetime.now()):
        self.username = username
        self.email = email
        self.institute = institute
        self.phone = phone
        self.pub_phone = pub_phone
        self.photo = photo
        self.research = research
        self.profile = profile
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
    type = Column(db.String(6))
    opened = Column(db.Boolean)
    sign = Column(db.Boolean)
    create_time = Column(db.DateTime)
    figures = db.relationship('DataFigure', backref='fig', lazy=True)

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

    def __init__(self,
                 content,
                 variety_name,
                 provider,
                 create_time=datetime.now()):
        self.content = content
        self.variety_name = variety_name
        self.provider = provider
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
        return '<variety: {}>'.format(self.id)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = Column(db.Integer, primary_key=True)
    parent_id = Column(db.Integer, nullable=False)
    content = Column(db.Text)
    provider = Column(db.String(45))
    create_time = Column(db.DateTime)

    def __init__(self,
                 parent_id,
                 content,
                 provider,
                 create_time=datetime.now()):
        self.parent_id = parent_id
        self.content = content
        self.provider = provider
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
        return '<comment: {}>'.format(self.id)


class VarietyComment(dbCRUD, db.Model):
    __tablename__ = 'varietyComment'
    id = Column(db.Integer, primary_key=True)
    comment_type = Column(db.String(10))
    provider = db.Column(db.Integer)
    variety = db.Column(db.Integer)
    content = Column(db.Text)
    create_time = Column(db.DateTime)

    def __init__(self,
                 content,
                 variety,
                 provider,
                 comment_type="commnet",
                 create_time=datetime.now()):
        self.content = content
        self.variety = variety
        self.provider = provider
        self.comment_type = comment_type
        self.create_time = create_time

    @property
    def provider_name(self):
        provider_obj = User.query.get(self.provider)
        return provider_obj.username

    @property
    def reply(self):
        reply_obj = VarietyComment.query.filter_by(variety=self.id,
                                                   comment_type="reply").all()
        return reply_obj

    def delete_reply(self, commit=True):
        for reply_i in self.reply:
            reply_i.delete(commit=commit)


class VarietyDetail(dbCRUD, db.Model):
    __tablename__ = 'varietyDetail'
    id = Column(db.Integer, primary_key=True)
    variety_name = Column(db.String(45))
    variety_type = Column(db.String(12))
    geographic = Column(db.String(45))
    country = Column(db.String(45))
    province = Column(db.String(45))
    affiliation = Column(db.String(200))
    basic_info_sup = Column(db.String(1000))
    provider = db.Column(db.Integer)
    create_time = Column(db.DateTime)
    flower_color = Column(db.String(45))
    leaf_color = Column(db.String(45))
    protein_content = Column(db.String(45))
    starch_content = Column(db.String(45))
    salt = Column(db.String(8))
    high_temperature = Column(db.String(8))
    low_temperature = Column(db.String(8))
    sheath_blight = Column(db.String(45))
    fusarium = Column(db.String(45))
    total_erosion = Column(db.String(45))
    powdery_mildew = Column(db.String(45))
    leaf_rust = Column(db.String(45))
    leaf_blight = Column(db.String(45))
    stripe_rust = Column(db.String(45))
    spinal_rust = Column(db.String(45))
    smut = Column(db.String(45))
    figures = db.relationship('VarietyFigure', backref='fig', lazy=True)

    def __init__(self,
                 variety_name,
                 variety_type,
                 geographic,
                 country,
                 province,
                 affiliation,
                 basic_info_sup,
                 flower_color,
                 leaf_color,
                 protein_content,
                 starch_content,
                 salt,
                 high_temperature,
                 low_temperature,
                 sheath_blight,
                 fusarium,
                 total_erosion,
                 powdery_mildew,
                 leaf_rust,
                 leaf_blight,
                 stripe_rust,
                 spinal_rust,
                 smut,
                 provider,
                 create_time=datetime.now()):
        self.variety_name = variety_name
        self.variety_type = variety_type
        self.geographic = geographic
        self.country = country
        self.province = province
        self.affiliation = affiliation
        self.basic_info_sup = basic_info_sup
        self.provider = provider
        self.create_time = create_time
        self.flower_color = flower_color
        self.leaf_color = leaf_color
        self.protein_content = protein_content
        self.starch_content = starch_content
        self.salt = salt
        self.high_temperature = high_temperature
        self.low_temperature = low_temperature
        self.sheath_blight = sheath_blight
        self.fusarium = fusarium
        self.total_erosion = total_erosion
        self.powdery_mildew = powdery_mildew
        self.leaf_rust = leaf_rust
        self.leaf_blight = leaf_blight
        self.stripe_rust = stripe_rust
        self.spinal_rust = spinal_rust
        self.smut = smut

    @property
    def provider_obj(self):
        return User.query.get(self.provider)

    def delete(self, commit=True):
        va_comment = VarietyComment.query.filter_by(provider=self.provider,
                                                    variety=self.id).all()
        for va_i in va_comment:
            va_i.delete(commit=commit)
            va_i.delete_reply(commit=commit)
        return super().delete(commit=commit)


class VarietyFigure(dbCRUD, db.Model):
    __tablename__ = 'varietyFig'
    id = Column(db.Integer, primary_key=True)
    url = Column(db.String(500))
    variety = db.Column(db.Integer,
                        db.ForeignKey('varietyDetail.id'),
                        nullable=True)

    def __init__(self, url, variety):
        self.url = url
        self.variety = variety


class VarietyFigureExample():
    def __init__(self):
        randomPhoto = random.choice(os.listdir(VA_IMG_DIR))
        self.id = 'example'
        self.url = f'/static/images/variety/{randomPhoto}'
        self.variety = 'example'


class DataFigure(dbCRUD, db.Model):
    __tablename__ = 'dataFig'
    id = Column(db.Integer, primary_key=True)
    url = Column(db.String(500))
    data = db.Column(db.Integer, db.ForeignKey('data.id'), nullable=True)

    def __init__(self, url, data):
        self.url = url
        self.data = data
