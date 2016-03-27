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
from models import Users, Teacher, Room, Course, CourseDetail, CourseStudent, UserType, GenderType, GameType
from models import CourseStatus, PayType, Orders, OrdersList, CourseSchedule
from mail import MailUtil
from sms import SmsUtil

# 测试页面
@app.route('/test')
def test():
	print '1111111111111111111111111111111111111111111111111111111111111111111111111111'
	userCount = Users.query.filter(Users.type >= 5 ).count()
	print 'userCount', userCount

	# SmsUtil.requestCode('18516595221')
	# SmsUtil.verifyCode('18516595221', '916838')

	# message = MailUtil.buildMessage('test subject', sender=config.MAIL_USERNAME, recipients=['hermasTang@hotmail.com'], body='test body')
	# mailthread = MailUtil(message)
	# mailthread.start()
	# return render_template('test.html')
	return render_template('dynamic_title.html')

# 用户激活
@app.route('/user_active')
def user_active():
	uid = request.args.get("uid")
	user = Users.query.filter(Users.uid == uid).first()
	if not user:
		abort(404)
	else:
		user.do_active();

	return render_template('index.html', index=1, username=user.username)

# 异常
@app.errorhandler(403)
def internal_error(error):
	return render_template('error.html', message='您没有权限访问该页面')

@app.errorhandler(404)
def internal_error(error):
	return render_template('error.html', message='您访问的页面不存在')

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('error.html', message='服务器发生了错误')

# 注入
@app.before_request
def before_request():
    g.user = current_user

# 登录
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    username=request.args.get('username')
    if username:
        return render_template('login.html', username=request.args.get('username'), next=request.args.get('next', ''))
    else:
        return render_template('login.html', username='', next=request.args.get('next', ''))

# 登出
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

# 账号激活（手机）
@app.route('/active', methods=['GET'])
def active():
	username = request.args.get("username")
	user = Users.query.filter(Users.username == username).first()
	if not user:
		abort(404)
	elif user.active == True:
		# flash(u'您尝试激活的账号已处于激活状态')
		app.logger.warning('your account is active')
		return redirect(url_for('index'))
	else:
		return render_template('user_active.html', username=user.username)

# 重置密码
@app.route('/reset_password', methods=['GET'])
def reset_password():
	return render_template('reset_password.html')

# 使用协议
@app.route('/terms', methods=['GET'])
def terms():
	return render_template('terms.html')

# 首页
@app.route('/', methods=("GET", "POST"))
@app.route('/index', methods = ['GET', 'POST'])
def index():
	try:
		username = current_user.username
		return render_template('index.html', index=1, username=username)
	except:
		return render_template('index.html', index=1, username=None)

# 桥牌介绍
@app.route('/bridge_detail', methods = ['GET'])
def bridge_detail():
	try:
		username = current_user.username
		return render_template('bridge_detail.html', username=username)
	except:
		return render_template('bridge_detail.html', username=None)

# 围棋介绍
@app.route('/go_detail', methods = ['GET'])
def go_detail():
	try:
		username = current_user.username
		return render_template('go_detail.html', username=username)
	except:
		return render_template('go_detail.html', username=None)

# 数独介绍
@app.route('/sudoku_detail', methods = ['GET'])
def sudoku_detail():
	try:
		username = current_user.username
		return render_template('sudoku_detail.html', username=username)
	except:
		return render_template('sudoku_detail.html', username=None)	

# 象棋介绍
@app.route('/xiangqi_detail', methods = ['GET'])
def xiangqi_detail():
	try:
		username = current_user.username
		return render_template('xiangqi_detail.html', username=username)
	except:
		return render_template('xiangqi_detail.html', username=None)

# 所有课程
@app.route('/all_courses', methods = ['GET'])
def all_courses():
	gtype = request.args.get("type", GameType.bridge)
	if int(gtype) == GameType.bridge:
		pagetitle = '智益加2016年春季桥牌课程安排'
	elif int(gtype) == GameType.sudoku:
		pagetitle = '智益加2016年春季数独课程安排'
	elif int(gtype) == GameType.go:
		pagetitle = '智益加2016年春季围棋课程安排'
	elif int(gtype) == GameType.xiangqi:
		pagetitle = '智益加2016年春季象棋课程安排'

	courses = Course.query.filter(Course.gtype==gtype, Course.status<2, Course.active==True).all() # 可以报名的课程
	if courses is not None:
		for c in courses:
			contents = CourseDetail.query.filter(CourseDetail.cid == c.cid).order_by(CourseDetail.index).all()
			if contents is not None:
				c.contents = contents	

			schedules = CourseSchedule.query.filter(CourseSchedule.cid == c.cid).all()
			if schedules is not None:
				for schedule in schedules:
					print '111111111111111111111111111111111111111111111111111111111111111111'
					mteacher = Teacher.query.filter(Teacher.tid == schedule.mteacher).first();
					muser = Users.query.filter(Users.username==mteacher.username).first()
					if muser:
						schedule.mteachername = muser.getName() # 

					bteacher = Teacher.query.filter(Teacher.tid == schedule.bteacher).first();

					schedule.bteachername = ''
					if bteacher:
						buser = Users.query.filter(Users.username==bteacher.username).first()
						if buser:
							# print 'buser', bteacher.username, buser
							schedule.bteachername = buser.getName()

					room = Room.query.filter(Room.rid==schedule.rid).first();
					if room:
						schedule.room = room.name
				c.schedules = schedules
	else:
		courses = []

	try:
		username = current_user.username
		return render_template('all_course.html', username=username, pagetitle=pagetitle, courses=courses)
	except:
		return render_template('all_course.html', username=None, pagetitle=pagetitle, courses=courses)

@app.route('/course_info', methods = ['GET'])
@login_required
def course_info():
	cid = request.args.get("cid", -1)
	if int(cid) == -1:
		abort(404)

	courses = []
	pagetitle = '课程信息预览'

	c = Course.query.filter(Course.cid==cid).first()
	if c is not None:
		courses.append(c)
		contents = CourseDetail.query.filter(CourseDetail.cid == c.cid).order_by(CourseDetail.index).all()
		if contents is not None:
			c.contents = contents

		schedules = CourseSchedule.query.filter(CourseSchedule.cid == c.cid).all()
		if schedules is not None:
			for schedule in schedules:
				mteacher = Teacher.query.filter(Teacher.tid == schedule.mteacher).first();
				muser = Users.query.filter(Users.username==mteacher.username).first()
				if muser:
					schedule.mteachername = muser.getName()

				bteacher = Teacher.query.filter(Teacher.tid == schedule.bteacher).first();
				schedule.bteachername = ''
				if bteacher:
					buser = Users.query.filter(Users.username==bteacher.username).first()
					if buser:
						schedule.bteachername = buser.getName()

				room = Room.query.filter(Room.rid==schedule.rid).first();
				if room:
					schedule.room = room.name
			c.schedules = schedules

	try:
		username = current_user.username
		return render_template('all_course.html', username=username, pagetitle='课程信息预览', courses=courses)
	except:
		return render_template('all_course.html', username=None, pagetitle='课程信息预览', courses=courses)

 #我要报名
@app.route('/course_userregister', methods = ['GET'])
@login_required
def course_userregister():
	if current_user is not None and current_user.is_privileged(UserType.registered):
		cid = request.args.get('cid')
		course = Course.query.filter(Course.cid==cid).first()

		if course is None:
			return render_template('error.html', message='查找不到与之匹配的课程')
		else:

			status = CourseStatus.getName(course.status)
			#teacher = Teacher.query.filter(Teacher.tid==course.tid).first()
			#allteachers = Teacher.query.order_by(Teacher.tid).all()
			studentCount =  CourseStudent.query.filter(CourseStudent.cid == cid).count()
			return render_template('register_usercourse.html', username=current_user.username, course=course, studentCount=studentCount, pays=PayType.getAll())
	else:
		return render_template('error.html', message='请您登录')


# 我要报名
@app.route('/course_register', methods = ['GET'])
@login_required
def course_register():
	if current_user is not None and current_user.is_privileged(UserType.registered):
		page = request.args.get("page", 1)
		if page < 1:
			page = 1

		gtype = request.args.get('type', GameType.undefined)
		try:
			if int(gtype) >= GameType.count:
				gtype = GameType.undefined
		except:
			gtype = GameType.undefined
		
		if int(gtype) == GameType.undefined:
			paginate = Course.query.order_by(Course.cid).paginate(int(page), config.PAGE_ITEMS, False)
		else:
			paginate = Course.query.filter(Course.gtype==gtype, Course.status<2).order_by(desc(Course.cid)).paginate(int(page), config.PAGE_ITEMS, False)

		status = []
		teachers = []
		for course in paginate.items:
			status.append(CourseStatus.getName(course.status))
			# 采用多表联合查询
			q = db.session.query(Users.name).join(Teacher, Teacher.username==Users.username) \
					.filter(Teacher.tid==course.tid).first()
			teachers.append(q.username)
		return render_template('course_register.html', index=5, type=gtype,
			username=current_user.username, pagination=paginate, status=status, teachers=teachers)
	else:
		return render_template('error.html', message='请您登录')

# # 用户基本信息 
# @app.route('/userprofile', methods = ['GET'])
# @login_required
# def userprofile():

# 	if current_user is not None and current_user.is_privileged(UserType.registered):
# 		username = request.args.get("username")

# 		if not username:
# 			abort(404)
# 		elif current_user.username.lower() != username.lower():
# 			abort(404)
# 		else:
# 			return render_template('userprofile.html', username=current_user.username, user=current_user, genderName = GenderType.getName(current_user.gender), birthStr = current_user.getBirthStr())
# 	else:
# 		abort(403)

# 用户基本信息 
@app.route('/edit_userprofile', methods = ['GET'])
@app.route('/userprofile', methods = ['GET'])
@login_required
def edit_userprofile():
	if current_user is not None and current_user.is_privileged(UserType.registered):
		username = request.args.get("username")
		if not username:
			abort(404)
		elif current_user.username.lower() != username.lower():
			abort(403)
		else:
			return render_template('edit_userprofile.html', username=current_user.username, user=current_user, 
				genderName = GenderType.getName(current_user.gender), typeName=UserType.getName(current_user.type), birthStr = current_user.getBirthStr())
	else:
		abort(403)

@app.route('/change_password', methods = ['GET'])
@login_required
def change_password():
	if current_user is not None and current_user.is_privileged(UserType.registered):
		username = request.args.get("username")
		if not username:
			abort(404)
		elif current_user.username.lower() != username.lower():
			abort(403)
		else:
			return render_template('change_password.html', username=current_user.username)
	else:
		abort(403)


# # 联系我们
# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
# 	try:
# 		username = current_user.username
# 		return render_template('contact.html', index=4, username=username)
# 	except:
# 		return render_template('contact.html', index=4, username=None)

