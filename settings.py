import dj_database_url


SECRET_KEY = 'django-args'
# Install the tests as an app so that we can make test models
INSTALLED_APPS = [
    'djarg',
    'djarg.tests',
]
# Database url comes from the DATABASE_URL env var
DATABASES = {'default': dj_database_url.config()}
