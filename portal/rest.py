# coding: utf-8
import sys, time, math, json, requests, config
from urllib import urlencode, quote
from flask import Flask, flash, redirect, url_for, request, jsonify, send_file
from sqlalchemy import desc, asc, or_, not_
from flask_bootstrap import Bootstrap, StaticCDN
from flask_appconfig import AppConfig
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from portal import app, db, lm, mail
from models import Users, Teacher, Room, Course, UserType, GenderType, GameType, CourseStatus, PayType, Orders, OrdersList, OrderStatus
from mail import MailUtil
from sms import SmsUtil

# REST APIs
@app.route('/rest/login', methods=['GET'])
def api_login():
    account = request.args.get("username")
    password = request.args.get("password")

    u = Users.query.filter(or_(Users.username==account, Users.phone==account, Users.email==account)).first()
    if not u:
        return jsonify({'error':1, 'cause':'用户名不存在'})
    elif u.block == True:
        return jsonify({'error':2, 'cause':'您的账号已被封禁，请与管理员联系'})
    elif u.active != True:
        return jsonify({'error':3, 'cause':'用户未激活'})
    elif u.password != Users.get_crypto_password(password, u.salt):
        return jsonify({'error':4, 'cause':'密码不正确'})
    else:
    	login_user(u, remember=True)
        return jsonify({'error':0, 'next': request.args.get('next')})

@app.route('/rest/reset_password', methods=['POST'])
def api_reset_password():
    username = request.values.get("username")
    password = request.values.get("password")
    phone = request.values.get("phone")
    code = request.values.get("code")

    u = Users.query.filter_by(username=username).first()
    if not u:
        return jsonify({'error':1, 'cause':'用户名不存在'})
    elif u.phone != phone:
        return jsonify({'error':2, 'cause':'输入手机号与绑定手机号不一致'})
    else:
    	result = SmsUtil.verifyCode(phone, code)
    	result_dict = json.loads(result)
    	if (result_dict['error'] == 0):
			try:
				u.reset_password(password)
				return jsonify({"error":0})
			except:
				return jsonify({"error": 500, "cause": '更新数据库操作失败'})
    	else:
    		return jsonify({"error":result_dict['error'], "cause":result_dict['cause']})

@app.route('/after_login', methods=['GET'])
def after_login():
	next = request.args.get('next')
	return redirect(next or url_for('index'))

@app.route('/rest/register', methods=['POST'])
def api_register():
    username = request.values.get("username")
    password = request.values.get("password")
    phone = request.values.get("phone")
    email = request.values.get("email")
    name = request.values.get("name")

    # 用户名、手机号、邮箱 3个字段做匹配判断
    u = Users.query.filter_by(username=username).first()
    p = Users.query.filter_by(phone=phone).first()
    e = Users.query.filter_by(email=email).first()
    if u:
    	return jsonify({'error':3, 'cause':'用户名已存在'})
    elif p:
        return jsonify({'error':4, 'cause':'手机号已被注册'})
    elif e:
        return jsonify({'error':5, 'cause':'邮箱已被注册'})
    else:
	    r = Users(username=username, password=password, phone=phone, email=email, name=name)
	    try :
		    db.session.add(r)
		    db.session.commit()
		    return jsonify({'error':0})
	    except:
		    return jsonify({'error':6, 'cause': '数据库操作失败'})

@app.route('/rest/active_user', methods=['POST'])
def api_active_user():
	uid = request.values.get("uid")
	user = Users.query.filter_by(uid=uid).first()
	if not user:
		abort(404)
	else:
		try:
			user.do_active()
			return json.dumps({'error':0})
		except:
			return json.dumps({'error':1, 'cause':'更新失败'})

@app.route('/rest/forbid_user', methods=['POST'])
def api_forbid_user():
	uid = request.values.get("uid")
	block = request.values.get("block", 0)
	user = Users.query.filter_by(uid=uid).first()
	if not user:
		abort(404)
	else:
		try:
			user.do_forbid(block)
			return json.dumps({'error':0})
		except:
			return json.dumps({'error':1, 'cause':'更新失败'})

@app.route('/rest/request_code', methods=['POST'])
def api_request_sms_code():
	phone = request.values.get("phone")
	return SmsUtil.requestCode(phone)

@app.route('/rest/verify_code', methods=['POST'])
def api_verify_sms_code():
	mobile = request.values.get("phone")
	code = request.values.get("code")
	result = SmsUtil.verifyCode(mobile, code)
	result_dict = json.loads(result)
	if (result_dict['error'] == 0):
		username = request.values.get("username")
		user = Users.query.filter_by(username=username).first()
		if not user:
			return json.dumps({"error": 500, "cause": '当前用户不存在'})
		else:
			user.do_active();
	return result

@app.route('/rest/add_teacher', methods=['GET', 'POST'])
def api_add_teacher():
	name = request.args.get("name")
	# birth = request.args.get("birth")
	# gender = request.args.get("gender")
	gtype = request.args.get("gtype")
	uprice = request.args.get("uprice")
	# desc = request.args.get("desc")
	# extend = request.args.get("extend")
	if uprice is None or uprice == "":
		uprice = 0.0

	try:
		user = Users.query.filter(Users.username==name).first()
		teacher = Teacher.query.filter(Teacher.username==name).first()
		if not user:
			return jsonify({'error':403, 'cause': '您添加的教师用户名尚未注册，请先注册用户'})
		elif teacher:
			return jsonify({'error':403, 'cause': '您添加的教师用户名已经被使用了'})
		else:
			t = Teacher(username=name, gtype=gtype, uprice=uprice)
			db.session.add(t)
			db.session.commit()
			return jsonify({'error':0, 'tid': t.tid})
	except Exception , e:
		# app.logger.error(e)
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

@app.route('/rest/create_course', methods=['POST'])
def api_create_course():
	summary = json.loads(request.values.get('summary'))
	try:
		c = Course(name=summary['name'], gtype=summary['gtype'], time=summary['time'], count=summary['count'],
			period=summary['period'], charge=summary['charge'], max_student=summary['max'], min_student=summary['min'],
			audition=summary['audition'], target=summary['target'], desc=summary['desc'], extend=summary['extend'])
		db.session.add(c)
		db.session.commit()
		return jsonify({'error':0, 'cid': c.cid})
	except Exception, e:
		print e
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
			return jsonify({'error':5, 'cause': u'查找不到与之匹配的课程信息'})
		elif user is None:
			return jsonify({'error':5, 'cause': u'查找不到报名的用户，请先注册用户'})
		else:
			operator = current_user.username
			if paytype == 0 or paytype == str(0):
				charged = False
			else:
				charged = True
			# register = Register(username=username, cid=cid, op=operator, charged=charged, ptype=paytype, extend=extend)
			# db.session.add(register)
			order = Orders(username = username, op=operator, charged=charged, amount = 0, paytype=paytype, status=OrderStatus.order, extend=extend)
			db.session.add(order)

			db.session.commit()
			return jsonify({'error':0, 'rid': order.orderid})
	except Exception , e:
		print e
		return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/add_room', methods=['POST'])
def api_add_room():
	name = request.values.get("name")
	location = request.values.get("location")
	traffic = request.values.get("traffic")
	extend = request.values.get("extend")

	try:
		room = Room.query.filter(Room.name==name).first()
		if room:
			return jsonify({'error':403, 'cause': '您添加的教室已存在'})
		else:
			r = Room(name=name, location=location, traffic=traffic, extend=extend)
			db.session.add(r)
			db.session.commit()
			return jsonify({'error':0, 'rid': r.rid})
	except Exception , e:
		# app.logger.error(e)
		return jsonify({'error':4, 'cause': '数据库操作失败'})
