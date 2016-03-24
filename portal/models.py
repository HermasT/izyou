# coding: utf-8
import sys, os, json, hashlib, enum, time, binascii
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

    @staticmethod
    def getName(type):
        if type == UserType.registered:
            return '注册用户'
        elif type == UserType.student:
            return '学员'
        elif type == UserType.faculty:
            return '教师'
        elif type == UserType.staff:
            return '员工'
        elif type == UserType.admin:
            return '管理员'
        else:
            return '普通用户'

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
        if type == GameType.bridge:
            return '桥牌'
        elif type == GameType.sudoku:
            return '数独'
        elif type == GameType.go:
            return '围棋'
        elif type == GameType.xiangqi:
            return '象棋'
        elif type == GameType.chess:
            return '国际象棋'
        elif type == GameType.mixed:
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
        if type == ProductType.course:
            return '课程'
        elif type == ProductType.problem:
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
        if type == PayType.undefined:
            return '未支付'
        elif type == PayType.cash:
            return '现金支付'
        elif type == PayType.wechat:
            return '微信支付'
        elif type == PayType.alipay:
            return '支付宝'
        elif type == PayType.online:
            return '在线支付'
        elif type == PayType.others:
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
        if type == OrderStatus.order:
            return '未支付'
        elif type == OrderStatus.ordered:
            return '已支付'
        elif type == OrderStatus.cancelled:
            return '已取消'
        elif type == OrderStatus.finished:
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
        if type == GenderType.male:
            return '男'
        elif type == GenderType.female:
            return '女'
        else:
            return '未知'

# 用户
@lm.user_loader
def load_user(username):
    return Users.query.filter_by(username=username).first()

class Users(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(String(32), unique=True, nullable=False, index=True) # 用户名
    password = db.Column(String(32), nullable=False) # 密码密文
    phone = db.Column(String(16), unique=True, nullable=False, index=True) # 手机号
    email = db.Column(String(64), unique=True, nullable=True, index=True) # 邮箱（后期可选）
    name = db.Column(String(32), nullable=False) # 姓名
    active = db.Column(Boolean, default=False, nullable=False) # 是否激活, false：未激活， true：激活； 未激活状态无法登录
    salt = db.Column(String(64), nullable=False) # 安全登录
    block = db.Column(Boolean, default=False, nullable=False) # 是否封禁
    type = db.Column(Integer, default=UserType.normal) # 用户类别
    birth = db.Column(Date) # 出生日期
    gender = db.Column(Integer, default=GenderType.undefined) # 性别
    desc = db.Column(String(64), nullable=True) # 基本信息
    extend = db.Column(String(256), nullable=True) # 扩展信息

    def __init__(self, username, password, phone, email, name, type=UserType.normal):
        self.username = username
        self.salt = binascii.hexlify(os.urandom(16))
        self.password = Users.get_crypto_password(password, self.salt)
        self.phone = phone
        self.email = email
        self.name = name
        self.active = False
        self.block = False
        self.type = type
        
    def __repr__(self):
        return self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.username)

    def is_privileged(self, level):
        return self.type >= level

    # 获取可读名称
    def getName(self):
        if self.name=='':
            return self.username
        else:
            return self.name

    # 封禁/解封
    def do_forbid(self, block):
        self.block = block
        db.session.add(self)
        db.session.commit()

    # 激活用户
    def do_active(self):
        self.active = True
        db.session.add(self)
        db.session.commit()

    # 重置密码
    def reset_password(self, password):
        self.salt = binascii.hexlify(os.urandom(16))
        self.password = Users.get_crypto_password(password, self.salt)
        db.session.add(self)
        db.session.commit()

    # 更新信息
    def update_info(self, birth, gender, desc='', extend=''):
        self.birth = birth
        self.gender = gender
        self.desc = desc
        self.extend = extend
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_crypto_password(password, salt):
        return hashlib.md5(password + salt).hexdigest()

# 学生
class Student(db.Model):
    sid = db.Column(Integer, primary_key=True) 
    username = db.Column(String(32), unique=True, nullable=False, index=True) # ForeignKey('Users.username')
    # birth = db.Column(Date) # 出生日期
    # gender = db.Column(Integer, default=GenderType.undefined) # 性别
    # school = db.Column(String(64)) # 学校
    # extend = db.Column(String(64), nullable=True)

    def __init__(self, username):
        self.username = username
        # self.birth = birth
        # self.gender = gender
        # self.school = school
        # self.extend = extend
 
    def __repr__(self):
        return "<Student({:d}): {:s}>".format(self.sid, self.username)

# 教师
class Teacher(db.Model):
    tid = db.Column(Integer, primary_key=True)
    username = db.Column(String(32), unique=True, nullable=False, index=True) # ForeignKey('Users.username')
    # birth = db.Column(Date)
    # gender = db.Column(Integer, default=GenderType.undefined)
    gtype = db.Column(Integer)
    uprice = db.Column(Float, default=0.0)
    # desc = db.Column(String(128))
    # extend = db.Column(String(64), nullable=True)

    def __init__(self, username, gtype, uprice=0.0):
        self.username = username
        # self.birth = birth
        # self.gender = gender
        self.gtype = gtype
        self.uprice = uprice
        # self.desc = desc
        # self.extend = extend
 
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
    name = db.Column(String(32), unique=True, nullable=False)
    active = db.Column(Boolean, default=True) # 是否上架
    gtype = db.Column(Integer, nullable=False)
    time = db.Column(String(64), nullable=False)
    max_student = db.Column(Integer) # 最大学生人数
    min_student = db.Column(Integer) # 最小学生人数
    audition = db.Column(Integer) # 允许试听次数
    count = db.Column(Integer) # 课时次数
    period = db.Column(Integer) # 课时时长（以分钟计）
    charge = db.Column(Float) # 课程费用
    discount = db.Column(Float) # 折扣率（0.9=9折）
    status = db.Column(Integer)  # CourseStatus
    target = db.Column(String(64)) # 招生对象
    desc = db.Column(String(128)) # 课程介绍
    extend = db.Column(String(64)) # 备注

    def __init__(self, name, gtype, time, count, period, charge, active=True,
            max_student=65536, min_student=1, audition=0, discount=1, target='', desc='', extend=''):
        self.name = name
        self.active = active
        self.gtype = gtype;
        self.time = time
        self.count = count
        self.period = period
        self.charge = charge
        self.max_student = max_student
        self.min_student = min_student
        self.audition = audition
        self.discount = discount
        self.status = CourseStatus.applying
        self.target = target
        self.desc = desc
        self.extend = extend
 
    def __repr__(self):
        return "<Course{:d}: {:s}>".format(self.cid, self.name)

class CourseDetail(db.Model):
    cdid = db.Column(Integer, primary_key=True)     # 主键
    cid = db.Column(Integer, nullable=False)        # 课程 ForeignKey('Course.cid')
    index = db.Column(Integer, nullable=False)      # 同一个课程下的多个详情排序
    title = db.Column(String(32), nullable=False)   # 课程标题
    detail = db.Column(String(64), nullable=False)  # 具体内容
    extend = db.Column(String(64))

    def __init__(self, cid, index, title, detail, extend=''):
        self.cid = cid;
        self.index = index
        self.title = title
        self.detail = detail
        self.extend = extend
 
    def __repr__(self):
        return "<CourseDetail{:s} {:s}>".format(self.title, self.detail)

class CourseSchedule(db.Model):
    csid = db.Column(Integer, primary_key=True)     # 主键
    cid = db.Column(Integer, nullable=False)        # ForeignKey('Course.cid')
    rid = db.Column(Integer, nullable=False)        # 教室 ForeignKey('Room.rid')
    time = db.Column(String(32), nullable=False)    # 班次时间
    mteacher = db.Column(Integer, nullable=False)   # 主教 ForeignKey('Teacher.tid')
    bteacher = db.Column(Integer, nullable=True)    # 助教 ForeignKey('Teacher.tid')
    extend = db.Column(String(64))                  # 暂规定一个课程同时最多有2个教师

    def __init__(self, cid, rid, time, mteacher, bteacher=0, extend=''):
        self.cid = cid;
        self.rid = rid;
        self.time = time
        self.mteacher = mteacher
        self.bteacher = bteacher
        self.extend = extend

    def __repr__(self):
        return "<CourseSchedule{:d} {:s}>".format(self.cid, self.time)

#课程上课学生
class CourseStudent(db.Model):
    csid = db.Column(Integer, primary_key=True) #课程学生主键
    cid = db.Column(Integer, nullable=False) #ForeignKey('Course.cid')
    sid = db.Column(Integer, nullable=False) #ForeignKey('Student.sid')
    
    def __repr__(self):
        return "<CourseStudent{:d}:{:d}:{:d}>".format(self.csid, self.cid, seld.sid)



# 教室
class Room(db.Model):
    rid = db.Column(Integer, primary_key=True)
    name = db.Column(String(64), unique=True, nullable=False)
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
 