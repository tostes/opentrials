from django.urls import path

from . import views

app_name = "diagnostic"

urlpatterns = [
    path("smoke/", views.smoke_test, name="smoke_test"),
    path("reqdump/", views.req_dump, name="req_dump"),
    path("sysinfo/", views.sys_info, name="sys_info"),
    path("error/", views.raise_error, name="raise_error"),
    path("dumpdb/", views.export_database, name="dump_database"),
    path("backupdb/", views.backup_database, name="backup_database"),
    path("dumpdata/", views.dump_data, name="dumpdata"),
    path("dumpdata/<str:appname>/", views.dump_data, name="dumpdata_app"),
]
