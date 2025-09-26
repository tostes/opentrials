from django.urls import re_path

from views import *

urlpatterns = [
    re_path(r'^getterm/(?P<lang>[a-z]{2,2})(-[a-z][a-z])?/(?P<code>[A-Z](\d{2,2}(\.\d{3,3})*)?)?$', getterm, name='decs.getterm'),
    re_path(r'^getdescendants/(?P<code>[A-Z](\d{2,2}(\.\d{3,3})*)?)?$', getdescendants, name='decs.getdescendants'),
    re_path(r'^search/(?P<lang>[a-z]{2,2})(-[a-z][a-z])?/(?P<prefix>[14]0[1-7])/(?P<term>.*)$', search),
    re_path(r'^search/(?P<lang>[a-z]{2,2})(-[a-z][a-z])?/(?P<term>.*)$', search, name='decs.search'),
    re_path(r'^test_search/$', test_search),
]
