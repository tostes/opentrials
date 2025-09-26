from django.urls import path, re_path
from django.contrib.auth.views import login, logout
from django.contrib.auth.views import password_reset, password_reset_done
from django.contrib.auth.views import password_reset_complete, password_reset_confirm
from django.views.generic.list_detail import object_list, object_detail

from reviewapp.views import index, user_dump, new_submission, submissions_list
from reviewapp.views import reviewlist, submission_edit_published
from reviewapp.views import dashboard, submission_detail, user_profile
from reviewapp.views import upload_trial, open_remark, resend_activation_email
from reviewapp.views import change_remark_status, delete_remark, allsubmissionslist
from reviewapp.views import contact, submission_delete, change_submission_status
from reviewapp.views import news_list, news_detail, terms_of_use

from reviewapp.models import Submission

from repository.feed import LastTrials, LastRecruiting

submissions = {
   'queryset':Submission.objects.all()
}

urlpatterns = [

    path('news/', news_list, name='reviewapp.newslist'),

    path('news/<int:object_id>/', news_detail, name='reviewapp.news'),

    path('accounts/dashboard/', dashboard, name='reviewapp.dashboard'),

    path('accounts/profile/', user_profile, name='reviewapp.userhome'),

    path('accounts/uploadtrial/', upload_trial, name='reviewapp.uploadtrial'), #same as accounts/profile

    path('accounts/submissionlist/', submissions_list, name='reviewapp.submissionlist'), #same as accounts/profile
    path('accounts/reviewlist/', reviewlist, name='reviewapp.reviewlist'),

    path('accounts/allsubmissionslist/', allsubmissionslist, name='reviewapp.allsubmissionslist'), #same as accounts/profile

    path('accounts/submission/<int:pk>/', submission_detail,
        name='reviewapp.submission'),

    path('accounts/submission/delete/<int:id>/', submission_delete,
        name='reviewapp.submission_delete'),

    path('accounts/submission/change/<int:submission_pk>/<slug:status>/', change_submission_status,
        name='reviewapp.change_submission_status'),

    path('accounts/newsubmission/', new_submission,
        name='reviewapp.new_submission'),

    path('accounts/termsofuse/', terms_of_use,
        name='reviewapp.terms_of_use'),

    path('accounts/submission/edit-published/<int:pk>/', submission_edit_published,
        name='reviewapp.submission_edit_published'),

    path('accounts/userdump/', user_dump),

    path('accounts/login/', login, dict(template_name='reviewapp/login.html',redirect_field_name='/'),
        name='reviewapp.login'),

    path('accounts/logout/', logout, dict(next_page='/'),
        name='reviewapp.logout'),

    path('accounts/resend/activation/email/', resend_activation_email,
        name='reviewapp.resend_activation_email'),

    path('accounts/password/reset/', password_reset, {
        'template_name': 'reviewapp/password_reset_form.html',
        'email_template_name': 'reviewapp/password_reset_email.html',
        'post_reset_redirect': '/accounts/password/reset/done/'},
        name='reviewapp.password_reset'),

    path('accounts/password/reset/done/', password_reset_done,
        {'template_name': 'reviewapp/password_reset_done.html'},
        name='reviewapp.password_reset_done'),

    re_path(r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm, {
        'template_name': 'reviewapp/password_reset_confirm.html',
        'post_reset_redirect': '/accounts/password/reset/complete/'},
        name='reviewapp.password_reset_confirm'),

    path('accounts/password/reset/complete/', password_reset_complete,
        {'template_name': 'reviewapp/password_reset_complete.html'},
        name='reviewapp.password_reset_complete'),

    re_path(r'^remark/open/(?P<submission_id>\d+)/(?P<context>[a-zA-Z0-9_\- ]+)/$', open_remark,
        name='reviewapp.openremark'),

    path('contact/', contact, name='reviewapp.contact'),

    path('remark/change/<int:remark_id>/<slug:status>/', change_remark_status,
        name='reviewapp.changeremarkstatus'),

    path('remark/delete/<int:remark_id>/', delete_remark,
        name='reviewapp.delete_remark'),

    re_path(r'^rss/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
        {'feed_dict': {'trials': LastTrials, 'recruiting': LastRecruiting}}),

    path('', index, name='reviewapp.home'),
]
