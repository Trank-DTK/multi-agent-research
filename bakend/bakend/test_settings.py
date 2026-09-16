"""Isolated regression tests: SQLite in memory, no real accounts or model calls."""
SECRET_KEY = 'isolated-tests-not-for-deployment'
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'accounts', 'documents', 'chat', 'writing']
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_TZ = True
ROOT_URLCONF = 'bakend.test_urls'
REST_FRAMEWORK = {'DEFAULT_AUTHENTICATION_CLASSES': []}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
