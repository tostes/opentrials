"""Admin registration for controlled vocabulary models."""
from django.contrib import admin

from opentrials_ng.vocabulary import models


class DefaultVocabularyAdmin(admin.ModelAdmin):
    list_display = ("label", "description", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("label", "description")


for model in (
    models.Country,
    models.TrialNumberAuthority,
    models.StudyType,
    models.InterventionCode,
    models.StudyPurpose,
    models.InterventionAssignment,
    models.StudyMasking,
    models.StudyAllocation,
    models.StudyPhase,
    models.RecruitmentStatus,
    models.TimePerspective,
    models.ObservationalStudyDesign,
    models.InstitutionType,
):
    admin.site.register(model, DefaultVocabularyAdmin)
