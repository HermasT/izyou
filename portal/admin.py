# coding: utf-8
import sys, time, math, json, requests, config
from urllib import urlencode, quote
from flask import Flask, flash, render_template, redirect, url_for, request, jsonify, g, send_file, abort
from sqlalchemy import desc, asc
from flask_bootstrap import Bootstrap, StaticCDN
from flask_appconfig import AppConfig
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from portal import app, db, lm, mail
from models import Users, Teacher, Room, Course, UserType, GenderType, GameType, CourseStatus, PayType, Orders, OrdersList

# 后台管理
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		return render_template('admin.html', username=current_user.username, index=1)
	else:
		abort(403)

# 师资管理
@app.route('/teacher', methods=['GET', 'POST'])
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
			teacher.gender = GenderType.getName(teacher.gender)
			teacher.gtype = GameType.getName(teacher.gtype)
			teachers.append(teacher)
		return render_template('teacher.html', username=current_user.username, index=2, pagination=paginate)
	else:
		abort(403)

@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		return render_template('add_teacher.html', username=current_user.username, index=2, types=GameType.getAll())
	else:
		abort(403)

@app.route('/search_teacher', methods=['GET', 'POST'])
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
				teacher.gender = GenderType.getName(teacher.gender)
				teacher.gtype = GameType.getName(teacher.gtype)
				teachers.append(teacher)
			return render_template('search_teacher.html', username=current_user.username, teachers=teachers)
		except Exception , e:
			# app.logger.error(e)
			return render_template('error.html', message='查询失败')
	else:
		abort(403)

@app.route('/update_teacher', methods=['GET', 'POST'])
@login_required
def update_teacher():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		tid = request.args.get('tid')
		teacher = Teacher.query.filter(Teacher.tid==tid).first()

		if teacher is None:
			return render_template('error.html', message='查找不到与之匹配的讲师')
		else:
			return render_template('update_teacher.html', username=current_user.username, teacher=teacher, types=GameType.getAll(),
				genderName=GenderType.getName(teacher.gender), gname=GameType.getName(teacher.gtype))
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

		# 需要从Course和Teacher两个表中进行联合查询
		# 第一种办法是直接关联，这样需要代码进行分页，实现太复杂
		# 第二种办法是直接对Course分页，然后根据外键进行关联查询
		paginate = Course.query.order_by(Course.cid).paginate(int(page), config.PAGE_ITEMS, False)

		status = []
		teachers = []
		for course in paginate.items:
			status.append(CourseStatus.getName(course.status))
			teacher = Teacher.query.filter(Teacher.tid==course.tid).first()
			teachers.append(teacher.username)
		return render_template('course.html', index=3, username=current_user.username, pagination=paginate, status=status, teachers=teachers)
	else:
		abort(403)

@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		teachers = Teacher.query.order_by(Teacher.tid).all()
		print teachers
		return render_template('create_course.html', username=current_user.username, types=GameType.getAll(), teachers=teachers)
	else:
		abort(403)

@app.route('/search_course', methods=['GET', 'POST'])
@login_required
def search_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		name = request.args.get("name")
		try:
			pattern = '%' + name + '%'
			result = Course.query.filter(Course.name.like(pattern)).order_by(Course.tid).all()

			status = []
			teachers = []
			for course in result:
				status.append(CourseStatus.getName(course.status))
				teacher = Teacher.query.filter(Teacher.tid==course.tid).first()
				teachers.append(teacher.name)
			return render_template('search_course.html', username=current_user.username, courses=result, status=status, teachers=teachers)
		except:
			return render_template('error.html', message='查询失败')
	else:
		abort(403)

@app.route('/update_course', methods=['GET', 'POST'])
@login_required
def update_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		cid = request.args.get('cid')
		course = Course.query.filter(Course.cid==cid).first()
		print course
		if course is None:
			return render_template('error.html', message='查找不到与之匹配的课程')
		else:
			status = CourseStatus.getName(course.status)
			teacher = Teacher.query.filter(Teacher.tid==course.tid).first()
			allteachers = Teacher.query.order_by(Teacher.tid).all()
			return render_template('update_course.html', username=current_user.username, course=course, 
				tname=teacher.username, teachers=allteachers, status=status, allstatus=CourseStatus.getAll())
	else:
		abort(403)

@app.route('/register_course',methods=['GET', 'POST'])
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

# 教室管理
@app.route('/room', methods=['GET', 'POST'])
@login_required
def room():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		page = request.args.get("page", 1)
		if page < 1:
			page = 1
		paginate = Room.query.paginate(int(page), config.PAGE_ITEMS, False)
		return render_template('room.html', username=current_user.username, pagination=paginate)
	else:
		abort(403)
