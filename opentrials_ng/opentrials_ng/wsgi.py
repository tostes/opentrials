"""WSGI config for opentrials_ng project."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "opentrials_ng.settings")

application = get_wsgi_application()
