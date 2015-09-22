# coding: utf-8
import os, sys, hashlib, math
sys.path.append(os.path.dirname(__name__))

from flask import Flask
from flask import current_app
from flask.ext.mail import Mail
from flask.ext.mail import Message
from threading import Thread

app = Flask(__name__)
app.config.from_object(__name__)

# these configs must be set before creating mail instance
app.config['MAIL_SERVER']='smtp.qq.com'
app.config['MAIL_PORT']=25
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USE_SSL']=False
app.config['MAIL_USERNAME']='36838082@qq.com'
app.config['MAIL_PASSWORD']='xx'
mail = Mail(app)

def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)

@app.route("/mail")
def SendMail():
    msg = Message('test',sender='36838082@qq.com',recipients=['hermasTang@hotmail.com'])
    msg.body = "text body"
    msg.html = "<b>HTML</b>body"
    thr = Thread(target=send_async_email,args=[app,msg])
    thr.start()
    return "send mail done"

if __name__ == '__main__':
	app.run(port=7777)
