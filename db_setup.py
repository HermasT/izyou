#coding: utf-8
import os, sys, hashlib, math
sys.path.append(os.path.dirname(__name__))

from portal import app
from portal import db
from portal.models import UserType, GameType, PayType, GenderType
from portal.models import Users, Teacher, Course, Room, Register#, GType, UType, PType

if __name__ == '__main__':
	# 创建数据表
	db.create_all()

	# # 默认用户初始化
	# u = Users(username="hermas", email='hermasTang@hotmail.com', 
	# 	phone='13636539441', password='123456', name='汤时虎', type=UserType.staff)
	# db.session.add(u)
	# db.session.commit()

	# # 用户类型常量表初始化
	# db.session.add(UType(UserType.normal, u'normal', u'普通用户'))
	# db.session.add(UType(UserType.registered, u'registered', u'注册用户'))
	# db.session.add(UType(UserType.student, u'student', u'学员'))
	# db.session.add(UType(UserType.fanculty, u'fanculty', u'教工'))
	# db.session.add(UType(UserType.staff, u'staff', u'工作人员'))
	# db.session.add(UType(UserType.admin, u'admin', u'管理员'))
	# db.session.commit()

	# # 项目类型常量表初始化
	# db.session.add(GType(GameType.undefined, u'undefined', u'未定义'))
	# db.session.add(GType(GameType.bridge, u'bridge', u'桥牌'))
	# db.session.add(GType(GameType.sudoku, u'sudoku', u'数独'))
	# db.session.add(GType(GameType.go, u'go', u'围棋'))
	# db.session.add(GType(GameType.chess, u'chess', u'国际象棋'))
	# db.session.add(GType(GameType.cchess, u'cchess', u'中国象棋'))
	# db.session.add(GType(GameType.miexed, u'miexed', u'混合'))
	# db.session.commit()

	# # 项目类型常量表初始化
	# db.session.add(PType(PayType.undefined, u'undefined', u'未定义'))
	# db.session.add(PType(PayType.cash, u'cash', u'现金支付'))
	# db.session.add(PType(PayType.wechat, u'wechat', u'微信支付'))
	# db.session.add(PType(PayType.alipay, u'alipay', u'支付宝'))
	# db.session.add(PType(PayType.online, u'online', u'在线支付'))
	# db.session.add(PType(PayType.others, u'others', u'其他'))
	# db.session.commit()	

	# 添加讲师
	# db.session.add(Teacher(name=u'小爪', birth='1984 09-12', gender=GenderType.male, gtype=GameType.bridge, uprice=200.0))
	# db.session.commit()
	
	# for i in range(1, 18):
	# 	db.session.add(Teacher(name=u'围棋{0}'.format(i), birth='1982 09-12', gender=GenderType.male, gtype=GameType.bridge, uprice=200.0))
	# 	db.session.commit()

	# # 添加课程
	# db.session.add(Course(name=u'桥牌初级班', gtype=GameType.bridge, tid=2, start='2015 10-01', end='2015 12-01', count=10, charge=800.0))
	# db.session.add(Course(name=u'桥牌高级班', gtype=GameType.bridge, tid=1, start='2015 09-11', end='2015 12-01', count=10, charge=1200.0))
	# db.session.add(Course(name=u'数独入门班', gtype=GameType.sudoku, tid=3, start='2015 09-11', end='2015 12-01', count=10, charge=800.0))
	# db.session.commit()
	# for i in range(1, 8):
	# 	db.session.add(Course(name=u'围棋入门', gtype=GameType.go, tid=2, start='2015 10-01', end='2015 12-01', count=10, charge=800.0))
	# 	db.session.add(Course(name=u'数独高级班', gtype=GameType.sudoku, tid=2, start='2015 10-01', end='2015 12-01', count=10, charge=800.0))
	# 	db.session.add(Course(name=u'桥牌初级班', gtype=GameType.bridge, tid=2, start='2015 10-01', end='2015 12-01', count=10, charge=800.0))
	# 	db.session.commit()

	# # 添加教室
	# db.session.add(Room(name=u'信远桥牌俱乐部', location=u'东三环xx路12号', traffic=u'地铁8号线望京站5号口出站即到'))
	# db.session.commit()

	# # 添加报名
	# db.session.add(Register(uid=2, cid=2, charged=True, ptype=PayType.cash))
	# db.session.commit()