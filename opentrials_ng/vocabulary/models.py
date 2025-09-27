"""Controlled vocabularies used across the modern OpenTrials stack."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Common timestamp fields shared by vocabulary models."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SimpleVocabulary(TimeStampedModel):
    """Reusable base for simple ordered vocabularies."""

    label = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["order", "label"]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.label

    def save(self, *args, **kwargs) -> None:
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.order == 0 and self.pk:
            self.order = self.pk * 10
            super().save(update_fields=["order"])


class Country(SimpleVocabulary):
    """Country codes used for recruitment and addresses."""

    iso_code = models.CharField(max_length=2, unique=True)

    class Meta(SimpleVocabulary.Meta):
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
        ordering = ["label"]


class TrialNumberAuthority(SimpleVocabulary):
    class Meta(SimpleVocabulary.Meta):
        verbose_name = _("Trial number issuing authority")
        verbose_name_plural = _("Trial number issuing authorities")


class StudyType(SimpleVocabulary):
    pass


class InterventionCode(SimpleVocabulary):
    pass


class StudyPurpose(SimpleVocabulary):
    pass


class InterventionAssignment(SimpleVocabulary):
    class Meta(SimpleVocabulary.Meta):
        verbose_name = _("Intervention assignment")
        verbose_name_plural = _("Intervention assignments")


class StudyMasking(SimpleVocabulary):
    class Meta(SimpleVocabulary.Meta):
        verbose_name = _("Study masking")
        verbose_name_plural = _("Study masking")


class StudyAllocation(SimpleVocabulary):
    class Meta(SimpleVocabulary.Meta):
        verbose_name = _("Study allocation")
        verbose_name_plural = _("Study allocation")


class StudyPhase(SimpleVocabulary):
    class Meta(SimpleVocabulary.Meta):
        verbose_name = _("Study phase")
        verbose_name_plural = _("Study phases")


class RecruitmentStatus(SimpleVocabulary):
    class Meta(SimpleVocabulary.Meta):
        verbose_name = _("Recruitment status")
        verbose_name_plural = _("Recruitment statuses")


class TimePerspective(SimpleVocabulary):
    pass


class ObservationalStudyDesign(SimpleVocabulary):
    class Meta(SimpleVocabulary.Meta):
        verbose_name = _("Observational study design")
        verbose_name_plural = _("Observational study designs")


class InstitutionType(SimpleVocabulary):
    pass
