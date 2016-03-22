# coding: utf-8
import sys, time, math, json, requests, config
from urllib import urlencode, quote
from flask import Flask, flash, render_template, redirect, url_for, request, jsonify, g, send_file
from sqlalchemy import desc, asc
from flask_bootstrap import Bootstrap, StaticCDN
from flask_appconfig import AppConfig
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from portal import app, db, lm, mail
from models import Users, Teacher, Room, Course, UserType, GenderType, GameType, CourseStatus, PayType, Orders, OrdersList
from mail import MailUtil
from sms import SmsUtil
import qrcode
import StringIO

# 测试页面
@app.route('/test')
def test():
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
		flash(u'您访问的页面不存在')
		return render_template('error.html')
	else:
		user.do_active();

	return render_template('index.html', index=1, username=user.username)

# 异常
@app.errorhandler(404)
def internal_error(error):
	flash(u'未找到页面')
	return render_template('error.html')
    # return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	flash(u'服务器发生了错误')
	db.session.rollback()
	return render_template('error.html')
	# return render_template('500.html'), 500

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
	username = request.args.get("user")
	user = Users.query.filter(Users.username == username).first()
	if not user:
		flash(u'您访问的页面不存在')
		return render_template('error.html')
	elif user.active == True:
		flash(u'您尝试激活的账号已处于激活状态')
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
	template = 'bridge_course.html'
	if int(gtype) == GameType.bridge:
		template = 'bridge_course.html'
	elif int(gtype) == GameType.sudoku:
		template = 'sudoku_course.html'
	elif int(gtype) == GameType.go:
		template = 'go_course.html'
	elif int(gtype) == GameType.xiangqi:
		template = 'xiangqi_course.html'

	try:
		username = current_user.username
		return render_template(template, username=username)
	except:
		return render_template(template, username=None)

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
			teachers.append(q.name)
		return render_template('course_register.html', index=5, type=gtype,
			username=current_user.username, pagination=paginate, status=status, teachers=teachers)
	else:
		flash(u'请您登录')
		return render_template('error.html')

# 联系我们
@app.route('/contact', methods=['GET', 'POST'])
def contact():
	try:
		username = current_user.username
		return render_template('contact.html', index=4, username=username)
	except:
		return render_template('contact.html', index=4, username=None)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		return render_template('admin.html', username=current_user.username)
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

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
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		return render_template('add_teacher.html', username=current_user.username, types=GameType.getAll())
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

@app.route('/search_teacher', methods=['GET', 'POST'])
@login_required
def search_teacher():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		# 由于使用站内搜索功能时结果集一般很少，为简单起见不再支持分页
		name = request.args.get("name")
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
 			print e
			flash(u'查询失败')
			return render_template('error.html')
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

@app.route('/update_teacher', methods=['GET', 'POST'])
@login_required
def update_teacher():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		tid = request.args.get('tid')
		teacher = Teacher.query.filter(Teacher.tid==tid).first()

		if teacher is None:
			flash(u'查找不到与之匹配的讲师')
			return render_template('error.html')
		else:
			return render_template('update_teacher.html', username=current_user.username, teacher=teacher, types=GameType.getAll(),
				genderName=GenderType.getName(teacher.gender), gname=GameType.getName(teacher.gtype))
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

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
			teachers.append(teacher.name)
		return render_template('course.html', index=3, username=current_user.username, pagination=paginate, status=status, teachers=teachers)
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		teachers = Teacher.query.order_by(Teacher.tid).all()
		print teachers
		return render_template('create_course.html', username=current_user.username, types=GameType.getAll(), teachers=teachers)
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

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
			flash(u'查询失败')
			return render_template('error.html')
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

@app.route('/update_course', methods=['GET', 'POST'])
@login_required
def update_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		cid = request.args.get('cid')
		course = Course.query.filter(Course.cid==cid).first()
		print course
		if course is None:
			flash(u'查找不到与之匹配的课程')
			return render_template('error.html')
		else:
			status = CourseStatus.getName(course.status)
			teacher = Teacher.query.filter(Teacher.tid==course.tid).first()
			allteachers = Teacher.query.order_by(Teacher.tid).all()
			return render_template('update_course.html', username=current_user.username, course=course, 
				tname=teacher.name, teachers=allteachers, status=status, allstatus=CourseStatus.getAll())
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

@app.route('/register_course',methods=['GET', 'POST'])
@login_required
def register_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		cid = request.args.get('cid')
		username = request.args.get('username')

		course = Course.query.filter(Course.cid==cid).first()
		user = Users.query.filter(Users.username==username).first()
		if course is None:
			flash(u'查找不到与之匹配的课程')
			return render_template('error.html')
		elif user is None:
			flash(u'查找不到与之匹配的用户')
			return render_template('error.html')
		else:
			status = CourseStatus.getName(course.status)
			teacher = Teacher.query.filter(Teacher.tid==course.tid).first()
			allteachers = Teacher.query.order_by(Teacher.tid).all()
			return render_template('register_course.html', username=current_user.username, course=course, pays=PayType.getAll())
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

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
		flash(u'您没有权限访问该页面')
		return render_template('error.html')
