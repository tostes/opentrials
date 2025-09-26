from django.urls import path

from assistance.views import faq
from assistance.models import Question

urlpatterns = [
    path('faq/', faq, name="assistance.faq"),
]
