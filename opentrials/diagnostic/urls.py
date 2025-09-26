from django.urls import path, re_path

from diagnostic.views import *

urlpatterns = [
    # Diagnostic views
    path('smoke/', smoke_test),
    path('reqdump/', req_dump),
    path('sysinfo/', sys_info),
    path('error/', raise_error),
    path('dumpdb/', export_database),
    path('backupdb/', backup_database, name='backup_database'),
    re_path(r'^dumpdata/(?P<appname>[a-z_]+)?/?$', dump_data, name='dumpdata'),
]
