"""Modernised Django models for the OpenTrials registry domain."""
from __future__ import annotations

from datetime import date

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from opentrials_ng.trials import choices
from opentrials_ng.vocabulary.models import (
    Country,
    InstitutionType,
    InterventionAssignment,
    InterventionCode,
    ObservationalStudyDesign,
    RecruitmentStatus,
    StudyAllocation,
    StudyMasking,
    StudyPhase,
    StudyPurpose,
    StudyType,
    TimePerspective,
    TrialNumberAuthority,
)


class TimeStampedModel(models.Model):
    """Reusable timestamp mixin."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TrialRegistrationDataSetModel(TimeStampedModel):
    """Base class mirroring the legacy TRDS data set mixin."""

    class Meta:
        abstract = True


class ClinicalTrialQuerySet(models.QuerySet):
    """Custom query helpers used by the registry."""

    def published(self) -> "ClinicalTrialQuerySet":
        return self.filter(record_status="published")

    def active(self) -> "ClinicalTrialQuerySet":
        return self.exclude(record_status="archived")


class ClinicalTrialManager(models.Manager):
    def get_queryset(self) -> ClinicalTrialQuerySet:  # type: ignore[override]
        return ClinicalTrialQuerySet(self.model, using=self._db)

    def published(self) -> ClinicalTrialQuerySet:
        return self.get_queryset().published()

    def active(self) -> ClinicalTrialQuerySet:
        return self.get_queryset().active()


class ClinicalTrial(TrialRegistrationDataSetModel):
    """Representation of a WHO Trial Registration Data Set record."""

    record_status = models.CharField(
        max_length=32, choices=choices.TRIAL_RECORD_STATUS, default="draft"
    )
    trial_id = models.CharField(max_length=64, unique=True, blank=True)
    registration_date = models.DateField(null=True, blank=True)
    utrn_number = models.CharField(max_length=255, blank=True)

    scientific_title = models.TextField()
    scientific_acronym = models.CharField(max_length=255, blank=True)
    scientific_acronym_expansion = models.CharField(max_length=255, blank=True)

    public_title = models.TextField(blank=True)
    acronym = models.CharField(max_length=255, blank=True)
    acronym_expansion = models.CharField(max_length=255, blank=True)

    primary_sponsor = models.ForeignKey(
        "Institution",
        related_name="primary_trials",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    support_sources = models.ManyToManyField(
        "Institution",
        through="TrialSupportSource",
        related_name="supported_trials",
        blank=True,
    )
    secondary_sponsors = models.ManyToManyField(
        "Institution",
        through="TrialSecondarySponsor",
        related_name="secondary_trials",
        blank=True,
    )

    public_contacts = models.ManyToManyField(
        "Contact",
        through="PublicContact",
        related_name="public_trials",
        blank=True,
    )
    scientific_contacts = models.ManyToManyField(
        "Contact",
        through="ScientificContact",
        related_name="scientific_trials",
        blank=True,
    )
    site_contacts = models.ManyToManyField(
        "Contact",
        through="SiteContact",
        related_name="site_trials",
        blank=True,
    )

    hc_freetext = models.TextField(blank=True)
    i_freetext = models.TextField(blank=True)

    inclusion_criteria = models.TextField(blank=True)
    exclusion_criteria = models.TextField(blank=True)
    gender = models.CharField(
        max_length=16, choices=choices.INCLUSION_GENDER, default="any"
    )
    agemin_value = models.PositiveIntegerField(null=True, blank=True)
    agemin_unit = models.CharField(
        max_length=16, choices=choices.INCLUSION_AGE_UNIT, default="none"
    )
    agemax_value = models.PositiveIntegerField(null=True, blank=True)
    agemax_unit = models.CharField(
        max_length=16, choices=choices.INCLUSION_AGE_UNIT, default="none"
    )

    study_type = models.ForeignKey(StudyType, null=True, blank=True, on_delete=models.SET_NULL)
    study_design = models.TextField(blank=True)
    expanded_access_program = models.BooleanField(null=True, blank=True)
    purpose = models.ForeignKey(StudyPurpose, null=True, blank=True, on_delete=models.SET_NULL)
    intervention_assignment = models.ForeignKey(
        InterventionAssignment, null=True, blank=True, on_delete=models.SET_NULL
    )
    number_of_arms = models.PositiveIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1)]
    )
    masking = models.ForeignKey(StudyMasking, null=True, blank=True, on_delete=models.SET_NULL)
    allocation = models.ForeignKey(StudyAllocation, null=True, blank=True, on_delete=models.SET_NULL)
    phase = models.ForeignKey(StudyPhase, null=True, blank=True, on_delete=models.SET_NULL)
    time_perspective = models.ForeignKey(
        TimePerspective, null=True, blank=True, on_delete=models.SET_NULL
    )
    observational_study_design = models.ForeignKey(
        ObservationalStudyDesign, null=True, blank=True, on_delete=models.SET_NULL
    )

    enrollment_start_planned = models.DateField(null=True, blank=True)
    enrollment_start_actual = models.DateField(null=True, blank=True)
    enrollment_end_planned = models.DateField(null=True, blank=True)
    enrollment_end_actual = models.DateField(null=True, blank=True)

    target_sample_size = models.PositiveIntegerField(null=True, blank=True)
    recruitment_status = models.ForeignKey(
        RecruitmentStatus, null=True, blank=True, on_delete=models.SET_NULL
    )
    recruitment_countries = models.ManyToManyField(
        Country, related_name="recruitment_trials", blank=True
    )

    intervention_codes = models.ManyToManyField(
        InterventionCode, related_name="trials", blank=True
    )

    notes = models.TextField(blank=True)

    objects = ClinicalTrialManager()

    class Meta:
        ordering = ["-updated_at", "trial_id"]

    def __str__(self) -> str:  # pragma: no cover - simple display helper
        identifier = self.display_identifier()
        return f"{identifier} – {self.short_title()}" if identifier else self.short_title()

    def display_identifier(self) -> str:
        if self.trial_id:
            return self.trial_id
        if self.pk:
            return f"trial-{self.pk}"
        return ""

    def main_title(self) -> str:
        return self.public_title or self.scientific_title

    def short_title(self) -> str:
        title = self.main_title()
        return title if len(title) <= 120 else f"{title[:117]}…"

    def mark_published(self, identifier: str | None = None) -> None:
        """Transition the record to *published* status."""

        self.record_status = "published"
        if identifier:
            self.trial_id = identifier
        if not self.registration_date:
            self.registration_date = date.today()

    def is_published(self) -> bool:
        return self.record_status == "published"


class TrialIdentifier(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(
        ClinicalTrial, related_name="identifiers", on_delete=models.CASCADE
    )
    issuing_authority = models.ForeignKey(
        TrialNumberAuthority, on_delete=models.PROTECT
    )
    identifier = models.CharField(max_length=255)

    class Meta:
        unique_together = ("trial", "issuing_authority", "identifier")
        verbose_name = _("Secondary identifier")
        verbose_name_plural = _("Secondary identifiers")

    def __str__(self) -> str:  # pragma: no cover - trivial display
        return f"{self.issuing_authority}: {self.identifier}"


class Institution(TrialRegistrationDataSetModel):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=50, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    institution_type = models.ForeignKey(
        InstitutionType, null=True, blank=True, on_delete=models.SET_NULL
    )
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover - trivial display
        return self.name


class Contact(TrialRegistrationDataSetModel):
    given_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    family_name = models.CharField(max_length=50)
    email = models.EmailField()
    affiliation = models.ForeignKey(
        Institution, null=True, blank=True, on_delete=models.SET_NULL
    )
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    postal_code = models.CharField(max_length=50, blank=True)
    telephone = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["family_name", "given_name"]

    def __str__(self) -> str:  # pragma: no cover - trivial display
        return self.full_name

    @property
    def full_name(self) -> str:
        parts = [self.given_name, self.middle_name, self.family_name]
        return " ".join(part for part in parts if part).strip()


class BaseContactLink(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=32, choices=choices.CONTACT_STATUS, default="active"
    )

    class Meta:
        abstract = True
        unique_together = ("trial", "contact")

    def __str__(self) -> str:  # pragma: no cover - trivial display
        return f"{self.trial.short_title()} – {self.contact.full_name}"


class PublicContact(BaseContactLink):
    class Meta(BaseContactLink.Meta):
        verbose_name = _("Public contact")
        verbose_name_plural = _("Public contacts")


class ScientificContact(BaseContactLink):
    class Meta(BaseContactLink.Meta):
        verbose_name = _("Scientific contact")
        verbose_name_plural = _("Scientific contacts")


class SiteContact(BaseContactLink):
    class Meta(BaseContactLink.Meta):
        verbose_name = _("Site contact")
        verbose_name_plural = _("Site contacts")


class TrialSupportSource(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("trial", "institution")
        verbose_name = _("Source of support")
        verbose_name_plural = _("Sources of support")

    def __str__(self) -> str:  # pragma: no cover - trivial display
        return f"{self.trial.short_title()} – {self.institution.name}"


class TrialSecondarySponsor(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("trial", "institution")
        verbose_name = _("Secondary sponsor")
        verbose_name_plural = _("Secondary sponsors")

    def __str__(self) -> str:  # pragma: no cover - trivial display
        return f"{self.trial.short_title()} – {self.institution.name}"


class Outcome(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial, related_name="outcomes", on_delete=models.CASCADE)
    interest = models.CharField(
        max_length=16, choices=choices.OUTCOME_INTEREST, default="primary"
    )
    description = models.TextField()
    time_frame = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["trial", "pk"]

    def __str__(self) -> str:  # pragma: no cover - trivial display
        return f"{self.get_interest_display()}: {self.description[:50]}"


class TrialDescriptor(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(
        ClinicalTrial, related_name="descriptors", on_delete=models.CASCADE
    )
    aspect = models.CharField(max_length=32, choices=choices.TRIAL_ASPECT)
    level = models.CharField(max_length=32, choices=choices.DESCRIPTOR_LEVEL)
    vocabulary = models.CharField(
        max_length=32, choices=choices.DESCRIPTOR_VOCABULARY
    )
    code = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=500)

    class Meta:
        ordering = ["trial", "aspect", "level", "description"]

    def __str__(self) -> str:  # pragma: no cover - trivial display
        return f"{self.get_aspect_display()} – {self.description}"
