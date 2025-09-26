from django.db import models, IntegrityError

from django.utils.translation import gettext_lazy as _
from django.utils.html import linebreaks
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from fossil.models import Fossil, FossilManager
from datetime import datetime
import string
from random import randrange, choice
from time import sleep

from utilities import safe_truncate

from vocabulary.models import CountryCode, StudyPhase, StudyType, RecruitmentStatus
from vocabulary.models import InterventionCode, InstitutionType, TimePerspective
from vocabulary.models import StudyPurpose, InterventionAssigment, StudyMasking
from vocabulary.models import ObservationalStudyDesign, StudyAllocation

from polyglot.models import Translation
from deleting.models import ControlledDeletion, NotDeletedManager

from repository import choices

from trial_validation import trial_validator
from django.db.models.signals import post_save
from serializers import serialize_trial, deserialize_trial
from serializers import serialize_institution
from serializers import serialize_contact
from serializers import serialize_descriptor
from serializers import serialize_outcome
from serializers import serialize_trialnumber
from serializers import serialize_trialsupportsource
from serializers import serialize_trialsecondarysponsor

from haystack.query import SearchQuerySet

def get_time_perspective_default():
    return TimePerspective.objects.get(id=1)

def length_truncate(text, max_size=240):
    text = text.split('|')
    size=max_size/len(text)
    text = '|'.join([safe_truncate(t,size,'') for t in text])
    return text

# remove digits that look like letters and vice-versa
# remove vowels to avoid forming words
BASE28 = ''.join(d for d in string.digits+string.ascii_lowercase
                   if d not in '1l0aeiou')

TRIAL_ID_TRIES = 3

def generate_trial_id(prefix, num_digits):
    s = str(randrange(2,10)) # start with a numeric digit 2...9
    s += ''.join(choice(BASE28) for i in range(1, num_digits))
    return '-'.join([prefix, s])

class TrialRegistrationDataSetModel(ControlledDeletion):
    """More details on:
        http://reddes.bvsalud.org/projects/clinical-trials/wiki/TrialRegistrationDataSet"""

    def html_dump(self, seen=None, follow_sets=True):
        html = [] # the enclosing <table> and </table> must be provided by the template
        if seen is None:
            seen = set([self.__class__.__name__])
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if field.rel and hasattr(value, 'html_dump'):
                seen.add(value.__class__.__name__)
                content = '<table bgcolor="yellow">%s</table>' % value.html_dump(seen, follow_sets=False)
            else:
                content = str(value)
                if u'\n' in content:
                    content = linebreaks(content)
            html.append('<tr><th>%s</th><td>%s</td></tr>' % (field.name, content))
        if follow_sets:
            for field_name in dir(self):
                try:
                    value = getattr(self, field_name)
                except AttributeError:
                    continue # ignore Manager (objects attribute)
                else:
                    if hasattr(value, '__class__') and value.__class__.__name__=='RelatedManager':
                        inner_html = []
                        for rel_value in value.all():
                            id = '#%s' % rel_value.pk
                            if (hasattr(rel_value, 'html_dump') and
                                    (rel_value.__class__.__name__ not in seen)):
                                seen.add(rel_value.__class__.__name__)
                                content = '<table>%s</table>' % rel_value.html_dump(seen, follow_sets=False)
                            else:
                                content = str(rel_value)
                            if u'\n' in content:
                                content = linebreaks(content)
                            inner_html.append('<tr><th>%s</th><td>%s</td></tr>' % (id, content))
                        content = '<table>%s</table>' % '\n\t'.join(inner_html)
                        html.append('<tr><th>%s</th><td>%s</td></tr>' % (field_name, content))

        return '\n'.join(html)


    class Meta:
        abstract = True

class TrialsPublished(NotDeletedManager):
    def get_query_set(self):
        return super(TrialsPublished, self).get_query_set().filter(status__exact='published')

class ClinicalTrialManager(NotDeletedManager):
    def deserialize_for_fossil(self, data, persistent=False):
        return deserialize_trial(data, persistent)

class TrialFossilsQuerySet(models.query.QuerySet):
    def proxies(self, language=None):
        def get_proxy(obj):
            ret = obj.get_object_fossil()
            ret._language = language
            ret.hash_code = obj.pk
            ret.previous_revision = obj.previous_revision
            return ret

        return [get_proxy(obj) for obj in self.all()]

class TrialsFossilManager(FossilManager):
    _ctype = None

    def get_query_set(self):
        if not self._ctype:
            self._ctype = ContentType.objects.get_for_model(ClinicalTrial)

        return TrialFossilsQuerySet(PublishedTrial).filter(
                content_type=self._ctype,
                )

    def recruiting(self):
        return self.indexed(recruitment_status='recruiting', display='True').filter(is_most_recent=True)

    def published(self, q=None):
        if not q:
            return self.indexed(display='True').filter(is_most_recent=True)
        else:
            return (self.indexed(display='True', scientific_title__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', public_title__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', acronym__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', scientific_acronym__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', scientific_acronym_expansion__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', hc_freetext__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', i_freetext__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', primary_sponsor__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', scientific_contacts__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', utrn_number__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', secondary_ids__icontains=q).filter(is_most_recent=True) |
                    self.indexed(display='True', trial_id__icontains=q).filter(is_most_recent=True))

    def published_advanced(self, q=None, is_most_recent=True, **kwargs):
        '''
        Provides advanced search features in PublishedTrial objects by
        using haystack as a search engine backend interface.

        Strings passed as the ``q`` arg, will be matched against a general
        free-text index, the ``is_most_recent`` indicates if you want recent
        or previous revisions and ``kwargs`` are optional filtering keys.
        '''

        hstack_qs = SearchQuerySet().filter(is_most_recent=is_most_recent)

        if q:
            hstack_qs = hstack_qs.filter(text=q)

        if kwargs:
            for k,v in kwargs.items():
                filters = {k + '__in':v} if isinstance(v, list) else {k:v}
                hstack_qs = hstack_qs.filter(**filters)

        fossil_qs = self.get_query_set()
        pks = [qs_item.pk for qs_item in hstack_qs]

        return fossil_qs.filter(pk__in=pks)

    def archived(self):
        return self.indexed(display='True').filter(is_most_recent=False)

    def proxies(self, language=None):
        return self.get_query_set().proxies(language=language)


class PublishedTrial(Fossil):
    class Meta:
        proxy = True
        verbose_name = _('Published Trial')
        verbose_name_plural = _('Published Trials')

    objects = _default_manager = TrialsFossilManager()

    def __getattr__(self, name):
        if name in ('display','status','scientific_title','public_title',
                    'acronym','scientific_acronym','scientific_acronym_expansion',
                    'hc_freetext','i_freetext','primary_sponsor','scientific_contacts',
                    'utrn_number','secondary_ids'):
            try:
                return self.indexers.key(name).value
            except ObjectDoesNotExist:
                return ''
        else:
            raise AttributeError(name)

    @property
    def trial_id(self):
        try:
            return self.indexers.key('trial_id').value
        except ObjectDoesNotExist:
            return ''

    def get_object_fossil(self, force_load=False):
        if force_load or not getattr(self, '_object_fossil', None):
            self._object_fossil = super(PublishedTrial, self).get_object_fossil()

        return self._object_fossil
    trial = property(get_object_fossil)

class ClinicalTrial(TrialRegistrationDataSetModel):
    objects = ClinicalTrialManager()
    published = TrialsPublished()
    fossils = TrialsFossilManager()

    # TRDS 1
    trial_id = models.CharField(_('Primary Id Number'), null=True, unique=True,
                                max_length=255, editable=False)
    # TRDS 2
    date_registration = models.DateTimeField(_('Date of Registration'), null=True,
                                         editable=False, db_index=True)

    # TRDS 3 - (UTRN required for ICTRP DTD) Secondary Identifying Numbers
    utrn_number = models.CharField(_('UTN Number'), null=True, blank=True,
                                max_length=255, db_index=True)

    # TRDS 10a
    scientific_title = models.TextField(_('Scientific Title'),
                                        max_length=2000)
    # TRDS 10b
    scientific_acronym = models.CharField(_('Scientific Acronym'), blank=True,
                                          max_length=255)
    # TRDS 10b
    scientific_acronym_expansion = models.CharField(_('Scientific Acronym Expansion'),
                                                    blank=True, max_length=255)
    # TRDS 5
    primary_sponsor = models.ForeignKey('Institution', null=True, blank=True,
                                        verbose_name=_('Primary Sponsor'))
    # TRDS 7
    public_contact = models.ManyToManyField('Contact', through='PublicContact',
                                            related_name='public_contact_of_set')
    # TRDS 8
    scientific_contact = models.ManyToManyField('Contact', through='ScientificContact',
                                            related_name='scientific_contact_of_set')

    site_contact = models.ManyToManyField('Contact', through='SiteContact',
                                            related_name='site_contact_of_set')

    # TRDS 9a
    public_title = models.TextField(_('Public Title'), blank=True,
                                    max_length=2000)
    # TRDS 9b
    acronym = models.CharField(_('Acronym'), blank=True, max_length=255)

    # TRDS 9b
    acronym_expansion = models.CharField(_('Acronym Expansion'), blank=True, max_length=255)

    # TRDS 12a
    hc_freetext = models.TextField(_('Health Condition(s)'), blank=True,
                                   max_length=8000)
    # TRDS 13a
    i_freetext = models.TextField(_('Intervention(s)'), blank=True,
                                   max_length=8000)

    # TRDS 13b
    i_code = models.ManyToManyField(InterventionCode)

    # TRDS 14a
    inclusion_criteria = models.TextField(_('Inclusion Criteria'), blank=True,
                                          max_length=8000)
    # TRDS 14b
    gender = models.CharField(_('Inclusion Gender'), max_length=1,
                              choices=choices.INCLUSION_GENDER,
                              default=choices.INCLUSION_GENDER[0][0])
    # TRDS 14c
    agemin_value = models.PositiveIntegerField(_('Inclusion Minimum Age'),
                                               default=0,null=True)
    agemin_unit = models.CharField(_('Minimum Age Unit'), max_length=1,
                                   choices=choices.INCLUSION_AGE_UNIT,
                                   default=choices.INCLUSION_AGE_UNIT[0][0])
    # TRDS 14d
    agemax_value = models.PositiveIntegerField(_('Inclusion Maximum Age'),
                                               default=0,null=True)
    agemax_unit = models.CharField(_('Maximum Age Unit'), max_length=1,
                                   choices=choices.INCLUSION_AGE_UNIT,
                                   default=choices.INCLUSION_AGE_UNIT[0][0])
    # TRDS 14e
    exclusion_criteria = models.TextField(_('Exclusion Criteria'), blank=True,
                                          max_length=8000)
    # TRDS 15a
    study_type = models.ForeignKey(StudyType, null=True, blank=True,
                                   verbose_name=_('Study Type'))

    # TRDS 15b
    study_design = models.TextField(_('Study Design'), blank=True,
                                          max_length=1000)
    ######## begin TRDS 15b - study design details

    expanded_access_program = models.NullBooleanField(_('Expanded access program'),
                                                      null=True, blank=True)
    purpose = models.ForeignKey(StudyPurpose, null=True, blank=True,
                                           verbose_name=_('Study Purpose'))
    intervention_assignment = models.ForeignKey(InterventionAssigment, null=True, blank=True,
                                           verbose_name=_('Intervention Assignment'))
    number_of_arms = models.PositiveIntegerField(_('Number of arms'), null=True, blank=True)
    masking = models.ForeignKey(StudyMasking, null=True, blank=True,
                                           verbose_name=_('Masking type'))
    allocation = models.ForeignKey(StudyAllocation, null=True, blank=True,
                                           verbose_name=_('Allocation type'))
    ######## end TRDS 15b - study design details

    # TRDS 15c
    phase = models.ForeignKey(StudyPhase, null=True, blank=True,
                              verbose_name=_('Study Phase'))

    # TRDS 16a,b (type_enrollment="anticipated")
    enrollment_start_planned = models.CharField( # yyyy-mm or yyyy-mm-dd
        _('Planned Date of First Enrollment'), max_length=10, null=True, blank=True)
    enrollment_start_actual = models.CharField( # yyyy-mm or yyyy-mm-dd
        _('Actual Date of First Enrollment'), max_length=10, null=True, blank=True)
    enrollment_end_planned = models.CharField( # yyyy-mm or yyyy-mm-dd
        _('Planned Date of Last Enrollment'), max_length=10, null=True, blank=True)
    enrollment_end_actual = models.CharField( # yyyy-mm or yyyy-mm-dd
        _('Actual Date of Last Enrollment'), max_length=10, null=True, blank=True)

    # TRDS 17
    target_sample_size = models.PositiveIntegerField(_('Target Sample Size'),
                                                       default=0)
    # TRDS 18
    recruitment_status = models.ForeignKey(RecruitmentStatus, null=True, blank=True,
                                           verbose_name=_('Recruitment Status'))

    outdated = models.BooleanField(default=False, blank=False,
                                           verbose_name=_('Outdated Trial'))

    # TRDS 11 - Countries of Recruitment
    recruitment_country = models.ManyToManyField(CountryCode,
        help_text=u'Several countries may be selected, one at a time')

    #Observational filelds
    is_observational = models.BooleanField(default=False, null=False)


    time_perspective = models.ForeignKey(TimePerspective, null=True, blank=True,
                                   default=get_time_perspective_default,
                                   verbose_name=_('Time Perspective'))

    observational_study_design = models.ForeignKey(ObservationalStudyDesign,
                                                   null=True, blank=True,
                                                   verbose_name=_('Observational Study Design')
                                                   )

    ################################### internal use, administrative fields ###
    created = models.DateTimeField(default=datetime.now, editable=False)
    updated = models.DateTimeField(_('Last Update'), null=True, editable=False)
    exported = models.DateTimeField(null=True, editable=False)
    status = models.CharField(_('Status'), max_length=64,
                              choices=choices.TRIAL_RECORD_STATUS,
                              default=choices.TRIAL_RECORD_STATUS[0][0])
    staff_note = models.CharField(_('Record Note (staff use only)'),
                                  max_length='255',
                                  blank=True)
    language = models.CharField(_('Submission language'), max_length=10,
                                choices=settings.MANAGED_LANGUAGES_CHOICES,
                                default=settings.DEFAULT_SUBMISSION_LANGUAGE)

    translations = generic.GenericRelation('ClinicalTrialTranslation')

    class Meta:
        ordering = ['-updated',]

    def save(self, *args, **kwargs):
        if self.id and not kwargs.get('dont_update',False):
            self.updated = datetime.now()
        if self.status == choices.PUBLISHED_STATUS and not self.trial_id:
            # assigns the date of publication/registration
            self.date_registration = datetime.now()

            for i in range(TRIAL_ID_TRIES):
                self.trial_id = generate_trial_id(settings.TRIAL_ID_PREFIX, settings.TRIAL_ID_DIGITS)
                try:
                    super(ClinicalTrial, self).save(*args, **kwargs)
                except IntegrityError:
                    if i < TRIAL_ID_TRIES:
                        sleep(2**i) # wait to try again
                    else:
                        raise # all tries exhausted: give up
                else:
                    break # no need to try again
        else:
            super(ClinicalTrial, self).save(*args, **kwargs)

    def identifier(self):
        return self.trial_id or '(req:%s)' % self.pk

    def short_title(self):
        return safe_truncate(self.main_title(), 120)

    def very_short_title(self):
        tit = u'%s - %s' % (self.identifier(),
                            self.short_title())
        return safe_truncate(tit, 60)

    def main_title(self):
        if self.public_title:
            return self.public_title
        else:
            return self.scientific_title

    def __str__(self):
        return f"{self.identifier()} {self.short_title()}"

    def trial_id_display(self):
        ''' return the trial id or an explicit message it is None '''
        if self.trial_id:
            return self.trial_id
        else:
            msg = 'not assigned (request #%)' % self.pk

    def acronym_display(self):
        if self.acronym_expansion:
            return u'%s: %s' % (self.acronym, self.acronym_expansion)
        else:
            return self.acronym

    def scientific_acronym_display(self):
        if self.scientific_acronym_expansion:
            return u'%s: %s' % (self.scientific_acronym, self.scientific_acronym_expansion)
        else:
            return self.scientific_acronym

    def record_status(self):
        return self.submission.status

    #TRDS 3 - Secondarty ID Numbers
    def trial_number(self):
        return self.trialnumber_set.all().select_related();

    # TRDS 4 - Source(s) of Monetary Support
    def support_sources(self):
        return self.trialsupportsource_set.all()

    # TRDS 6 - Secondary Sponsor(s)
    def secondary_sponsors(self):
        return self.trialsecondarysponsor_set.all()

    def updated_str(self):
        return self.updated.strftime('%Y-%m-%d %H:%M')
    updated_str.short_description = _('Updated')

    def related_health_conditions(self, aspect, level):
        ''' return set of hc-code or keywords related to this trial with a
            given relationship
        '''
        return self.descriptor_set.filter(aspect=aspect, level=level).select_related()

    # TRDS 11 - Countries of Recruitment
    def trial_recruitment_country(self):
        ''' return set of countries of recruitment related to this trial with
        '''
        return self.recruitment_country.all().select_related()

    #TRDS 12b - Health Condition Codes are generic, high level descriptors
    def hc_code(self):
        ''' return set of HC-Code related to this trial with
            aspect = 'HealthCondition'
            level  = 'general'
        '''
        return self.related_health_conditions('HealthCondition','general')

    #TRDS 12c - Health Condition Keywords are specific descriptors
    def hc_keyword(self):
        ''' return set of HC-Code related to this trial with
            aspect = 'HealthCondition'
            level  = 'specific'
        '''
        return self.related_health_conditions('HealthCondition','specific')

    #TRDS 13b - Intervetion Code
    def intervention_code(self):
        ''' return set of Intervention Code related to this trial with
        '''
        return self.i_code.all().select_related()

    #TRDS 13c - Intervention Keyword
    def intervention_keyword(self):
        ''' return set of Intervention Keyword related to this trial with
        '''
        return self.descriptor_set.filter(aspect='Intervention').select_related()

    #TRDS 19 - Primary Outcomes
    def primary_outcomes(self):
        ''' return set of Primary Outcomes related to this trial with
        '''
        return self.outcome_set.filter(interest='primary').select_related()

    #TRDS 20 - Secondary Outcomes
    def secondary_outcomes(self):
        ''' return set of Secondary Outcomes related to this trial with
        '''
        return self.outcome_set.filter(interest='secondary').select_related()

    def public_contacts(self):
        return self.public_contact.all().select_related()

    def scientific_contacts(self):
        return self.scientific_contact.all().select_related()

    def site_contacts(self):
        return [ st.contact for st in self.sitecontact_set.all().select_related() ]

    def trial_attach(self):
        return self.submission.attachment_set.all().select_related()

    def serialize_for_fossil(self, as_string=True):
        return serialize_trial(self, as_string, attrs_to_ignore=['status','_deleted'])

    @property
    def public_url(self):
        return reverse('repository.trial_registered', kwargs={'trial_fossil_id': self.trial_id})

    def create_fossil(self):
        fossil = PublishedTrial.objects.create_for_object(self)
        fossil.set_indexer(key='trial_id', value=self.trial_id)
        fossil.set_indexer(key='status', value=self.status)
        fossil.set_indexer(key='display', value='True')

        fossil.set_indexer(key='scientific_title', value=length_truncate("%s%s" % (self.scientific_title, '|'.join([trans.scientific_title for trans in self.translations.all()]))))
        fossil.set_indexer(key='public_title', value=length_truncate("%s%s" % (self.public_title, '|'.join([trans.public_title for trans in self.translations.all()]))))
        fossil.set_indexer(key='acronym', value="%s%s" % (self.acronym, '|'.join([trans.acronym for trans in self.translations.all()])))
        fossil.set_indexer(key='scientific_acronym', value="%s%s" % (self.scientific_acronym, '|'.join([trans.scientific_acronym for trans in self.translations.all()])))
        fossil.set_indexer(key='scientific_acronym_expansion', value="%s%s" % (self.scientific_acronym_expansion, '|'.join([trans.scientific_acronym_expansion for trans in self.translations.all()])))
        fossil.set_indexer(key='hc_freetext', value=length_truncate("%s%s" % (self.hc_freetext, '|'.join([trans.hc_freetext for trans in self.translations.all()]))))
        fossil.set_indexer(key='i_freetext', value=length_truncate("%s%s" % (self.i_freetext, '|'.join([trans.i_freetext for trans in self.translations.all()]))))
        fossil.set_indexer(key='primary_sponsor', value=self.primary_sponsor.name)
        fossil.set_indexer(key='scientific_contacts', value="%s" % ('|'.join(["%s|%s" % (contact.name(),contact.email) for contact in self.scientific_contacts()])))
        fossil.set_indexer(key='utrn_number', value=self.utrn_number)
        fossil.set_indexer(key='secondary_ids', value="%s" % ('|'.join([t_number.id_number for t_number in self.trial_number()])))


        if self.recruitment_status:
            fossil.set_indexer(key='recruitment_status', value=self.recruitment_status.label)

        return fossil

# Sets validation model to ClinicalTrial
trial_validator.model = ClinicalTrial


class ClinicalTrialTranslation(Translation):
    # TRDS 10a
    scientific_title = models.TextField(_('Scientific Title'), max_length=2000)
    # TRDS 10b
    scientific_acronym = models.CharField(_('Scientific Acronym'), blank=True, max_length=255)
    # TRDS 10b
    scientific_acronym_expansion = models.CharField(_('Scientific Acronym Expansion'), blank=True, max_length=255)
    # TRDS 9a
    public_title = models.TextField(_('Public Title'), blank=True, max_length=2000)
    # TRDS 9b
    acronym = models.CharField(_('Acronym'), blank=True, max_length=255)
    # TRDS 9b
    acronym_expansion = models.CharField(_('Acronym Expansion'), blank=True, max_length=255)
    # TRDS 12a
    hc_freetext = models.TextField(_('Health Condition(s)'), blank=True, max_length=8000)
    # TRDS 13a
    i_freetext = models.TextField(_('Intervention(s)'), blank=True, max_length=8000)
    # TRDS 14a
    inclusion_criteria = models.TextField(_('Inclusion Criteria'), blank=True, max_length=8000)
    # TRDS 14e
    exclusion_criteria = models.TextField(_('Exclusion Criteria'), blank=True, max_length=8000)
    # TRDS 15b
    study_design = models.TextField(_('Study Design'), blank=True, max_length=1000)

    # This method is here just to be an example
    #@classmethod
    #def get_multilingual_fields(cls):
    #    return ['public_title']

    def serialize_for_fossil(self, as_string=True):
        return serialize_trial(self, as_string, attrs_to_ignore=['content_type','object_id'])

################################### Entities linked to a Clinical Trial ###

# TRDS 3 - Secondary Identifying Numbers

class TrialNumber(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial)
    issuing_authority = models.CharField(_('Issuing Authority'),
                                         max_length=255, db_index=True,)
    id_number = models.CharField(_('Secondary Id Number'),
                                max_length=255, db_index=True)

    def __str__(self):
        return f"{self.issuing_authority}: {self.id_number}"

    def serialize_for_fossil(self, as_string=True):
        return serialize_trialnumber(self, as_string)

# TRDS 6 - Secondary Sponsor(s)
class TrialSecondarySponsor(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial)
    institution = models.ForeignKey('Institution', verbose_name=_('Institution'))

    def __str__(self):
        return str(self.institution)

    def serialize_for_fossil(self, as_string=True):
        return serialize_trialsecondarysponsor(self, as_string)

# TRDS 4 - Source(s) of Monetary Support
class TrialSupportSource(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial)
    institution = models.ForeignKey('Institution', verbose_name=_('Institution'))

    def __str__(self):
        return str(self.institution)

    def serialize_for_fossil(self, as_string=True):
        return serialize_trialsupportsource(self, as_string)

# TRDS 5 - Primary Sponsor

class Institution(TrialRegistrationDataSetModel):
    name = models.CharField(_('Name'), max_length=255)
    address = models.TextField(_('Postal Address'), max_length=1500, blank=True)
    country = models.ForeignKey(CountryCode, verbose_name=_('Country'))
    state = models.CharField(_('State'), max_length=255, blank=True, default='', choices=settings.LOCAL_STATE_CHOICES)
    city = models.CharField(_('City'), max_length=255, blank=True, default='')
    creator = models.ForeignKey(User, related_name='institution_creator', editable=False)
    i_type = models.ForeignKey(InstitutionType, null=True, blank=True,
                                           verbose_name=_('Institution type'))

    def __str__(self):
        return safe_truncate(self.name, 120)

    def serialize_for_fossil(self, as_string=True):
        return serialize_institution(self, as_string)

# TRDS 7 - Contact for Public Queries
# TRDS 8 - Contact for Scientific Queries

class Contact(TrialRegistrationDataSetModel):
    firstname = models.CharField(_('First Name'), max_length=50)
    middlename = models.CharField(_('Middle Name'), max_length=50, blank=True)
    lastname = models.CharField(_('Last Name'), max_length=50)
    email = models.EmailField(_('E-mail'), max_length=255)
    affiliation = models.ForeignKey(Institution, null=True, blank=True,
                                    verbose_name=_('Institution'))
    address = models.CharField(_('Address'), max_length=255, blank=True)
    city = models.CharField(_('City'), max_length=255, blank=True)
    country = models.ForeignKey(CountryCode, null=True, blank=True,
                                verbose_name=_('Country'),)
    zip = models.CharField(_('Postal Code'), max_length=50, blank=True)
    telephone = models.CharField(_('Telephone'), max_length=255, blank=True)

    creator = models.ForeignKey(User, related_name='contact_creator', editable=False)

    def name(self):
        names = self.firstname + u' ' + self.middlename + u' ' + self.lastname
        return u' '.join(names.split())

    def __str__(self):
        return self.name()

    def serialize_for_fossil(self, as_string=True):
        return serialize_contact(self, as_string)

class PublicContact(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial)
    contact = models.ForeignKey(Contact, verbose_name=_('Contact'))
    status = models.CharField(_('Status'), max_length=255,
                            choices = choices.CONTACT_STATUS,
                            default = choices.CONTACT_STATUS[0][0])
    class Meta:
        unique_together = ('trial', 'contact')

    def __str__(self):
        return (
            f"Public Contact for {self.trial.short_title()}: {self.contact.name()}"
            f" ({self.status})"
        )

class ScientificContact(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial)
    contact = models.ForeignKey(Contact, verbose_name=_('Contact'))
    status = models.CharField(_('Status'), max_length=255,
                            choices = choices.CONTACT_STATUS,
                            default = choices.CONTACT_STATUS[0][0])
    class Meta:
        unique_together = ('trial', 'contact')

    def __str__(self):
        return (
            f"Scientific Contact for {self.trial.short_title()}: {self.contact.name()}"
            f" ({self.status})"
        )

class SiteContact(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial)
    contact = models.ForeignKey(Contact, verbose_name=_('Contact'))
    status = models.CharField(_('Status'), max_length=255,
                            choices = choices.CONTACT_STATUS,
                            default = choices.CONTACT_STATUS[0][0])
    class Meta:
        unique_together = ('trial', 'contact')

    def __str__(self):
        return (
            f"Site Contact for {self.trial.short_title()}: {self.contact.name()}"
            f" ({self.status})"
        )

# TRDS 19 - Primary Outcome(s)
# TRDS 20 - Key Secondary Outcome(s)

class Outcome(TrialRegistrationDataSetModel):
    trial = models.ForeignKey(ClinicalTrial)
    interest = models.CharField(_('Interest'), max_length=32,
                               choices=choices.OUTCOME_INTEREST,
                               default = choices.OUTCOME_INTEREST[0][0])
    description = models.TextField(_('Outcome Description'), max_length=8000)

    translations = generic.GenericRelation('OutcomeTranslation')

    class Meta:
        order_with_respect_to = 'trial'

    def __str__(self):
        return safe_truncate(self.description, 80)

    def translations_all(self):
        return self.translations.all()

    def serialize_for_fossil(self, as_string=True):
        return serialize_outcome(self, as_string)

class OutcomeTranslation(Translation):
    description = models.TextField(_('Outcome Description'), max_length=8000)


class Descriptor(TrialRegistrationDataSetModel):
    class Meta:
        order_with_respect_to = 'trial'

    trial = models.ForeignKey(ClinicalTrial)
    aspect = models.CharField(_('Trial Aspect'), max_length=255,
                        choices=choices.TRIAL_ASPECT)
    vocabulary = models.CharField(_('Vocabulary'), max_length=255,
                        choices=choices.DESCRIPTOR_VOCABULARY)
    version = models.CharField(_('Version'), max_length=64, blank=True)
    level = models.CharField(_('Level'), max_length=64,
                        choices=choices.DESCRIPTOR_LEVEL)
    code = models.CharField(_('Code'), max_length=255)
    text = models.CharField(_('Text'), max_length=255, blank=True)

    translations = generic.GenericRelation('DescriptorTranslation')

    def __str__(self):
        return f"[{self.vocabulary}] {self.code}: {self.text}"

    def trial_identifier(self):
        return self.trial.identifier()

    def translations_all(self):
        return self.translations.all()

    def serialize_for_fossil(self, as_string=True):
        return serialize_descriptor(self, as_string)

class DescriptorTranslation(Translation):
    text = models.CharField(_('Text'), max_length=255, blank=True)

# SIGNALS

def clinicaltrial_post_save(sender, instance, signal, **kwargs):
    # This signal calls validation method to validate the instance according to
    # rules made with mandatory fields but aren't obligatory on the model
    trial_validator.validate(instance)

    # Creates a fossil if the status is equal to 'published'
    if instance.status == choices.PUBLISHED_STATUS:
        instance.create_fossil()

post_save.connect(clinicaltrial_post_save, sender=ClinicalTrial)
