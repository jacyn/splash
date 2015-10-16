development install notes
=========================

VM requirements
------------

CentOS
  python27 python27-pip python27-virtualenv
  mysql mysql-devel mysql-server 
  zlib-devel libjpeg-turbo.x86_64 gcc libjpeg-turbo-devel.x86_64 freetype.x86_64 freetype-devel.x86_64
  lighttpd
  git

setup a host file
-----------------
  /etc/hosts something like:
    127.0.0.1 .......... www.splashsite.localhost.tld splashsite.localhost.tld static.splashsite.localhost.tld uploads.splashsite.localhost.tld


setting up python virtualenv and packages
-----------------------------------------

  virtualenv -p /usr/bin/python2.7 --no-site-packages venv
  source venv/bin/activate
  pip install -r requirements.pip
  

  /etc/init.d/mysqld start
  # new configurations for webapp-source, supervisor, lighttpd
  # new database;
  # grant database access to user

  (source etc/webapp.source && python git/epins-frontend/webapp/manage.py syncdb)
  (source etc/webapp.source && python git/epins-frontend/webapp/manage.py migrate --fake)
  (source etc/webapp.source && python git/epins-frontend/webapp/manage.py collectstatic --noinput)

  (source etc/webapp.source && python git/epins-frontend/webapp/manage.py loaddata) ## load fixtures

  supervisord -c etc/supervisord.conf
  supervisorctl -c etc/supervisord.conf

