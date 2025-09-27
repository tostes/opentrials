"""Read-only views for browsing clinical trial metadata."""
from django.views.generic import ListView

from opentrials_ng.trials.models import ClinicalTrial


class ClinicalTrialListView(ListView):
    model = ClinicalTrial
    paginate_by = 25
    template_name = "trials/trial_list.html"
    context_object_name = "trials"
    queryset = ClinicalTrial.objects.active().select_related(
        "primary_sponsor",
        "recruitment_status",
        "study_type",
    ).prefetch_related("recruitment_countries")

    def get_queryset(self):  # type: ignore[override]
        queryset = super().get_queryset()
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(record_status=status)
        return queryset
