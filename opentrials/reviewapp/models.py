from datetime import datetime

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes import generic
from django.utils import simplejson

from repository.models import ClinicalTrial, Institution
from repository.choices import PROCESSING_STATUS, PUBLISHED_STATUS, ARCHIVED_STATUS
from repository.serializers import deserialize_trial
from tickets.models import Ticket
from utilities import safe_truncate
from vocabulary.models import CountryCode
from polyglot.models import Translation, MANAGED_LANGUAGES_LOWER
from fossil.models import Fossil

from repository.trial_validation import TRIAL_FORMS
from consts import REMARK, MISSING, PARTIAL, COMPLETE
from django.conf import settings
from deleting.models import ControlledDeletion

from django.template.defaultfilters import slugify

SUBMISSION_STATUS = [
    ('draft', _('draft')), # clinical trial is 'processing'
    ('pending', _('pending')), # clinical trial remains 'processing'
    ('approved', _('approved')), # clinical trial is 'published'
    ('resubmit', _('resubmit')), # clinical trial remains 'processing'
]
STATUS_DRAFT = SUBMISSION_STATUS[0][0]
STATUS_PENDING = SUBMISSION_STATUS[1][0]
STATUS_APPROVED = SUBMISSION_STATUS[2][0]
STATUS_RESUBMIT = SUBMISSION_STATUS[3][0]

SUBMISSION_TRANSITIONS = {
    STATUS_DRAFT: [STATUS_PENDING],
    STATUS_PENDING: [STATUS_APPROVED, STATUS_RESUBMIT],
    STATUS_APPROVED: [],
    STATUS_RESUBMIT: [STATUS_DRAFT],
}

ACCESS = [
    ('public', _('Public')),
    ('private', _('Private')),
]

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    preferred_language = models.CharField(_('Preferred language'),max_length=10,
                                choices=settings.MANAGED_LANGUAGES_CHOICES,
                                default=settings.MANAGED_LANGUAGES_CHOICES[-1][0])

    def amount_submissions(self):
        return "%03d" % (Submission.objects.filter(creator=self.user).count())

    def amount_tickets(self):
        return "%03d" % (Ticket.objects.filter(creator=self.user).count())

class Submission(ControlledDeletion):
    class Meta:
        ordering = ['-created']
        permissions = (
            ("review", "Can review"),
        )

    creator = models.ForeignKey(User, related_name='submission_creator', editable=False)
    created = models.DateTimeField(default=datetime.now, editable=False)
    updater = models.ForeignKey(User, null=True, related_name='submission_updater', editable=False)
    updated = models.DateTimeField(null=True, editable=False)
    title = models.TextField('Scientific title', max_length=2000)
    primary_sponsor = models.ForeignKey(Institution, null=True, blank=True,
                                    verbose_name=_('Primary Sponsor'))

    trial = models.OneToOneField(ClinicalTrial, null=True)
    status = models.CharField(_('Status'), max_length=64,
                              choices=SUBMISSION_STATUS,
                              default=SUBMISSION_STATUS[0][0])
    fields_status = models.TextField(_('Fields Status'), max_length=512, null=True,
                                     blank=True, editable=False)
    language = models.CharField(_('Submission language'), max_length=10,
                                choices=settings.MANAGED_LANGUAGES_CHOICES,
                                default=settings.DEFAULT_SUBMISSION_LANGUAGE)
    staff_note = models.TextField(_('Submission note (staff use only)'), max_length=255,
                                    blank=True)

    def save(self, *args, **kwargs):
        if self.id:
            self.updated = datetime.now()
        if self.status == STATUS_APPROVED and self.trial.status == PROCESSING_STATUS:
            self.trial.status = PUBLISHED_STATUS
            self.trial.save()

        super(Submission, self).save(*args, **kwargs)

    def short_title(self):
        return safe_truncate(self.title, 120)

    def creator_username(self):
        return self.creator.username

    def __str__(self):
        return self.short_title()

    def get_mandatory_languages(self):
        langs = {'en'}
        if self.trial.primary_sponsor is not None:
            langs.add(self.trial.primary_sponsor.country.submission_language)

        for rc in self.trial.recruitment_country.all():
            langs.add(rc.submission_language)

        return langs.intersection(set(MANAGED_LANGUAGES_LOWER))

    def get_trans_languages(self):
        return self.get_mandatory_languages() - set([self.language])

    def get_secondary_language(self):
        sec = None
        for lang in self.get_mandatory_languages():
            # fixme: get from settings
            if lang != 'en':
                sec = lang.lower()
                break
        return sec

    def get_absolute_url(self):
        # TODO: use reverse to replace absolute path
        return '/accounts/submission/%s/' % self.id

    def init_fields_status(self):
        # sets the initial status of the fields
        fields_status = {}
        FIELDS = {
            TRIAL_FORMS[0]: MISSING, TRIAL_FORMS[1]: PARTIAL, TRIAL_FORMS[2]: MISSING,

            TRIAL_FORMS[3]: MISSING, TRIAL_FORMS[4]: MISSING, TRIAL_FORMS[5]: MISSING,
            TRIAL_FORMS[6]: MISSING, TRIAL_FORMS[7]: MISSING, TRIAL_FORMS[8]: PARTIAL
        }
        for lang in self.get_mandatory_languages():
            lang = lang.lower()
            fields_status.update({lang: dict(FIELDS)})
            if lang == self.language.lower():
                fields_status[lang].update({TRIAL_FORMS[0]: PARTIAL})

        self.fields_status = simplejson.dumps(fields_status)
        self.save()

    def get_fields_status(self):
        if not getattr(self, '_fields_status', None):
            self._fields_status = simplejson.loads(self.fields_status)

        return self._fields_status

    def get_status(self):
        status = [field for step in self.get_fields_status().values() for field in step.values()]
        if REMARK in status:
            return REMARK
        elif MISSING in status:
            return MISSING
        elif PARTIAL in status:
            return PARTIAL
        return COMPLETE

    def can_delete(self):
        if Fossil.objects.filter(object_id=self.trial.pk).count() > 0:
            return False
        return self.status in [SUBMISSION_STATUS[0][0]]

class RecruitmentCountry(models.Model):
    class Meta:
        verbose_name_plural = _('Recruitment Countries')

    submission = models.ForeignKey(Submission)
    country = models.ForeignKey(CountryCode, verbose_name=_('Country'), related_name='submissionrecruitmentcountry_set')

class Attachment(models.Model):
    class Meta:
        verbose_name_plural = _('Attachments')

    # Function that remove spaces and special characters from filenames
    def new_filename(instance, filename):
        fname, dot, extension = filename.rpartition('.')
        fname = slugify(fname)
        return settings.ATTACHMENTS_DIR + '/' + '%s.%s' % (fname, extension)

    file = models.FileField(_('File'), max_length=250, upload_to=new_filename, blank=True)
    attach_url = models.URLField(_('Link'), blank=True)
    description = models.TextField(_('Description'),blank=True,max_length=8000)
    submission = models.ForeignKey(Submission)
    public = models.BooleanField(_('Public'))

    def get_relative_url(self):
        return self.file.url.replace(settings.PROJECT_PATH, '')

    def __str__(self):
        return str(self.description)

REMARK_STATUS = [
    # initial state, as created by reviewer
    ('open', _('Open')),
    # marked as noted by user
    ('acknowledged', _('Acknowledged')),
    # final state, after reviewer verifies changes by the user
    ('closed', _('Closed')),
]

REMARK_TRANSITIONS = {
    'open':['acknowledged'],
    'acknowledged':['closed','open'],
    'closed':[],
}

class RemarksOpen(models.Manager):
    def get_query_set(self):
        return super(RemarksOpen, self).get_query_set().filter(status__exact='open')

class RemarksAcknowledged(models.Manager):
    def get_query_set(self):
        return super(RemarksAcknowledged, self).get_query_set().filter(status__exact='acknowledged')

class RemarksClosed(models.Manager):
    def get_query_set(self):
        return super(RemarksClosed, self).get_query_set().filter(status__exact='closed')

class Remark(models.Model):
    ''' A reviewer comment regarding a submission field.

    The remark is directed at the field identified by the context attribute.
    '''
    creator = models.ForeignKey(User, editable=False)
    created = models.DateTimeField(default=datetime.now, editable=False)
    submission = models.ForeignKey(Submission)
    context = models.CharField(_('Context'), max_length=256, blank=True)
    text = models.TextField(_('Text'), max_length=2048)
    status = models.CharField(_('Status'), max_length=16, choices=REMARK_STATUS,
                              default=REMARK_STATUS[0][0])

    objects = models.Manager()
    status_open = RemarksOpen()
    status_acknowledged = RemarksAcknowledged()
    status_closed = RemarksClosed()

    def __str__(self):
        return f"{self.pk}:{self.submission_id}"

    def short_text(self):
        return safe_truncate(self.text, 60)

    def context_title(self):
        return _(self.context.title().replace('-', ' '))

NEWS_STATUS = [
    ('pending', _('Pending')),
    ('published', _('Published')),
]

class News(models.Model):

    class Meta:
        verbose_name_plural = _('News')

    title = models.CharField(_('Title'), max_length=256)
    text = models.TextField(_('Text'), max_length=2048)
    created = models.DateTimeField(default=datetime.now, editable=False)
    creator = models.ForeignKey(User, related_name='news_creator', editable=False)
    status = models.CharField(_('Status'), max_length=16, choices=NEWS_STATUS,
                              default=NEWS_STATUS[0][0])
    translations = generic.GenericRelation('NewsTranslation')

    def short_title(self):
        return safe_truncate(self.title, 120)

    def short_text(self):
        return safe_truncate(self.text, 240)

    def __str__(self):
        return str(self.short_title())

class NewsTranslation(Translation):
    title = models.CharField(_('Title'), max_length=256)
    text = models.TextField(_('Text'), max_length=2048)

# SIGNALS
def create_user_profile(sender, instance,**kwargs):
    UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)
