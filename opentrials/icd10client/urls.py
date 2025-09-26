from django.urls import re_path

from icd10client.views import *

urlpatterns = [
    re_path(r'^get_chapters/$', get_chapters, name='icd10.get_chapters'),
    re_path(r'^search/(?P<lang>[a-z]{2,2})(-[a-z][a-z])?/(?P<prefix>\w+)/(?P<term>.*)$', search),
    re_path(r'^search/(?P<lang>[a-z]{2,2})(-[a-z][a-z])?/(?P<term>.*)$', search, name='icd10.search'),
    re_path(r'^test_search/$', test_search),
]
