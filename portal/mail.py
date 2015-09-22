from flask.ext.mail import Mail
from flask.ext.mail import Message
from threading import Thread
from portal import app, mail

class MailUtil(Thread):
    def __init__(self, message):
    	Thread.__init__(self)
    	self._message = message
  
    def run(self):
    	with app.app_context():
	    	mail.send(self._message)
	    	print 'mail sent'

    @staticmethod
    def buildMessage(subject, sender, recipients, body):
		message = Message(subject=subject, sender=sender, recipients=recipients, body=body)
		return message
