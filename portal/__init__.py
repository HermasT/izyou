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
# from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

# 应用实例
app = Flask(__name__)
Bootstrap(app)

# 数据库实例
db = SQLAlchemy(app)

# 用户管理
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = u'您需要登录才能访问该页面'
lm.login_message_category = "info"
lm.session_protection = "strong"

# 邮箱实力
mail = Mail(app)

# 应用配置管理
# app.config.from_object('config')
app.config['SECRET_KEY'] = 'devkey'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://hema:123456@localhost/izyou'
app.extensions['bootstrap']['cdns'] = {'jquery': StaticCDN(), 'html5shiv': StaticCDN(),
                                       'respond.js': StaticCDN(),
                                       'bootstrap': StaticCDN(), 'static': StaticCDN(), 'local': StaticCDN()}

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
#     import logging
#     from logging.handlers import RotatingFileHandler
#     file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
#     file_handler.setLevel(logging.INFO)
#     file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
#     app.logger.addHandler(file_handler)
#     app.logger.setLevel(logging.INFO)
#     app.logger.info('microblog startup')

from portal import views, models

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=8000, debug=True)