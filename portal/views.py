# coding: utf-8
import sys, time, math, json, requests, config
from urllib import urlencode, quote
from flask import Flask, flash, render_template, redirect, url_for, request, jsonify, g
from sqlalchemy import desc, asc
from flask_bootstrap import Bootstrap, StaticCDN
from flask_appconfig import AppConfig
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from portal import app, db, lm, mail
from models import Users, Teacher, Room, Course, UserType, GenderType, GameType, CourseStatus, PayType, Register
from mail import MailUtil

# 测试页面
@app.route('/test')
def test():
	message = MailUtil.buildMessage('test subject', sender=config.MAIL_USERNAME, recipients=['hermasTang@hotmail.com'], body='test body')
	mailthread = MailUtil(message)
	mailthread.start()
        return render_template('test.html')

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
    return render_template('login.html', next=request.args.get('next', ''))

# 登出
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')

# 首页
@app.route('/', methods=("GET", "POST"))
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/', methods = ['GET', 'POST'])
def index():
	try:
		username = current_user.username
		return render_template('index.html', index=1, user=username)
	except:
		return render_template('index.html', index=1, user=None)

# 关于
@app.route('/about', methods=['GET', 'POST'])
@login_required
def about():
	try:
		username = current_user.username
		return render_template('about.html', index=2, user=username)
	except:
		return render_template('about.html', index=2, user=None)

# 师资
@app.route('/fanculty', methods=['GET', 'POST'])
@login_required
def fanculty():
	try:
		username = current_user.username
		return render_template('fanculty.html', index=3, user=username)
	except:
		return render_template('fanculty.html', index=3, user=None)

# 联系
@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
	try:
		username = current_user.username
		return render_template('contact.html', index=4, user=username)
	except:
		return render_template('contact.html', index=4, user=None)

# 后台管理
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		return render_template('admin.html')
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
		return render_template('teacher.html', index=2, pagination=paginate)
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		return render_template('add_teacher.html')
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
			result = Teacher.query.filter(Teacher.name.like(pattern)).order_by(Teacher.tid).all()

			teachers = []
			for teacher in result:
				teacher.gender = GenderType.getName(teacher.gender)
				teacher.gtype = GameType.getName(teacher.gtype)
				teachers.append(teacher)
			return render_template('search_teacher.html', teachers=teachers)
		except:
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
			return render_template('update_teacher.html', teacher=teacher, 
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
		return render_template('course.html', index=3, user=current_user, pagination=paginate, status=status, teachers=teachers)
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

@app.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
	if current_user is not None and current_user.is_privileged(UserType.staff):
		teachers = Teacher.query.order_by(Teacher.tid).all()
		return render_template('create_course.html', teachers=teachers)
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
			return render_template('search_course.html', courses=result, status=status, teachers=teachers)
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
			return render_template('update_course.html', course=course, 
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
			return render_template('register_course.html', course=course, pays=PayType.getAll())
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
		return render_template('room.html', pagination=paginate)
	else:
		flash(u'您没有权限访问该页面')
		return render_template('error.html')

# REST APIs
@app.route('/rest/login', methods=['GET'])
def api_login():
    username = request.args.get("username")
    password = request.args.get("password")

    u = Users.query.filter_by(username=username).first()
    if not u:
        return jsonify({'error':1, 'cause':'用户名不存在'})
    elif u.password != Users.get_crypto_password(password):
        return jsonify({'error':2, 'cause':'密码不正确'})
    else:
    	login_user(u, remember=True)
        return jsonify({'error':0, 'next': request.args.get('next')})

@app.route('/after_login', methods=['GET'])
def after_login():
	next = request.args.get('next')
	return redirect(next or url_for('index'))

@app.route('/rest/register', methods=['GET'])
def api_register():
    username = request.args.get("username")
    password = request.args.get("password")
    phone = request.args.get("phone")
    email = request.args.get("email")
    name = request.args.get("name")

    u = Users.query.filter_by(username=username).first()
    if u:
    	return jsonify({'error':3, 'cause':'用户名已存在'})
    else:
	    r = Users(username=username, password=password, phone=phone, email=email, name=name)
	    try :
		    db.session.add(r)
		    db.session.commit()
		    return jsonify({'error':0})
	    except:
		    return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/add_teacher', methods=['GET', 'POST'])
def api_add_teacher():
	name = request.args.get("name")
	birth = request.args.get("birth")
	gender = request.args.get("gender")
	gtype = request.args.get("gtype")
	uprice = request.args.get("uprice")
	desc = request.args.get("desc")
	extend = request.args.get("extend")
	if uprice is None or uprice == "":
		uprice = 0.0

	try:
		t = Teacher(name=name, birth=birth, gender=gender, gtype=gtype, uprice=uprice, desc=desc, extend=extend)
		db.session.add(t)
		db.session.commit()
		return jsonify({'error':0, 'tid': t.tid})
	except:
		return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/update_teacher', methods=['GET', 'POST'])
def api_update_teacher():
	try:
		tid = request.args.get('tid')
		teacher = Teacher.query.filter(Teacher.tid==tid).first()
		if teacher is None:
			flash(u'查找不到与之匹配的讲师信息')
			return render_template('error.html')
		else:
			teacher.name = request.args.get("name")
			teacher.birth = request.args.get("birth")
			teacher.gender = request.args.get("gender")
			teacher.gtype = request.args.get("gtype")
			teacher.desc = request.args.get("desc")
			teacher.extend = request.args.get("extend")
			uprice = request.args.get("uprice")
			if uprice is None or uprice == "":
				teacher.uprice = 0.0
			else:
				teacher.uprice = uprice

			db.session.add(teacher)
			db.session.commit()
			return jsonify({'error':0})
	except:
		return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/create_course', methods=['GET', 'POST'])
def api_create_course():
	name = request.args.get("name")
	start = request.args.get("start")
	end = request.args.get("end")
	tid = request.args.get("teacher")
	count = request.args.get("count")
	fee = request.args.get("fee")
	desc = request.args.get("desc")
	extend = request.args.get("extend")

	try:
		c = Course(name=name, tid=tid, start=start, end=end, count=count, charge=fee, desc=desc, extend=extend)
		db.session.add(c)
		db.session.commit()
		return jsonify({'error':0, 'cid': c.cid})
	except:
		return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/update_course', methods=['GET', 'POST'])
def api_update_course():
	try:
		cid = request.args.get('cid')
		course = Course.query.filter(Course.cid==cid).first()
		if course is None:
			flash(u'查找不到与之匹配的课程信息')
			return render_template('error.html')
		else:
			course.name = request.args.get("name")
			course.status = request.args.get("status")
			course.tid = request.args.get("teacher")
			course.start = request.args.get("start")
			course.end = request.args.get("end")
			course.count = request.args.get("count")
			course.desc = request.args.get("desc")
			course.charge = request.args.get("fee")
			course.extend = request.args.get("extend")

			db.session.commit()
			return jsonify({'error':0})
	except:
		return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/register_course', methods=['GET', 'POST'])
def api_register_course():
	try:
		cid = request.args.get('cid')
		username = request.args.get("username")
		paytype = request.args.get("paytype")
		extend = request.args.get("extend")
		course = Course.query.filter(Course.cid==cid).first()
		user = Users.query.filter(Users.username==username).first()
		if course is None:
			flash(u'查找不到与之匹配的课程信息')
			return render_template('error.html')
		elif user is None:
			flash(u'查找不到报名的用户，请先注册用户')
			return render_template('error.html')
		else:
			operator = current_user.username
			if paytype == 0 or paytype == str(0):
				charged = False
			else:
				charged = True
			register = Register(username=username, cid=cid, op=operator, charged=charged, ptype=paytype, extend=extend)
			db.session.add(register)
			db.session.commit()
			return jsonify({'error':0, 'rid': register.rid})
	except:
		return jsonify({'error':4, 'cause': '数据库操作失败'})
