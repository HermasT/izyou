#coding: utf-8
import os, sys, hashlib, math
sys.path.append(os.path.dirname(__name__))

from portal import app
from portal import db
from portal.models import UserType, GameType, PayType, GenderType, ProductType
from portal.models import Users, Student, Teacher, Course, Room, Orders, OrdersList, OrderStatus, CourseDetail, CourseSchedule

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
	# u.active = 1
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
	c = Course(name=u'初级提高班', gtype=GameType.bridge, time='3月5日起连续15周，每周2小时', count=15,
		period=120, charge=3600, max_student=16, min_student=12, audition=1, discount=0.9, step=3,
		target='面向9-14岁，零基础的学生', desc='1. 学中玩：收获乐趣，培养兴趣\n2. 玩中学：掌握初级知识，参与桥牌运动\n" \
		"3. 提升：沟通、合作、社交\n4. 进阶：为走向竞赛阶段打下坚实基础', extend='')
	db.session.add(c)
	title = ['走进桥牌', '数字的游戏', '比大小', '矛与盾', '制订计划', '四人参与', '弱牌的价值', 
		'防守方的武器','不确定的因素', '激动人心的满贯', '聚焦', '执行计划', '奇妙的桥牌', '习题课1', '习题课2']
	content = ['桥牌的基本概念、术语和发展史', '桥牌叫牌打牌所需基础知识', '1NT开叫及无将做庄',
		'一阶高花开叫相关知识和防守入门', '一阶低花开叫相关知识和做庄计划', '争叫和简要飞牌入门', 
		'阻击叫相关知识，出牌方向综述', '强开叫相关知识，防守信号入门', '飞牌知识深入，争叫后的应叫变化',
		'满贯叫牌介绍，桥路和次序', '标准美国黄卡介绍，单套处理', '加倍和再加倍介绍，攻防整体技巧', 
		'叫牌原则和约定叫总结，高级桥牌技巧概览', '无将做庄，牌型牌点计算', '有将做庄，简要读牌']
	for i in range(1, len(title) + 1):
		detail = CourseDetail(cid=1, index=i, title=title[i - 1], detail=content[i - 1])
		db.session.add(c)
		db.session.add(detail)
	time = ['每周六10:00~12:00', '每周六13:30~15:30', '每周六15:50~17:50',
		'每周六18:00~20:00', '每周日10:20~12:20', '每周日13:30~15:30', '每周日15:50~17:50']
	for i in range(1, len(time) + 1):
		schedule = CourseSchedule(cid=1, rid=1, index=i, time=time[i - 1], mteacher='1', bteacher='2')
		db.session.add(schedule)
	db.session.commit()

	c = Course(name=u'桥牌高级班', gtype=GameType.bridge, time='3月5日起连续15周，每周2小时', count=15,
		period=120, charge=4500, max_student=20, min_student=12, audition=1, discount=1, step=3,
		target='面向14岁的学生', desc='1. 学中玩：收获乐趣，培养兴趣\n2. 玩中学：掌握初级知识，参与桥牌运动\n" \
		"3. 提升：沟通、合作、社交\n4. 进阶：为走向竞赛阶段打下坚实基础', extend='')
	db.session.add(c)
	for i in range(1, len(title) + 1):
		detail = CourseDetail(cid=2, index=i, title=title[i - 1], detail=content[i - 1])
		db.session.add(detail)
	for i in range(1, len(time) + 1):
		schedule = CourseSchedule(cid=2, rid=1, index=i, time=time[i - 1], mteacher='2', bteacher='1')
		db.session.add(schedule)
	db.session.commit()

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
