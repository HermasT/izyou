#coding: utf-8
import os, sys, hashlib, math
sys.path.append(os.path.dirname(__name__))

from portal import app
from portal import db
from portal.models import UserType, GameType, PayType, GenderType
from portal.models import Users, Student, Teacher, Course, Room, Orders, OrdersList, ProductType, OrderStatus

if __name__ == '__main__':
	# 创建数据表
	db.create_all()

	# 默认用户初始化
	# u = Users(username="hermas", email='hermasTang@hotmail.com',
	#  	phone='13636539441', password='123456', name='测试员工', type=UserType.staff)
	# u.update_info(birth=u'1997-09-11', gender=GenderType.male, desc=u'河马')
	# db.session.add(u)
	# u = Users(username="test", email='test@qq.com',
	# 	phone='18612345678', password='123456', name='测试账号', type=UserType.registered)
	# u.update_info(birth=u'1997-09-11', gender=GenderType.female, desc=u'测试信息', extend=u'测试扩展信息')
	# db.session.add(u)
	# db.session.commit()


	# 添加学生 一个学生是一个用户的同时，包含特定的学生信息（以下2个语句必须在事务中执行）
	# u = Users(username=u'student', email=u'student@gmail.com',
	# 	phone=u'15187654321', password=u'123456', name=u'测试学生', type=UserType.student)
	# u.update_info(birth=u'1997-09-11', gender=GenderType.male, desc=u'人大附中', extend=u'桥牌特长班')
	# db.session.add(u)
	# s = Student(username=u.username)
	# db.session.add(s)
	# db.session.commit()


	# 添加讲师 一个讲师是一个用户的同时，包含特定的教师信息（以下2个语句必须在事务中执行）
	# u = Users(username=u'teacher', email=u'teacher@gmail.com',
	# 	phone=u'13924681357', password=u'123456', name=u'测试教师', type=UserType.faculty)
	# u.update_info(birth=u'1997-01-12', gender=GenderType.female, desc=u'人大硕士毕业', extend=u'数独特长')
	# db.session.add(u)
	# t = Teacher(username=u.username, gtype=GameType.bridge, uprice=200.0)
	# db.session.add(t)
	# db.session.commit()
	
	# for i in range(1, 18):
	# 	u = Users(username=u'bridge{0}'.format(i), email=u'teacher{0}@gmail.com'.format(i),
	# 		phone=u'{0}'.format(i + 19924681357), password=u'123456', name=u'桥牌教师{0}'.format(i), type=UserType.faculty)
	# 	u.update_info(birth=u'1997-01-12', gender=GenderType.female, desc=u'zoo', extend=u'特长')
	# 	db.session.add(u)
	# 	t = Teacher(username=u.username, gtype=GameType.bridge, uprice=200.0)
	# 	db.session.add(t)
	# 	db.session.commit()


	# 添加课程
	# c = Course(name=u'桥牌初级班', gtype=GameType.bridge, tid=2, start='2015 10-01', end='2015 12-01', count=10, 
	# 	period=120, charge=800.0, max_student=32, min_student=4, audition=1, discount=1, desc='', extend='')
	# db.session.add(c)
	# c = Course(name=u'桥牌高级班', gtype=GameType.bridge, tid=1, start='2015 10-01', end='2015 12-01', count=10, 
	# 	period=120, charge=1200.0, max_student=32, min_student=4, audition=1, discount=1, desc='', extend='')
	# db.session.add(c)
	# db.session.commit()

	# 添加教室
	# db.session.add(Room(name=u'信远桥牌俱乐部', location=u'东三环xx路12号', traffic=u'地铁8号线望京站5号口出站即到'))
	# db.session.commit()

	# 添加订单
	# o = Orders(username=u'student', op=u'hermas', amount=800.0, income=0, 
	# 	charged=True, status=OrderStatus.ordered, paytype=PayType.cash, extend='')
	# p = OrdersList(ptype=ProductType.course, pid=2, op=u'hermas', count=1, status=0, extend='')
	# db.session.add(o)
	# db.session.add(p)
	# db.session.commit()

	# 多表联合查询示例	 查询所有课程对应的授课教师的姓名
	#    SELECT Users.name
	#    FROM USERS, Teacher, Course
	#    WHERE Teacher.username==Users.username AND Teacher.tid==Course.tid
	# q = db.session.query(Users.name).join(Teacher, Teacher.username==Users.username).join(Course, Teacher.tid==Course.tid).all()
	# for user in q:
	# 	print user.name
