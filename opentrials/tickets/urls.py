from django.urls import path
from django.views.generic.list_detail import object_detail, object_list
from tickets.models import Ticket, Followup
from tickets.views import index, new_iteration, reopen_ticket, resolve_ticket, close_ticket, open_ticket, waiting_acceptance, accept_ticket


info_dict = {
    'queryset': Ticket.objects.all(),
}

urlpatterns = [
    path('', index, name="ticket.index"),
    path('list/', object_list, info_dict, name="ticket.list"),
    path('list_waiting/', waiting_acceptance, name="ticket.waiting_acceptance"),
    path('history/<int:object_id>/', object_detail, info_dict, name='ticket.history'),
    path('open/<str:context>/<str:type>/', open_ticket, name='ticket.open'),
    path('reopen/<int:object_id>/', reopen_ticket, name='ticket.reopen'),
    path('resolve/<int:object_id>/', resolve_ticket, name='ticket.resolve'),
    path('accept/<int:object_id>/', accept_ticket, name='ticket.accept'),
    path('close/<int:object_id>/', close_ticket, name='ticket.close'),
    path('newiteration/<int:object_id>/', new_iteration, name='ticket.new_iteration'),
]
