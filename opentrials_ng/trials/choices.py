"""Choice definitions for the clinical trials registry domain."""
from django.utils.translation import gettext_lazy as _

INSTITUTIONAL_RELATION = (
    ("support", _("Source of monetary or material support")),
    ("secondary_sponsor", _("Secondary sponsor")),
)

CONTACT_RELATION = (
    ("public", _("Contact for Public Queries")),
    ("scientific", _("Contact for Scientific Queries")),
    ("site", _("Contact for Recruitment Site Queries")),
)

CONTACT_STATUS = (
    ("active", _("Active and current contact")),
    ("inactive", _("Inactive or previous contact")),
)

OUTCOME_INTEREST = (
    ("primary", _("Primary")),
    ("secondary", _("Secondary")),
)

TRIAL_RECORD_STATUS = (
    ("draft", _("Draft")),
    ("submitted", _("Submitted")),
    ("published", _("Published")),
    ("archived", _("Archived")),
)

INCLUSION_GENDER = (
    ("any", _("Both")),
    ("male", _("Male")),
    ("female", _("Female")),
)

INCLUSION_AGE_UNIT = (
    ("none", _("No limit")),
    ("years", _("Years")),
    ("months", _("Months")),
    ("weeks", _("Weeks")),
    ("days", _("Days")),
    ("hours", _("Hours")),
)

TRIAL_ASPECT = (
    ("health_condition", _("Health Condition or Problem Studied")),
    ("intervention", _("Intervention")),
)

DESCRIPTOR_LEVEL = (
    ("general", _("General")),
    ("specific", _("Specific")),
)

DESCRIPTOR_VOCABULARY = (
    ("decs", _("DeCS: Health Sciences Descriptors")),
    ("icd10", _("ICD-10: International Classification of Diseases (10th. rev.)")),
)
