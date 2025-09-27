from django.test import TestCase

from opentrials_ng.trials.models import ClinicalTrial, Contact, Institution
from opentrials_ng.vocabulary.models import Country, RecruitmentStatus, StudyType


class ClinicalTrialModelTests(TestCase):
    def setUp(self) -> None:
        self.country = Country.objects.create(label="Brazil", description="", iso_code="BR")
        self.status = RecruitmentStatus.objects.create(label="Recruiting", description="")
        self.study_type = StudyType.objects.create(label="Interventional", description="")
        self.institution = Institution.objects.create(name="Test Institution", country=self.country)

    def test_mark_published_assigns_identifier_and_date(self) -> None:
        trial = ClinicalTrial.objects.create(
            scientific_title="Example trial",
            primary_sponsor=self.institution,
            study_type=self.study_type,
            recruitment_status=self.status,
        )
        trial.mark_published(identifier="BR-001")

        self.assertEqual(trial.record_status, "published")
        self.assertEqual(trial.trial_id, "BR-001")
        self.assertIsNotNone(trial.registration_date)

    def test_contact_full_name(self) -> None:
        contact = Contact.objects.create(
            given_name="Jane",
            middle_name="Q",
            family_name="Doe",
            email="jane@example.com",
            country=self.country,
        )
        self.assertEqual(contact.full_name, "Jane Q Doe")
