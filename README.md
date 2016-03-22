izyo pro
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

### release deploy, with nginx + uwsgi
$ sudo vi /etc/nginx/nginx.conf
### add server config, notice the address difference:    
    server {
        listen       80;
        server_name zhiyijia.cn www.zhiyijia.cn zhyjia.com www.zhyjia.com;
	location / {
            include uwsgi_params;
            uwsgi_pass  127.0.0.1:8080;
        }
   }
### uwsgi_pass needs to be same as the nohup uwsgi socket and the port in main.py

$ nohup uwsgi --socket 127.0.0.1:8080 --wsgi-file main.py --callable app --processes 1 -H mentalgames &
