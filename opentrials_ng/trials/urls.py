from django.urls import path

from opentrials_ng.trials.views import ClinicalTrialListView

app_name = "trials"

urlpatterns = [
    path("", ClinicalTrialListView.as_view(), name="trial-list"),
]
