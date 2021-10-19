# ASI Django Applications

This repository includes all Django applications for ASI.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisities

1. LAMP/WAMP environment
2. Python 3.6
3. Django 1.11.*

### Installing

* Download and install Python > 3.6

* Install project dependencies
```python
# Recommended way that will install: Django djangorestframework djangorestframework-jwt django-debug-toolbar Pillow django-guardian qrcode
# Navigate to root and run
pip install -r requirements.txt

# Alternative - use line below to install latest version of dependencies. They will not be compatible with each other, so specify their versions from the requirements file if you really need to do this, 
pip install djangorestframework djangorestframework-jwt django-debug-toolbar Pillow django-guardian qrcode
```

* Install MySQL DB API Driver for Django
```python
# For linux
pip install mysqlclient 

# For Windows, 
# Download mysqlclient from http://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient and install a compatible version
# Example - below is for Python version 3.6 64 bit (32/64 are for Python version, not for Windows version):
pip install path\to\folder\mysqlclient‑1.3.13‑cp36‑cp36m‑win_amd64.whl # If using Windows x64 & Python 3.6
```

* Configure MySQL for timezone support (https://dev.mysql.com/doc/refman/5.7/en/mysql-tzinfo-to-sql.html) from the mysql shell
```mysql
shell> mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql # (Linux only)

# For Windows, download and extract timezone data from http://dev.mysql.com/downloads/timezones.html
# Download the version that contains the SQL file (e.g. timezone_2018e_posix_sql.zip)
# Run following command from the MySQL shell (e.g. If using XAMPP, open Control Panel, click on 'Shell' button and enter following command)
shell> mysql -u root;
mysql> use mysql;
mysql> source file_name.sql; # (specify absolute path to file_name - e.g. C:/some_folder/timezone_posix.sql)
```
* Clone *asi-django-apps* repository
```
git clone https://{username}@bitbucket.org/edaceituno/asi-django-apps.git
```
* Configure your asicsulb/settings.py file	
	1. Copy settings_sample.py file and name it settings.py
	2. Set SECRET_KEY (e.g., generate any random string)
	3. Configure DATABASE (e.g., using phpMyAdmin)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '{DB_NAME}',
        'USER': '{DB_USER}',
        'PASSWORD': '{DB_PASSWORD}',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
	4. Configure other settings as needed (e.g. STATIC_ROOT, MEDIA_ROOT, etc.) and ensure database specified above exists with 'utf8_general_ci' collation before running next command.
* Run migrations
```python
python manage.py migrate
```
* Create cache tables
```python
# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'api_wellness_cache', # Table name
    }
}
# Run command
python manage.py createcachetable
```
* Import initial data into database
```python
python manage.py loaddata {fixturename} # See {app}/fixtures folder for available file names
```
* Run development server
```python
python manage.py runserver
```
* Access site
```python
http://127.0.0.1:8000/{APP} # See asicsulb/urls.py for available routes
```
* Access admin site
```python
http://127.0.0.1:8000/admin

# If you need an account, run the following command and follow the prompts to create a superuser.
python manage.py createsuperuser
```

## Running tests

Coming soon.

## Deployment

Coming soon.