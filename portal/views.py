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
from mail import MailUtil
from sms import SmsUtil

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
	flash(u'服务器发生了错误')
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
		return render_template('error.html', message='请您登录')

# # 联系我们
# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
# 	try:
# 		username = current_user.username
# 		return render_template('contact.html', index=4, username=username)
# 	except:
# 		return render_template('contact.html', index=4, username=None)