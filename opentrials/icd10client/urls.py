from django.urls import path, re_path

from icd10client.views import *

urlpatterns = [
    path('get_chapters/', get_chapters, name='icd10.get_chapters'),
    re_path(r'^search/(?P<lang>[a-z]{2,2})(-[a-z][a-z])?/(?P<prefix>\w+)/(?P<term>.*)$', search),
    re_path(r'^search/(?P<lang>[a-z]{2,2})(-[a-z][a-z])?/(?P<term>.*)$', search, name='icd10.search'),
    path('test_search/', test_search),
]
