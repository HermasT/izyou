# coding: utf-8
import json, hashlib, enum, time
import sqlalchemy.sql as sasql
from sqlalchemy import exc, event, create_engine, schema, Column, ForeignKey, select, func
from sqlalchemy.pool import QueuePool, Pool
from sqlalchemy.types import Unicode, Integer, String, BIGINT, TIMESTAMP, Boolean, Text, Date, Float, Enum
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import Session, sessionmaker, scoped_session, relationship, backref
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.schema import Index, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.login import login_user, logout_user, current_user, login_required
from portal import app, db, lm

# 枚举类型
class Enum(enum.Enum):
    @property
    def strvalue(self):
        return str(self.value)

# 用户类型
class UserType(Enum):
    normal = 0
    registered = 1
    student = 2
    fanculty = 3
    staff = 4
    admin = 65535

# class UType(db.Model):
#     id = db.Column(Integer, primary_key=True)
#     name = db.Column(String(16), nullable=True)
#     cname = db.Column(String(32), nullable=True)

#     def __init__(self, id, name, cname):
#         self.id = id
#         self.name = name
#         self.cname = cname
 
#     def __repr__(self):
#         return "<UserType '{:d}-{:s}-{:s}'>".format(self.id, self.name, self.cname)

# 项目类型
class GameType(Enum):
    undefined = 0
    bridge = 1
    sudoku = 2
    go = 3
    chess = 4
    cchess = 5
    miexed = 6
    count = 7

    @staticmethod
    def getAll():
        return [
            {'type':1, 'name': '桥牌'},
            {'type':2, 'name': '数独'},
            {'type':3, 'name': '围棋'}
        ]

    @staticmethod
    def getName(type):
        if type == 1:
            return '桥牌'
        elif type == 2:
            return '数独'
        elif type == 3:
            return '围棋'
        elif type == 4:
            return '中国象棋'
        elif type == 5:
            return '国际象棋'
        elif type == 6:
            return '混合'
        else:
            return '未知'

# class GType(db.Model):
#     type = db.Column(Integer, primary_key=True)
#     name = db.Column(String(16), nullable=True)
#     cname = db.Column(String(16), nullable=True)
#     extend = db.Column(String(32), nullable=False)

#     def __init__(self, type, name, cname, extend=''):
#         self.type = type
#         self.name = name
#         self.cname = cname
#         self.extend = extend
 
#     def __repr__(self):
#         return "<GameType '{:d}-{:s}'>".format(self.type, self.cname)

# 付费类型
class PayType(Enum):
    undefined = 0
    cash = 1
    wechat = 2
    alipay = 3
    online = 4
    others = 5

    @staticmethod
    def getAll():
        return [
            {'type':0, 'name': '未支付'},
            {'type':1, 'name': '现金支付'},
            {'type':2, 'name': '微信支付'},
            {'type':3, 'name': '支付宝'},
            {'type':4, 'name': '在线支付'},
            {'type':5, 'name': '其他'}
        ]


# class PType(db.Model):
#     type = db.Column(Integer, primary_key=True)
#     name = db.Column(String(16), nullable=True)
#     cname = db.Column(String(16), nullable=True)
#     extend = db.Column(String(32), nullable=False)

#     def __init__(self, type, name, cname, extend=''):
#         self.type = type
#         self.name = name
#         self.cname = cname
#         self.extend = extend
 
#     def __repr__(self):
#         return "<GameType '{:d}-{:s}'>".format(self.type, self.cname)

# 性别
class GenderType(Enum):
    undefined = 0
    male = 1
    female =2

    @staticmethod
    def getType(name):
        if name == '男':
            return 1
        elif type == '女':
            return 2
        else:
            return 0

    @staticmethod
    def getName(type):
        if type == 1:
            return '男'
        elif type == 2:
            return '女'
        else:
            return '未知'

# 用户
@lm.user_loader
def load_user(username):
    return Users.query.filter_by(username=username).first()

class Users(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(String(32), unique=True, nullable=False)
    password = db.Column(String(32), nullable=False)
    phone = db.Column(String(16), nullable=False)
    email = db.Column(String(64), nullable=False)
    name = db.Column(String(32), nullable=True)
    type = db.Column(Integer, default=UserType.normal)

    def __init__(self, username, password, phone, email, name, type=UserType.normal):
        self.username = username
        self.password= Users.get_crypto_password(password)
        self.phone = phone
        self.email = email
        self.name = name
        self.type = type;
        
    def __repr__(self):
        return "<User '{:s}-{:s}-{:s}-{:s}''>".format(self.username, self.email, self.password, self.phone)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.username)

    def is_privileged(self, level):
        return self.type >= level

    @staticmethod
    def get_crypto_password(password):
        return hashlib.md5(password).hexdigest()

# 教师
class Teacher(db.Model):
    tid = db.Column(Integer, primary_key=True)
    name = db.Column(String(16), nullable=False)
    birth = db.Column(Date)
    gender = db.Column(Integer, default=GenderType.undefined)
    gtype = db.Column(Integer)
    uprice = db.Column(Float, default=0.0)
    desc = db.Column(String(128))
    extend = db.Column(String(64), nullable=True)

    def __init__(self, name, birth, gtype, gender=GenderType.undefined, uprice=0.0, desc='', extend=''):
        self.name = name
        self.birth = birth
        self.gender = gender
        self.gtype = gtype
        self.uprice = uprice
        self.desc = desc
        self.extend = extend
 
    def __repr__(self):
        return "<Teacher({:d}): {:s}>".format(self.tid, self.name)

# 课程
class CourseStatus(Enum):
    applying = 0
    opening = 1
    full = 2
    ended = 3
    cancelled = 4

    @staticmethod
    def getAll():
        return [
            {'status':0, 'name': '报名中'},
            {'status':1, 'name': '已开课'},
            {'status':2, 'name': '已报满'},
            {'status':3, 'name': '已结束'},
            {'status':4, 'name': '已取消'}
        ]

    @staticmethod
    def getName(status):
        if status == 0:
            return '报名中'
        elif status == 1:
            return '已开课'
        elif status == 2:
            return '已报满'
        elif status == 3:
            return '已结束'
        elif status == 4:
            return '已取消'
        else:
            return '未知'    

class Course(db.Model):
    cid = db.Column(Integer, primary_key=True)
    name = db.Column(String(32), nullable=False)
    gtype = db.Column(Integer, nullable=False)
    tid = db.Column(Integer) # ForeignKey('teacher.tid')
    start = db.Column(Date)
    end = db.Column(Date)
    count = db.Column(Integer)
    charge = db.Column(Float)
    status = db.Column(Integer)  #CourseStatus
    desc = db.Column(String(128))
    extend = db.Column(String(64))

    def __init__(self, name, gtype, tid, start, end, count, charge, desc='', extend=''):
        self.name = name
        self.gtype = gtype;
        self.tid = tid
        self.start = start
        self.end = end
        self.count = count
        self.charge = charge
        self.status = CourseStatus.applying
        self.desc = desc
        self.extend = extend
 
    def __repr__(self):
        return "<Course{:d}: {:s}>".format(self.cid, self.name)

# 教室
class Room(db.Model):
    rid = db.Column(Integer, primary_key=True)
    name = db.Column(String(32), nullable=False)
    location = db.Column(String(128))
    traffic = db.Column(String(128))
    extend = db.Column(String(64))

    def __init__(self, name, location='', traffic='', extend=''):
        self.name = name
        self.location = location
        self.traffic = traffic
        self.extend = extend
 
    def __repr__(self):
        return "<Room: {:s}>".format(self.name)

# 报名
class Register(db.Model):
    rid = db.Column(Integer, primary_key=True)
    username = db.Column(String(32)) # ForeignKey('users.username')
    cid = db.Column(Integer) # ForeignKey('course.cid')
    charged = db.Column(Boolean)
    ptype = db.Column(Integer) # PayType
    origin = db.Column(Integer)
    operator = db.Column(String(32))
    extend = db.Column(String(64))

    def __init__(self, username, cid, op, charged=False, ptype=0, extend=''):
        self.username = username
        self.cid = cid
        self.charged = charged
        self.ptype = ptype
        self.origin = cid
        self.operator = op
        self.extend = extend
 
    def __repr__(self):
        return "<Register{:s}: {:s}报名了{:s}>".format(self.rid, self.username, self.cid)
