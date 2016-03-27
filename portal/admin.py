# coding: utf-8
import sys, time, math, json, requests, config
from urllib import urlencode, quote
from flask import Flask, flash, render_template, redirect, url_for, request, jsonify, g, send_file, abort
from sqlalchemy import desc, asc, or_
from flask_bootstrap import Bootstrap, StaticCDN
from flask_appconfig import AppConfig
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from portal import app, db, lm, mail
from models import Users, Teacher, Room, UserType, GenderType, GameType, PayType, Orders, OrdersList
from models import Course, CourseStatus, CourseDetail, CourseSchedule, CourseStudent

# 后台管理
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
	if current_user is not None and current_user.is_privileged(UserType.staff):

		userCount = Users.query.filter(Users.type <= 1).count()
		teacherCount = Teacher.query.count()
		courseCount = Course.query.count()
		roomCount = Room.query.count()

		return render_template('admin.html', username=current_user.username, registeredUserCount = userCount, teacherCount = teacherCount, courseCount = courseCount, roomCount = roomCount, index=1)
	else:
		abort(403)

# 师资管理
@app.route('/teacher', methods=['GET'])
@login_required
def teacher():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		page = request.args.get("page", 1)
		if page < 1:
			page = 1
		paginate = Teacher.query.order_by(Teacher.tid).paginate(int(page), config.PAGE_ITEMS, False)

		# 需要将相关的常量替换成可读字符串
		# 一种办法是使用ORM进行联合查询，这样的坏处是容易造成SQL复杂且不稳定
		# 因此直接使用数据后处理进行替换，效率虽低，但安全性和扩展性更好，对于本应用来说是可以接受的
		teachers = []
		for teacher in paginate.items:
			user = Users.query.filter(Users.username==teacher.username).first()
			teacher.name = user.name
			teacher.birth = user.birth
			teacher.gender = GenderType.getName(user.gender)
			teacher.gtypename = GameType.getName(teacher.gtype) # gtypename
			teacher.desc = user.desc
			teacher.extend = user.extend
			# teachers.append(teacher)
		return render_template('teacher.html', username=current_user.username, index=2, pagination=paginate)
	else:
		abort(403)

@app.route('/add_teacher', methods=['GET'])
@login_required
def add_teacher():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		return render_template('add_teacher.html', username=current_user.username, index=2, types=GameType.getAll())
	else:
		abort(403)

@app.route('/search_teacher', methods=['GET'])
@login_required
def search_teacher():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		# 由于使用站内搜索功能时结果集一般很少，为简单起见不再支持分页
		name = request.args.get("username")
		if name == '':
			return render_template('error.html', message='请输入查询的教师用户名')
		try:
			pattern = '%' + name + '%'	# 支持模糊查询
			result = Teacher.query.filter(Teacher.username.like(pattern)).order_by(Teacher.tid).all()

			teachers = []
			for teacher in result:
				user = Users.query.filter(Users.username==teacher.username).first()
				teacher.name = user.name
				teacher.birth = user.birth
				teacher.gender = GenderType.getName(user.gender)
				teacher.gtype = GameType.getName(teacher.gtype)
				teacher.desc = user.desc
				teacher.extend = user.extend
				teachers.append(teacher)
			return render_template('search_teacher.html', username=current_user.username, teachers=teachers)
		except Exception , e:
			# app.logger.error(e)
			return render_template('error.html', message='查询失败')
	else:
		abort(403)

@app.route('/update_teacher', methods=['GET'])
@login_required
def update_teacher():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		tid = request.args.get('tid')
		teacher = Teacher.query.filter(Teacher.tid==tid).first()

		if teacher is None:
			return render_template('error.html', message='查找不到与之匹配的讲师')
		else:
			user = Users.query.filter(Users.username==teacher.username).first()
			if not user:
				return render_template('error.html', message='找不到教师的基本用户数据')
			else:
				return render_template('update_teacher.html', username=current_user.username, teacher=teacher, types=GameType.getAll(),
				genderName=GenderType.getName(user.gender), gname=GameType.getName(teacher.gtype))
	else:
		abort(403)

# 课程管理
@app.route('/course', methods=['GET', 'POST'])
@login_required
def course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		page = request.args.get("page", 1)
		if page < 1:
			page = 1

		paginate = Course.query.order_by(Course.cid).paginate(int(page), config.PAGE_ITEMS, False)
		for course in paginate.items:
			schedule_count = db.session.query(CourseSchedule).filter(CourseSchedule.cid==course.cid).count()
			course.scount = schedule_count

			studentCount = db.session.query(CourseStudent).filter(CourseStudent.cid == course.cid).count()
			course.studentCount = studentCount

			studentIsFull = '已满员' if studentCount >= course.max_student else '未满员'
			course.studentIsFull = studentIsFull

		return render_template('course.html', index=3, username=current_user.username, pagination=paginate)
	else:
		abort(403)

@app.route('/create_course', methods=['GET'])
@login_required
def create_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		teachers = Teacher.query.order_by(Teacher.tid).all()
		print teachers
		return render_template('create_course.html', username=current_user.username, types=GameType.getAll(), teachers=teachers)
	else:
		abort(403)

@app.route('/add_course_detail', methods=['GET'])
@login_required
def add_course_detail():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		cid = request.args.get("cid")
		name = request.args.get("name")
		count = request.args.get("count")
		return render_template('add_course_detail.html', username=current_user.username, cid=cid, name=name, count=count)
	else:
		abort(403)

@app.route('/add_course_schedule', methods=['GET'])
@login_required
def add_course_schedule():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		cid = request.args.get("cid")
		name = request.args.get("name")
		return render_template('add_course_schedule.html', username=current_user.username, cid=cid, name=name)
	else:
		abort(403)

@app.route('/search_course', methods=['GET'])
@login_required
def search_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		name = request.args.get("q")
		try:
			pattern = '%' + name + '%'
			result = Course.query.filter(Course.name.like(pattern)).order_by(Course.cid).all()
			for course in result:
				schedule_count = db.session.query(CourseSchedule).filter(CourseSchedule.cid==course.cid).count()
				course.scount = schedule_count
			return render_template('search_course.html', username=current_user.username, courses=result, index=3)
		except Exception, e:
			print e
			return render_template('error.html', message='查询失败')
	else:
		abort(403)

@app.route('/update_course', methods=['GET'])
@login_required
def update_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		cid = request.args.get('cid')
		course = Course.query.filter(Course.cid==cid).first()
		print course
		if course is None:
			return render_template('error.html', message='查找不到与之匹配的课程')
		else:
			# status = CourseStatus.getName(course.status)
			# teacher = Teacher.query.filter(Teacher.tid==course.tid).first()
			# allteachers = Teacher.query.order_by(Teacher.tid).all()
			gtype = {'type':course.gtype, "name": GameType.getName(course.gtype)}
			return render_template('update_course.html', username=current_user.username, course=course,
				gtype = gtype, types=GameType.getAll())
	else:
		abort(403)

@app.route('/register_course',methods=['GET'])
@login_required
def register_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		cid = request.args.get('cid')
		username = request.args.get('username')

		course = Course.query.filter(Course.cid==cid).first()
		user = Users.query.filter(Users.username==username).first()
		if course is None:
			return render_template('error.html', message='查找不到与之匹配的课程')
		elif user is None:
			return render_template('error.html', message='查找不到与之匹配的用户')
		else:
			status = CourseStatus.getName(course.status)
			teacher = Teacher.query.filter(Teacher.tid==course.tid).first()
			allteachers = Teacher.query.order_by(Teacher.tid).all()
			return render_template('register_course.html', username=current_user.username, course=course, pays=PayType.getAll())
	else:
		abort(403)

# 用户管理
@app.route('/user', methods=['GET'])
@login_required
def user():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		page = request.args.get("page", 1)
		if page < 1:
			page = 1
		paginate = Users.query.order_by(Users.uid).paginate(int(page), config.PAGE_ITEMS, False)

		users = []
		for user in paginate.items:
			user.gender = GenderType.getName(user.gender)
			user.type = UserType.getName(user.type)
			users.append(user)
		return render_template('user.html', username=current_user.username, index=4, pagination=paginate)
	else:
		abort(403)

@app.route('/userinfo', methods=['GET'])
@login_required
def userinfo():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		username = request.args.get("username")
		if not username:
			abort(404)
		else:
			return render_template('userinfo.html', username=current_user.username, index=4)
	else:
		abort(403)

@app.route('/search_user', methods=['GET'])
@login_required
def search_user():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		# 由于使用站内搜索功能时结果集一般很少，为简单起见不再支持分页
		name = request.args.get("username")
		if name == '':
			return render_template('error.html', message='请输入查询的用户名')
		try:
			pattern = '%' + name + '%'	# 支持模糊查询
			result = Users.query.filter(
				or_(Users.username.like(pattern), Users.phone.like(pattern), Users.email.like(pattern))).order_by(Users.uid).all()
			users = []
			for user in result:
				user.gender = GenderType.getName(user.gender)
				user.type = UserType.getName(user.type)
				users.append(user)
			return render_template('search_user.html', username=current_user.username, users=result, index=4)
		except Exception , e:
			# app.logger.error(e)
			return render_template('error.html', message='查询失败')
	else:
		abort(403)

# 教室管理
@app.route('/room', methods=['GET'])
@login_required
def room():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		page = request.args.get("page", 1)
		if page < 1:
			page = 1
		paginate = Room.query.paginate(int(page), config.PAGE_ITEMS, False)
		return render_template('room.html', username=current_user.username, pagination=paginate, index=5)
	else:
		abort(403)

@app.route('/search_room', methods=['GET'])
@login_required
def search_room():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		# 由于使用站内搜索功能时结果集一般很少，为简单起见不再支持分页
		name = request.args.get("q")
		if name == '':
			return render_template('error.html', message='请输入查询的教室信息')
		try:
			pattern = '%' + name + '%'	# 支持模糊查询
			result = Room.query.filter(Room.name.like(pattern)).order_by(Room.rid).all()
			return render_template('search_room.html', username=current_user.username, rooms=result, index=5)
		except Exception , e:
			# app.logger.error(e)
			return render_template('error.html', message='查询失败')
	else:
		abort(403)

@app.route('/add_room', methods=['GET'])
@login_required
def add_room():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		page = request.args.get("page", 1)
		if page < 1:
			page = 1
		paginate = Room.query.paginate(int(page), config.PAGE_ITEMS, False)
		return render_template('add_room.html', username=current_user.username, pagination=paginate, index=5)
	else:
		abort(403)