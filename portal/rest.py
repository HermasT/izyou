# coding: utf-8
import sys, time, math, json, requests, config, pingpp
from urllib import urlencode, quote
from flask import Flask, flash, redirect, url_for, request, jsonify, send_file
from sqlalchemy import desc, asc, or_, not_
from flask_bootstrap import Bootstrap, StaticCDN
from flask_appconfig import AppConfig
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from portal import app, db, lm, mail
from models import Users, Teacher, Room, UserType, GenderType, GameType, PayType, ProductType, Orders, OrderItem, OrderStatus
from models import Course, CourseStatus, CourseDetail, CourseSchedule, CourseStudent
from mail import MailUtil
from sms import SmsUtil

# 用户账号
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

# 师资管理
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

			userToUpdate = Users.query.filter(Users.username == teacher.username).first()
			if not userToUpdate:
				return jsonify({'error':403, 'cause': '您添加的教师用户名尚未注册，请先注册用户'})			

			userToUpdate.name = request.args.get("name")
			userToUpdate.birth = request.args.get("birth")
			userToUpdate.gender = request.args.get("gender")
			userToUpdate.gtype = request.args.get("gtype")
			teauserToUpdatecher.desc = request.args.get("desc")
			userToUpdate.extend = request.args.get("extend")

			uprice = request.args.get("uprice")
			if uprice is None or uprice == "":
				teacher.uprice = 0.0
			else:
				teacher.uprice = uprice

			db.session.add(userToUpdate)
			db.session.add(teacher)
			db.session.commit()
			return jsonify({'error':0})
	except:
		return jsonify({'error':4, 'cause': '数据库操作失败'})

# 课程管理
@app.route('/rest/create_course', methods=['POST'])
def api_create_course():
	summary = json.loads(request.values.get('summary'))
	try:
		c = Course(name=summary['name'], gtype=summary['gtype'], time=summary['time'], count=summary['count'], step=1,
			period=summary['period'], charge=summary['charge'], max_student=summary['max'], min_student=summary['min'],
			audition=summary['audition'], target=summary['target'], desc=summary['desc'], extend=summary['extend'])
		db.session.add(c)
		db.session.commit()
		return jsonify({'error':0, 'cid': c.cid})
	except Exception, e:
		print e
		return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/add_course_detail', methods=['POST'])
def api_add_course_detail():
	cid = request.values.get('cid')
	contents = json.loads(request.values.get('contents'))

	# 将课程的step设置为2
	course = Course.query.filter(Course.cid==cid).first()
	if not course:
		abort(404)
	else:
		course.step = 2
		db.session.add(course)

	for c in contents:
		course_content = CourseDetail(cid=cid, index=c['index'], title=c['title'], detail=c['detail'], extend='')
		db.session.add(course_content)

	try:
		db.session.commit()
		return jsonify({'error':0})
	except Exception, e:
		db.session.rollback()
		return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/add_course_schedule', methods=['POST'])
def api_add_course_schedule():
	cid = request.values.get('cid')
	schedules = json.loads(request.values.get('schedules'))

	# 将课程的step设置为3
	course = Course.query.filter(Course.cid==cid).first()
	if not course:
		abort(404)
	else:
		course.step = 3
		db.session.add(course)

	for s in schedules:
		course_schedule = CourseSchedule(cid=cid, rid=s['rid'], index=s['index'], 
			time=s['time'], mteacher=s['mteacher'], bteacher=s['bteacher'], extend='')
		db.session.add(course_schedule)
	try:
		db.session.commit()
		return jsonify({'error':0})
	except Exception, e:
		print e
		db.session.rollback()
		return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/update_course', methods=['GET', 'POST'])
def api_update_course():
	cid = request.values.get('cid')
	course = Course.query.filter(Course.cid==cid).first()
	if course is None:
		return jsonify({'error':1, 'cause': '查找不到与之匹配的课程信息'})
	else:
		summary = json.loads(request.values.get('summary'))
		course.name = name=summary['name']
		course.gtype=summary['gtype']
		course.time=summary['time']
		course.count=summary['count']
		course.period=summary['period']
		course.charge=summary['charge']
		course.max_student=summary['max']
		course.min_student=summary['min']
		course.audition=summary['audition']
		course.target=summary['target']
		course.desc=summary['desc']
		course.extend=summary['extend']
		db.session.add(course)
		try:
			db.session.commit()
			return jsonify({'error':0})
		except Exception, e:
			print e
			db.session.rollback()
			return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/register_course', methods=['POST'])
def api_register_course():
	try:
		cid = request.values.get('cid')
		csid = request.values.get('csid')
		username = request.values.get("username")
		paytype = request.values.get("paytype")

		courseSchedule = CourseSchedule.query.filter(CourseSchedule.csid == csid).first()
		if courseSchedule is None:
			return jsonify({'error':5, 'cause': u'查找不到与之匹配的课程班次信息'})

		course = Course.query.filter(Course.cid==courseSchedule.cid).first()
		if course is None:
			return jsonify({'error':5, 'cause': u'查找不到与之匹配的课程信息'})

		user = Users.query.filter(Users.username==username).first()
		if user is None:
			return jsonify({'error':5, 'cause': u'查找不到报名的用户，请先注册用户'})

		courseStudent = CourseStudent.query.filter(CourseStudent.cid==course.cid, 
			CourseStudent.uid==current_user.uid, CourseStudent.csid==csid).first()
		if courseStudent:
			return jsonify({'error':5, 'cause': u'您已报名了本班次的课程，不需要重新报名'})

		studentCount =  CourseStudent.query.filter(CourseStudent.cid==course.cid).count()
		if studentCount == course.max_student:
			return jsonify({'error':5, 'cause': u'本班次课程已报满，请选择其他班次'})
		else:
			operator = current_user.username
			if paytype == 0 or paytype == str(0):
				charged = False
			else:
				charged = True

			# 生成订单
			order = Orders(username = username, op=operator, cid = course.cid, csid=courseSchedule.csid, charged=charged, amount = course.charge, paytype=paytype, status=OrderStatus.order, extend='')
			db.session.add(order)
			db.session.commit()

			item = OrderItem(orderid=order.orderid, ptype=ProductType.course, pid=course.cid, subid=courseSchedule.csid, op=operator, count=1, status=0)
			db.session.add(item)

			# 统计班次的报名学生和人数
			courseStudent = CourseStudent(cid = courseSchedule.cid, uid = user.uid, csid = courseSchedule.csid)
			db.session.add(courseStudent)

			try:
				db.session.commit()
				return jsonify({'error':0, 'rid': order.orderid})
			except Exception, e:
				print e
				db.session.rollback()
				return jsonify({'error':6, 'cause': '数据库操作失败'})
	except Exception , e:
		print e
		return jsonify({'error':4, 'cause': '请求处理失败'})

# 教室管理
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

@app.route('/rest/update_room', methods=['POST'])
def api_update_room():
	rid = request.values.get("rid", -1);
	name = request.values.get("name")
	location = request.values.get("location")
	traffic = request.values.get("traffic")
	extend = request.values.get("extend")

	try:
		room = Room.query.filter(Room.rid==rid).first()
		if room is None:
			return jsonify({'error':403, 'cause': '您更新的教室不存在'})
		else:
			room.traffic = traffic
			room.name = name
			room.extend = extend
			room.location = location

			db.session.add(room)
			db.session.commit()
			return jsonify({'error':0, 'rid': room.rid})
	except Exception , e:
		return jsonify({'error':4, 'cause': '数据库操作失败'})		

# 用户更新自己的信息
@app.route('/rest/update_userprofile', methods=['POST'])
def  api_update_userprofile():
	name = request.values.get("name")
	birth = request.values.get("birth")
	phone = request.values.get("phone")
	email = request.values.get("email")
	gender = request.values.get("gender")
	desc = request.values.get("desc")
	extend = request.values.get("extend")

	userToUpdate = Users.query.filter(Users.uid == current_user.uid).first()
	if not userToUpdate:
		return jsonify({'error':403, 'cause': '用户名不存在'})

	userToUpdate.name = name;
	userToUpdate.birth = birth;
	userToUpdate.phone = phone;
	userToUpdate.gender = gender;
	userToUpdate.email = email;
	userToUpdate.desc = desc
	userToUpdate.extend = extend

	db.session.add(userToUpdate)
	try:
		db.session.commit()
		return jsonify({'error':0})
	except Exception , e:
		# app.logger.error(e)
		db.session.rollback()
		return jsonify({'error':4, 'cause': '数据库操作失败'})

# 修改用户密码
@app.route('/rest/update_password', methods=['POST'])
def  api_update_password():
	oldPassword = request.values.get('oldPassword')
	newPassword = request.values.get('newPassword')

	saltOldPassword = Users.get_crypto_password(oldPassword, current_user.salt)
	saltNewPassword = Users.get_crypto_password(newPassword, current_user.salt)
	if saltOldPassword == saltNewPassword:
		return jsonify({'error':404, 'cause': '新密码不能与原密码相同'})
	
	try:
		user = Users.query.filter(Users.password == saltOldPassword).first()
		if not user:
			return jsonify({'error':404, 'cause': '原密码输入错误'})
		current_user.reset_password(newPassword);
		return jsonify({'error':0})
	except Exception, e:
		db.session.rollback()
		return jsonify({'error':4, 'cause': '数据库操作失败'})

@app.route('/rest/update_order', methods=['GET', 'POST'])
def api_update_order():
	orderid = request.values.get('orderid')
	order = Orders.query.filter(Orders.orderid == orderid).first()
	
	if order is None:
		return jsonify({'error':1, 'cause': '查找不到与之匹配的订单信息'})
	else:
		summary = json.loads(request.values.get('summary'))

		order.amount = summary['amount']
		order.income = summary['income']
		order.status = summary['status']
		order.paytype = summary['paytype']
		order.extend = summary['extend']
		
		db.session.add(order)
		try:
			db.session.commit()
			return jsonify({'error':0})
		except Exception, e:
			print e
			db.session.rollback()
			return jsonify({'error':4, 'cause': '数据库操作失败'})


# 支付测试
@app.route('/rest/test_pay', methods=['GET', 'POST'])
def api_test_pay():
	print '111'

	appID = {'id':'app_i9CG80HifzvTPyvn'}
	alipayPCDirectConfig = { 'success_url':'https://www.ctrip.com' }

	pingpp.api_key = 'sk_test_TebTaP8yDCyPXj54eP8qvvjT'
	ch = pingpp.Charge.create(
		order_no='1234567890',
		amount=100,
		app=appID,
		channel='alipay_pc_direct',
		currency='cny',
		client_ip='127.0.0.1',
		subject='Your Subject',
		body='Your Body',
		extra=alipayPCDirectConfig
	)
	print 'pingpp.Charge.create', ch	

	return jsonify(ch)

# 订单支付
@app.route('/rest/order_pay', methods=['GET', 'POST'])
def api_order_pay():

	orderid = request.values.get('orderid', -1)

	if orderid <= 0:
		return jsonify({'error':1, 'cause': '订单号不存在'})

	order = Orders.query.filter(Orders.orderid == orderid).first()
	if order is None:
		return jsonify({'error':1, 'cause': '查找不到与之匹配的订单信息'})

	if cmp(order.username, current_user.username) != 0:
		return jsonify({'error':1, 'cause': '只能为自己支付订单'})

	orderCourse = Course.query.filter(Course.cid == order.cid).first()
	courseSchedule = CourseSchedule.query.filter(CourseSchedule.csid == order.csid).first()

	appID = {'id':'app_5448OKvT00GOnb54'}
	alipayPCDirectConfig = { 'success_url':'http://zhiyijia.cn' }

	pingpp.api_key = 'sk_live_LqvfPG4mHCa9bbrP08yvjXLO'
	ch = pingpp.Charge.create(
		order_no= orderid,
		amount= order.income * 100,   #单位是分！
		app=appID,
		channel='alipay_wap',
		currency='cny',
		client_ip='127.0.0.1',        # 待定
		subject=orderCourse.name,   
		body=courseSchedule.time,
		extra=alipayPCDirectConfig
	)

	return jsonify(ch)
