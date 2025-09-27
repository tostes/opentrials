"""Admin registrations for the clinical trial domain."""
from django.contrib import admin

from opentrials_ng.trials import models


@admin.register(models.ClinicalTrial)
class ClinicalTrialAdmin(admin.ModelAdmin):
    list_display = ("display_identifier", "main_title", "record_status", "registration_date")
    search_fields = ("trial_id", "scientific_title", "public_title", "utrn_number")
    list_filter = ("record_status", "recruitment_status")
    filter_horizontal = ("intervention_codes", "recruitment_countries")
    autocomplete_fields = ("primary_sponsor", "purpose", "study_type", "phase")


@admin.register(models.Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country")
    search_fields = ("name", "city")
    list_filter = ("institution_type", "country")


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "affiliation")
    search_fields = ("given_name", "family_name", "email")
    list_filter = ("country",)


@admin.register(models.TrialIdentifier)
class TrialIdentifierAdmin(admin.ModelAdmin):
    list_display = ("trial", "issuing_authority", "identifier")
    search_fields = ("identifier", "trial__trial_id")
    autocomplete_fields = ("trial", "issuing_authority")


@admin.register(models.TrialSupportSource)
class TrialSupportSourceAdmin(admin.ModelAdmin):
    list_display = ("trial", "institution")
    autocomplete_fields = ("trial", "institution")


@admin.register(models.TrialSecondarySponsor)
class TrialSecondarySponsorAdmin(admin.ModelAdmin):
    list_display = ("trial", "institution")
    autocomplete_fields = ("trial", "institution")


@admin.register(models.Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ("trial", "interest", "description")
    list_filter = ("interest",)
    search_fields = ("description",)


@admin.register(models.TrialDescriptor)
class TrialDescriptorAdmin(admin.ModelAdmin):
    list_display = ("trial", "aspect", "level", "description")
    list_filter = ("aspect", "level", "vocabulary")
    search_fields = ("description", "code")
