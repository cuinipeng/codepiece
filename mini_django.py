#!/usr/bin/env python
import os
import sys
#
# python mini_django.py runserver
#
G_SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
#################### Part-I ####################
from django.conf import settings
settings.configure(
    DEBUG=True,
    SECRET_KEY=G_SECRET_KEY,
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSESS=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
)

#################### Part-II ####################
from django.conf.urls import url
from django.http import HttpResponse
from django.core.wsgi import get_wsgi_application

def index(request):
    return HttpResponse('HELLO WORLD FROM DJANGO')

urlpatterns = (
    url(r'^$', index, name='index'),
)

application = get_wsgi_application()

#################### Part-III ####################
if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
