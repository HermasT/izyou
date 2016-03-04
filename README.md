izyou project
===============

###dependcies

$ pip install -r requires.txt

$ pip intall flask-login==0.2.11

###create database izyou via psql client

###install python connector for mysql (/etc/my.cnf)
$ pip install mysql-python

###create tables and initial data for database izyou
$ python db_setup.py

-----

## debug deploy
$ python main.py

#### release deploy, with nginx + uwsgi
$ sudo vi nginx/conf
    
    server {
        listen       8000;
        
	location / {
            include uwsgi_params;
            uwsgi_pass  127.0.0.1:5000;
        }
   }

##### nohup uwsgi --socket 127.0.0.1:5000 --wsgi-file main.py --callable app --processes 4 -H mentalgames &

