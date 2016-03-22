# coding: utf-8
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask
from flask_bootstrap import Bootstrap, StaticCDN
from flask_appconfig import AppConfig
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.mail import Mail

from config import SECRET_KEY, RECAPTCHA_PUBLIC_KEY, SQLALCHEMY_DATABASE_URI
from config import MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USE_SSL, MAIL_USERNAME, MAIL_PASSWORD

# 应用实例
app = Flask(__name__)

# 初始化bootstrap                                       
Bootstrap(app)

# 应用配置管理
# app.config.from_object('config')
app.config['SECRET_KEY'] = SECRET_KEY
app.config['RECAPTCHA_PUBLIC_KEY'] = RECAPTCHA_PUBLIC_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.extensions['bootstrap']['cdns'] = {'jquery': StaticCDN(), 'html5shiv': StaticCDN(),
                                       'respond.js': StaticCDN(),
                                       'bootstrap': StaticCDN(), 'static': StaticCDN(), 'local': StaticCDN()}
app.config['MAIL_SERVER']=MAIL_SERVER
app.config['MAIL_PORT']=MAIL_PORT
app.config['MAIL_USE_TLS']=MAIL_USE_TLS
app.config['MAIL_USE_SSL']=MAIL_USE_SSL
app.config['MAIL_USERNAME']=MAIL_USERNAME
app.config['MAIL_PASSWORD']=MAIL_PASSWORD

# 数据库实例
db = SQLAlchemy(app)

# 用户管理
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = u'您需要登录才能访问该页面'
lm.login_message_category = "info"
lm.session_protection = "strong"

# 邮箱实例
mail = Mail(app)

# if not app.debug:
#     import logging
#     from logging.handlers import SMTPHandler
#     credentials = None
#     if MAIL_USERNAME or MAIL_PASSWORD:
#         credentials = (MAIL_USERNAME, MAIL_PASSWORD)
#     mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
#     mail_handler.setLevel(logging.ERROR)
#     app.logger.addHandler(mail_handler)

# if app.debug:
import logging
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler('log/izyou.log', 'a', 1 * 1024 * 1024, 10)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.warning('izyou startup')

from portal import views, models, admin, rest

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=8000, debug=True)