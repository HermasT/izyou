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
    faculty = 3
    staff = 4
    admin = 65535

# 项目类型
class GameType(Enum):
    undefined = 0
    bridge = 1
    sudoku = 2
    go = 3
    xiangqi = 4
    chess = 5
    mixed = 6
    count = 7

    @staticmethod
    def getAll():
        return [
            {'type':1, 'name': '桥牌'},
            {'type':2, 'name': '数独'},
            {'type':3, 'name': '围棋'},
            {'type':4, 'name': '象棋'}
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
            return '象棋'
        elif type == 5:
            return '国际象棋'
        elif type == 6:
            return '混合'
        else:
            return '未知'

# 产品线
class ProductType(Enum):
    undefined = 0
    course = 1
    problem = 2

    @staticmethod
    def getAll():
        return [
            {'type':0, 'name': '未定义'},
            {'type':1, 'name': '课程'},
            {'type':2, 'name': '题库'}
        ]

    @staticmethod
    def getName(type):
        if type == 1:
            return '课程'
        elif type == 2:
            return '题库'
        else:
            return '未定义'

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

    @staticmethod
    def getName(type):
        if type == 0:
            return '未支付'
        elif type == 1:
            return '现金支付'
        elif type == 2:
            return '微信支付'
        elif type == 3:
            return '支付宝'
        elif type == 4:
            return '在线支付'
        elif type == 5:
            return '其他'
        else:
            return '未定义'

# 订单状态
class OrderStatus(Enum):
    undefined = 0
    order = 1
    ordered = 2
    cancelled = 3
    finished = 4

    @staticmethod
    def getAll():
        return [
            {'type':0, 'name': '未定义'},
            {'type':1, 'name': '未支付'},
            {'type':2, 'name': '已支付'},
            {'type':3, 'name': '已取消'},
            {'type':4, 'name': '已完成'}
        ]

    @staticmethod
    def getName(type):
        if type == 1:
            return '未支付'
        elif type == 2:
            return '已支付'
        elif type == 3:
            return '已取消'
        elif type == 4:
            return '已完成'
        else:
            return '未定义'

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
    username = db.Column(String(32), unique=True, nullable=False) # 用户名
    password = db.Column(String(32), nullable=False) # 密码密文
    phone = db.Column(String(16), nullable=False) # 手机号
    email = db.Column(String(64), nullable=False) # 邮箱（后期可选）
    name = db.Column(String(32), nullable=True) # 姓名
    type = db.Column(Integer, default=UserType.normal) # 用户类别

    def __init__(self, username, password, phone, email, name, type=UserType.normal):
        self.username = username
        self.password= Users.get_crypto_password(password)
        self.phone = phone
        self.email = email
        self.name = name
        self.type = type;
        
    def __repr__(self):
        return "<User 'uid={:d}-{:s}-{:s}-{:s}-{:s}''>".format(self.uid, self.username, self.email, self.password, self.phone)

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

# 学生
class Student(db.Model):
    sid = db.Column(Integer, primary_key=True) 
    username = db.Column(String(32), unique=True, nullable=False) # ForeignKey('Users.username')
    birth = db.Column(Date) # 出生日期
    gender = db.Column(Integer, default=GenderType.undefined) # 性别
    school = db.Column(String(64)) # 学校
    extend = db.Column(String(64), nullable=True)

    def __init__(self, username, birth, gender, school='', extend=''):
        self.username = username
        self.birth = birth
        self.gender = gender
        self.school = school
        self.extend = extend
 
    def __repr__(self):
        return "<Student({:d}): {:s}>".format(self.sid, self.username)

# 教师
class Teacher(db.Model):
    tid = db.Column(Integer, primary_key=True)
    username = db.Column(String(32), unique=True, nullable=False) # ForeignKey('Users.username')
    birth = db.Column(Date)
    gender = db.Column(Integer, default=GenderType.undefined)
    gtype = db.Column(Integer)
    uprice = db.Column(Float, default=0.0)
    desc = db.Column(String(128))
    extend = db.Column(String(64), nullable=True)

    def __init__(self, username, birth, gtype, gender=GenderType.undefined, uprice=0.0, desc='', extend=''):
        self.username = username
        self.birth = birth
        self.gender = gender
        self.gtype = gtype
        self.uprice = uprice
        self.desc = desc
        self.extend = extend
 
    def __repr__(self):
        return "<Teacher({:d}): {:s}>".format(self.tid, self.username)

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
    start = db.Column(Date) # 开始日期
    end = db.Column(Date)  # 结束日期
    max_student = db.Column(Integer) # 最大学生人数
    min_student = db.Column(Integer) # 最小学生人数
    audition = db.Column(Integer) # 允许试听次数
    count = db.Column(Integer) # 课程总计次数
    period = db.Column(Integer) # 课程时长（以分钟计）
    charge = db.Column(Float) # 课程费用
    discount = db.Column(Float) # 折扣率（0.9=9折）
    status = db.Column(Integer)  # CourseStatus
    desc = db.Column(String(128)) # 课程介绍
    extend = db.Column(String(64))

    def __init__(self, name, gtype, tid, start, end, count, period, charge, 
                max_student=65536, min_student=1, audition=0, discount=1, desc='', extend=''):
        self.name = name
        self.gtype = gtype;
        self.tid = tid
        self.start = start
        self.end = end
        self.count = count
        self.period = period
        self.charge = charge
        self.max_student = max_student
        self.min_student = min_student
        self.audition = audition
        self.discount = discount
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

# 订单
class Orders(db.Model):
    orderid = db.Column(Integer, primary_key=True)
    username = db.Column(String(32)) # ForeignKey('users.username') 下单的用户名（用户）
    charged = db.Column(Boolean) # 是否收费
    paytype = db.Column(Integer) # 付费类型
    amount = db.Column(Float) # 应收账款（产品价格累计）
    income = db.Column(Float) # 实收账款（处理打折、减免等）
    status = db.Column(Integer) # 订单状态 OrderStatus
    operator = db.Column(String(32)) # ForeignKey('users.username') 操作的用户名（工作人员）
    extend = db.Column(String(64)) # 退费记录原因

    def __init__(self, username, op, amount, income=0, charged=False, 
                status=OrderStatus.undefined, paytype=PayType.undefined, extend=''):
        self.username = username
        self.charged = charged
        self.paytype = paytype
        self.status = status
        self.amount = amount
        if (income == 0):
            self.income = amount
        else:
            self.income = income
        self.operator = op
        self.extend = extend
 
    def __repr__(self):
        return "<Order{:s}: {:s}>".format(self.orderid, self.username)

# 订单产品列表 一张订单中允许同时购买多个产品
class OrdersList(db.Model):
    orderid = db.Column(Integer, primary_key=True)
    ptype = db.Column(Integer) # 产品类型
    pid = db.Column(Integer) # 产品编号
    count = db.Column(Integer) # 产品数量
    status = db.Column(Integer) # 产品状态 0 = 正常，1 = 退费
    operator = db.Column(String(32)) # 当前操作的用户账号
    extend = db.Column(String(64)) # 退费记录原因

    def __init__(self, ptype, pid, op, count=1, status=0, extend=''):
        self.pid = pid
        self.ptype = ptype
        self.count = count
        self.operator = op
        self.status = status
        self.extend = extend
 