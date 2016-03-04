#coding: utf-8
import os
import sys
sys.path.append(os.path.dirname(__name__))

from portal import app

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=80, debug=True, threaded=True)
