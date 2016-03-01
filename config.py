import os
basedir = os.path.abspath(os.path.dirname(__file__))

# basic settings
CSRF_ENABLED = True
SECRET_KEY = 'izyou-secert-dev-key'
RECAPTCHA_PUBLIC_KEY = '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'

# sqlalchemy
#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://hema:123456@localhost/izyou'
SQLALCHEMY_DATABASE_URI = 'mysql://root:111111@localhost/izyou'

#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
#WHOOSH_BASE = os.path.join(basedir, 'search.db')

# mail server
MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 25
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'your-qq-account'
MAIL_PASSWORD = 'your-qq-password'

# administrator
#ADMINS = ['you@example.com']

# pagination
PAGE_ITEMS = 10

# debug switch
IS_DEBUG=True
