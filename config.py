import os
basedir = os.path.abspath(os.path.dirname(__file__))

# basic settings
CSRF_ENABLED = True
SECRET_KEY = 'izyou-secert-dev-key'
RECAPTCHA_PUBLIC_KEY = '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'

# sqlalchemy
# connect string for local postgresql server
#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://root@localhost/izyou'
# connect string for rds mysql server
SQLALCHEMY_DATABASE_URI = 'mysql://izyou:ZYJizyou@rdsvdk0918cl7z915n71.mysql.rds.aliyuncs.com/izyou'
# connect string for local mysql server
#SQLALCHEMY_DATABASE_URI = 'mysql://root@localhost/izyou'

#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
#WHOOSH_BASE = os.path.join(basedir, 'search.db')

# mail server
MAIL_SERVER = 'smtp.mxhichina.com'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = 'contact@zhiyijia.cn'
MAIL_PASSWORD = 'ZhiYJ262510~~'

# sms rest api
LC_APP_ID = '4ipytcknqxezwia4z6wj3e38h477ngevocrfc18apy1hmc5e'
LC_APP_KEY = 'yjflu1m3vzklyxrqkmrb8w61myq834i42bo5anj5u3ynler5'
LC_APP_MASTER_KEY = 'sty2l8s0b8hkcuh65wmnmbc05bqxtim0ljzvba8ltee9j4n6'
LC_REQUEST_SMS_CODE_API = 'https://api.leancloud.cn/1.1/requestSmsCode'
LC_VERIFY_SMS_CODE_API = 'https://api.leancloud.cn/1.1/verifySmsCode'

# administrator
ADMINS = ['tangshihu@zhiyijia.cn']

# pagination
PAGE_ITEMS = 10

# debug switch
IS_DEBUG=True
