# coding: utf-8

try:
    set
except:
    from sets import Set as set

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.forms.models import inlineformset_factory
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import loader
from django.db.models import Q
from django.views.generic.list_detail import object_list
from django.conf import settings
from django.template.defaultfilters import slugify
from django.template.context import RequestContext
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from django.utils.translation import get_language
from django.utils.encoding import smart_str

from reviewapp.models import Attachment, Submission, Remark
from reviewapp.models import STATUS_PENDING, STATUS_RESUBMIT, STATUS_DRAFT, STATUS_APPROVED
from reviewapp.forms import ExistingAttachmentForm,NewAttachmentForm
from reviewapp.consts import STEP_STATES, REMARK, MISSING, PARTIAL, COMPLETE
from reviewapp.views import submission_edit_published, send_opentrials_email

from repository.trial_validation import trial_validator
from repository.models import ClinicalTrial, Descriptor, TrialNumber
from repository.models import TrialSecondarySponsor, TrialSupportSource, Outcome
from repository.models import PublicContact, ScientificContact, SiteContact, Contact, Institution
from repository.models import ClinicalTrialTranslation
from repository.trds_forms import MultilingualBaseFormSet
from repository.trds_forms import GeneralHealthDescriptorForm, PrimarySponsorForm
from repository.trds_forms import SecondaryIdForm, make_secondary_sponsor_form
from repository.trds_forms import make_support_source_form, TrialIdentificationForm
from repository.trds_forms import SpecificHealthDescriptorForm, HealthConditionsForm
from repository.trds_forms import InterventionDescriptorForm, InterventionForm
from repository.trds_forms import RecruitmentForm, StudyTypeForm, PrimaryOutcomesForm
from repository.trds_forms import SecondaryOutcomesForm, make_public_contact_form
from repository.trds_forms import make_scientifc_contact_form, make_contact_form, NewInstitution
from repository.trds_forms import make_site_contact_form, TRIAL_FORMS
from vocabulary.models import RecruitmentStatus, VocabularyTranslation, CountryCode, InterventionCode
from vocabulary.models import StudyPurpose, InterventionAssigment, StudyMasking, StudyAllocation
from vocabulary.models import MailMessage, InstitutionType

from polyglot.multilingual_forms import modelformset_factory

from fossil.fields import DictKeyAttribute
from fossil.models import Fossil

from utilities import user_in_group, normalize_age, denormalize_age

import datetime

import choices
import settings
import csv
import cStringIO
from zipfile import ZipFile, ZIP_DEFLATED

EXTRA_FORMS = 1

MENU_SHORT_TITLE = [_('Trial Identif.'),
                    _('Spons.'),
                    _('Health Cond.'),
                    _('Interv.'),
                    _('Recruit.'),
                    _('Study Type'),
                    _('Outcomes'),
                    _('Contacts'),
                    _('Attachs')]
def localized_vocabulary(model_instance, language, *args):
    """
    Retrieve vocabulary in a given language

    default *args: ['pk', 'description', 'label']
    """
    if not args:
        args = ['pk', 'description', 'label']

    model_qs = model_instance.objects.all()
    localized_list = model_qs.values(*args)
    for item in localized_list:
        try:
            t = VocabularyTranslation.objects.get_translation_for_object(
                                language, model=model_instance,
                                object_id=item['pk'])
            if t.description:
                item['description'] = t.description
        except ObjectDoesNotExist:
            pass

    return localized_list

def is_outdate(ct):

    now = datetime.date.today()

    start_planned = ct.enrollment_start_planned
    end_planned = ct.enrollment_end_planned
    start_actual = ct.enrollment_start_actual
    end_actual = ct.enrollment_end_planned

    if start_planned is not None:
        start_planned = start_planned
        if start_planned < now and start_actual is None:
            return True

    if end_planned is not None:
        end_planned = end_planned
        if end_planned < now and end_actual is None:
            return True

    return False

def check_user_can_edit_trial(func):
    """
    Decorator to check if current user has permission to edit a given clinical trial
    """
    def _inner(request, trial_pk, *args, **kwargs):
        request.ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))
        request.can_change_trial = True

        if request.ct.submission.status == STATUS_APPROVED:
            request.can_change_trial = False
            parsed_link = reverse(submission_edit_published, args=[trial_pk])
            message_confirm_update = str(_("Updating a clinical trial, a new revision process will be started. Would you like to continue?"))
            edit_trial_button_string = '<form action="%s" onsubmit="return window.confirm(\'%s\')"><input type="submit" value="%s"/> </form>' % (parsed_link,message_confirm_update,str(_('Update')))
            messages.warning(request, _('This trial cannot be modified because it has already been approved.%s') % edit_trial_button_string)

        # Creator can edit in statuses draft and resubmited but can view on other statuses
        elif request.user == request.ct.submission.creator:
            if request.ct.submission.status not in (STATUS_DRAFT, STATUS_RESUBMIT):
                request.can_change_trial = False
                messages.warning(request, _('You cannot modify this trial because it is being revised.'))

        elif not request.user.is_staff: # If this is a staff member...
            request.can_change_trial = False
            messages.warning(request, _('Only the creator can modify a trial.'))

            # A reviewer in status pending
            if not( request.ct.submission.status == STATUS_PENDING and
                    user_in_group(request.user, 'reviewers') ):

                resp = render_to_response(
                        '403.html',
                        {'site': Site.objects.get_current()},
                        context_instance=RequestContext(request),
                        )
                resp.status_code = 403

                return resp

        return func(request, trial_pk, *args, **kwargs)

    return _inner

@login_required
@check_user_can_edit_trial
def edit_trial_index(request, trial_pk):
    ct = request.ct

    status = ct.submission.get_status()

    if status in [REMARK, MISSING]:
        submit = False
    else:
        submit = request.can_change_trial

    if request.method == 'POST' and submit:
        sub = ct.submission
        sub.status = STATUS_PENDING

        recepient = ct.submission.creator.email
        subject = _('Trial Submitted')
        message =  MailMessage.objects.get(label='submitted').description
        if '%s' in message:
            message = message % ct.public_title
        send_opentrials_email(subject, message, recepient)

        sub.save()
        return HttpResponseRedirect(reverse('reviewapp.dashboard'))
    else:
        ''' start view '''

        # Changes status from "resubmit" to "draft" if user is the creator
        sub = ct.submission
        if sub.status == STATUS_RESUBMIT and request.user == sub.creator:
            sub.status = STATUS_DRAFT
            sub.save()

        fields_status = ct.submission.get_fields_status()

        links = []
        for i, name in enumerate(TRIAL_FORMS):
            data = dict(label=_(name))
            data['url'] = reverse('step_' + str(i + 1), args=[trial_pk])

            trans_list = []
            for lang in ct.submission.get_mandatory_languages():
                trans = {}
                lang = lang.lower()
                step_status = fields_status.get(lang, {}).get(name, None)
                if step_status == MISSING:
                    trans['icon'] = settings.MEDIA_URL + 'images/form-status-missing.png'
                    trans['msg'] = STEP_STATES[MISSING-1][1].title()
                    trans['leg'] = _("There are required fields missing.")
                elif step_status == PARTIAL:
                    trans['icon'] = settings.MEDIA_URL + 'images/form-status-partial.png'
                    trans['msg'] = STEP_STATES[PARTIAL-1][1].title()
                    trans['leg'] = _("All required fields were filled.")
                elif step_status == COMPLETE:
                    trans['icon'] = settings.MEDIA_URL + 'images/form-status-complete.png'
                    trans['msg'] = STEP_STATES[COMPLETE-1][1].title()
                    trans['leg'] = _("All fields were filled.")
                elif step_status == REMARK:
                    trans['icon'] = settings.MEDIA_URL + 'images/form-status-remark.png'
                    trans['msg'] = STEP_STATES[REMARK-1][1].title()
                    trans['leg'] = _("There are fields with remarks.")
                else:
                    trans['icon'] = settings.MEDIA_URL + 'media/img/admin/icon_error.gif'
                    trans['msg'] = _('Error')
                    trans['leg'] = _('Error')

                trans_list.append(trans)
            data['trans'] = trans_list
            links.append(data)

        status_message = {}
        if status == REMARK:
            status_message['icon'] = settings.MEDIA_URL + 'images/form-status-remark.png'
            status_message['msg'] = _("There are fields with remarks.")
        elif status == MISSING:
            status_message['icon'] = settings.MEDIA_URL + 'images/form-status-missing.png'
            status_message['msg'] = _("There are required fields missing.")
        elif status == PARTIAL:
            status_message['icon'] = settings.MEDIA_URL + 'images/form-status-partial.png'
            status_message['msg'] = _("All required fields were filled.")
        elif status == COMPLETE:
            status_message['icon'] = settings.MEDIA_URL + 'images/form-status-complete.png'
            status_message['msg'] = _("All fields were filled.")
        else:
            status_message['icon'] = settings.MEDIA_URL + 'media/img/admin/icon_error.gif'
            status_message['msg'] = _("Error")

        return render_to_response('repository/trial_index.html',
                                  {'trial_pk':trial_pk,
                                   'submission':ct.submission,
                                   'links':links,
                                   'status': status,
                                   'submit': submit,
                                   'status_message': status_message,},
                                   context_instance=RequestContext(request))

def full_view(request, trial_pk):
    ''' full view '''
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))
    return render_to_response('repository/trds.html',
                              {'fieldtable':ct.html_dump()},
                               context_instance=RequestContext(request))


def recruiting(request):
    ''' List all registered trials with recruitment_status = recruiting
    '''
    object_list = ClinicalTrial.fossils.recruiting()
    object_list = object_list.proxies(language=request.LANGUAGE_CODE)

    """
    recruitments = RecruitmentStatus.objects.filter(label__exact='recruiting')
    if len(recruitments) > 0:
        object_list = ClinicalTrial.published.filter(recruitment_status=recruitments[0])
    else:
        object_list = None

    for obj in object_list:
        try:
            trans = obj.translations.get(language__iexact=request.LANGUAGE_CODE)
        except ClinicalTrialTranslation.DoesNotExist:
            trans = None

        if trans:
            if trans.public_title:
                obj.public_title = trans.public_title
            if trans.public_title:
                obj.scientific_title = trans.scientific_title

        if obj.recruitment_status:
            try:
                rec_status_trans = obj.recruitment_status.translations.get(language__iexact=request.LANGUAGE_CODE)
            except VocabularyTranslation.DoesNotExist:
                rec_status_trans = obj.recruitment_status
            obj.rec_status = rec_status_trans.label
    """

    # pagination
    paginator = Paginator(object_list, getattr(settings, 'PAGINATOR_CT_PER_PAGE', 10))

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)


    return render_to_response('repository/clinicaltrial_recruiting.html',
                              {'objects': objects,
                               'page': page,
                               'paginator': paginator},
                               context_instance=RequestContext(request))

#Applied Search Criteria
def get_humanizer(language_code, min_age_unit, max_age_unit):

    def humanize_search_values(key, value, default_str=None):
        """
        This function is used to translate advanced search params
        into formatted values ready to print in templates.

        If a key/value is unknown, a default string is returned.
        """
        if default_str is None:
            default_str = '###unknown search parameters###'

        age_unit_labels = {
            'Y':_('years'),
            'M':_('months'),
            'W':_('weeks'),
            'D':_('days'),
            'H':_('hours'),
        }

        if key == 'rec_country':
            humanized = [_('Recruitment Country')]

            for country in localized_vocabulary(CountryCode, language_code):
                if country['label'] == value:
                    humanized.append(country['description'])
                    break
            else:
                humanized.append(default_str)
            return humanized

        elif key == 'rec_status_exact':
            humanized = [_('Recruitment Status')]

            statuses = []
            for status in localized_vocabulary(RecruitmentStatus, language_code):
                if status['label'] in value:
                    statuses.append(status['description'])
            humanized.append(', '.join(statuses) if statuses else default_str)
            return humanized

        elif key == 'is_observational':
            humanized = [_('Study Type')]

            if value not in ['true','false']:
                humanized.append(default_str)
            else:
                humanized.append(_('Observational') if value == 'true' else _('Interventional'))
            return humanized

        elif key == 'i_type_exact':
            humanized = [_('Institution type')]

            i_types = []
            for i_type in localized_vocabulary(InstitutionType, language_code):
                if i_type['label'] in value:
                    i_types.append(i_type['description'])
            humanized.append(', '.join(i_types) if i_types else default_str)
            return humanized

        elif key == 'gender':
            humanized = [_('Inclusion Gender')]

            if value in ['male', 'female', 'both']:
                humanized.append(_(value))
            else:
                humanized.append(default_str)
            return humanized
        elif key == 'maximum_recruitment_age__gte':
            #due to the logic applied to the query, the key names are inverted (min an max age)
            #see the index view callable
            humanized = [_('Inclusion Minimum Age')]
            try:
                humanized.append(u'%s %s' % (denormalize_age(value, min_age_unit), age_unit_labels[min_age_unit]))
            except KeyError:
                humanized.append(u'%s %s' % (denormalize_age(value, 'Y'), age_unit_labels['Y']))
            return humanized
        elif key == 'minimum_recruitment_age__lte':
            #due to the logic applied to the query, the key names are inverted (min an max age)
            #see the index view callable
            humanized = [_('Inclusion Maximum Age')]
            try:
                humanized.append(u'%s %s' % (denormalize_age(value, max_age_unit), age_unit_labels[max_age_unit]))
            except KeyError:
                humanized.append(u'%s %s' % (denormalize_age(value, 'Y'), age_unit_labels['Y']))
            return humanized
        else:
            return [key, default_str]

    return humanize_search_values

def index(request):
    ''' List all registered trials
        If you use a search term, the result is filtered
    '''
    q = request.GET.get('q', '').strip()
    rec_status = request.GET.getlist('rec_status')
    rec_country = request.GET.get('rec_country', '').strip()
    is_observational = request.GET.get('is_observ', '').strip()
    i_type = request.GET.getlist('i_type')
    gender = request.GET.get('gender', '').strip()
    minimum_age = request.GET.get('age_min','').strip()
    maximum_age = request.GET.get('age_max','').strip()
    minimum_age_unit = request.GET.get('age_min_unit','').strip()
    maximum_age_unit = request.GET.get('age_max_unit','').strip()

    filters = {}
    if rec_status:
        filters['rec_status_exact'] = rec_status
    if rec_country:
        filters['rec_country'] = rec_country
    if is_observational:
        filters['is_observational'] = is_observational
    if i_type:
        filters['i_type_exact'] = i_type
    if gender:
        filters['gender'] = gender

    #query by age logic explained at http://reddes.bvsalud.org/projects/clinical-trials/wiki/InclusionCriteriaField
    if minimum_age:
        try:
            filters['maximum_recruitment_age__gte'] = normalize_age(int(minimum_age),minimum_age_unit)
        except (ValueError, KeyError):
            filters['maximum_recruitment_age__gte'] = 0
    if maximum_age:
        try:
            filters['minimum_recruitment_age__lte'] = normalize_age(int(maximum_age),maximum_age_unit)
        except (ValueError, KeyError):
            filters['minimum_recruitment_age__lte'] = normalize_age(200, 'Y')


    object_list = ClinicalTrial.fossils.published_advanced(q=q, **filters)
    unsubmiteds = Submission.objects.filter(title__icontains=q).filter(Q(status='draft') | Q(status='resubmit')).order_by('-updated')
    object_list = object_list.proxies(language=request.LANGUAGE_CODE)
    paginator = Paginator(object_list, getattr(settings, 'PAGINATOR_CT_PER_PAGE', 10))

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)

    search_humanizer = get_humanizer(request.LANGUAGE_CODE.lower(), minimum_age_unit, maximum_age_unit)
    search_filters = [search_humanizer(k, v)
                        for k, v in filters.items() if v]

    return render_to_response('repository/clinicaltrial_list.html',
                              {'objects': objects,
                               'page': page,
                               'paginator': paginator,
                               'q': q,
                               'unsubmiteds':unsubmiteds,
                               'outdated_flag':settings.MEDIA_URL + 'media/img/admin/icon_error.gif',
                               'search_filters': dict(search_filters),
                               },
                               context_instance=RequestContext(request))

@login_required
def trial_view(request, trial_pk):
    ''' show details of a trial of a user logged '''
    ct = get_object_or_404(ClinicalTrial, id=int(trial_pk))
    review_mode = True
    if not request.user.is_staff and not user_in_group(request.user, 'reviewers'):
        review_mode = False
        if request.user != ct.submission.creator:
            return render_to_response('403.html', {'site': Site.objects.get_current(),},
                            context_instance=RequestContext(request))

    if review_mode:
        can_approve = ct.submission.status == STATUS_PENDING and ct.submission.remark_set.exclude(status='closed').count() == 0
        can_resubmit = ct.submission.status == STATUS_PENDING
        is_ct_author = ct.submission.creator
    else:
        can_approve = False
        can_resubmit = False

    translations = [t for t in ct.translations.all()]
    remark_list = []
    for tf in TRIAL_FORMS:
         remarks = ct.submission.remark_set.filter(context=slugify(tf))
         if remarks:
            remark_list.append(remarks)

    # get translation for recruitment status
    recruitment_status = ct.recruitment_status
    if recruitment_status:
        recruitment_label = recruitment_status.label
        try:
            t = VocabularyTranslation.objects.get_translation_for_object(
                                request.LANGUAGE_CODE.lower(), model=RecruitmentStatus,
                                object_id=recruitment_status.id)
            if t.label:
                recruitment_label = t.label
        except ObjectDoesNotExist:
            pass
    else:
        recruitment_label = ""

    # get translations for recruitment country
    recruitment_country = ct.recruitment_country.all()
    recruitment_country_list = recruitment_country.values('pk', 'description')
    for obj in recruitment_country_list:
        try:
            t = VocabularyTranslation.objects.get_translation_for_object(
                                request.LANGUAGE_CODE.lower(), model=CountryCode,
                                object_id=obj['pk'])
            if t.description:
                obj['description'] = t.description
        except ObjectDoesNotExist:
            pass

    # get translations for scientific contacts country
    scientific_contacts = ct.scientific_contacts()
    scientific_contacts_list = scientific_contacts.values('pk', 'firstname', 'middlename',
                            'lastname', 'address', 'city', 'zip', 'country_id', 'telephone',
                            'email', 'affiliation__name')

    for obj in scientific_contacts_list:
        try:
            country = CountryCode.objects.get(pk=obj['country_id'])
            obj['country_description'] = country.description
        except CountryCode.DoesNotExist:
            obj['country_description'] = ""

        try:
            t = VocabularyTranslation.objects.get_translation_for_object(
                                request.LANGUAGE_CODE.lower(), model=CountryCode,
                                object_id=obj['country_id'])
            if t.description:
                obj['country_description'] = t.description
        except ObjectDoesNotExist:
            pass

    # get translations for public contacts country
    public_contacts = ct.public_contacts()
    public_contacts_list = public_contacts.values('pk', 'firstname', 'middlename',
                            'lastname', 'address', 'city', 'zip', 'country_id', 'telephone',
                            'email', 'affiliation__name')

    for obj in public_contacts_list:
        try:
            country = CountryCode.objects.get(pk=obj['country_id'])
            obj['country_description'] = country.description
        except CountryCode.DoesNotExist:
            obj['country_description'] = ""

        try:
            t = VocabularyTranslation.objects.get_translation_for_object(
                                request.LANGUAGE_CODE.lower(), model=CountryCode,
                                object_id=obj['country_id'])
            if t.description:
                obj['country_description'] = t.description
        except ObjectDoesNotExist:
            pass

    # get translations for site contacts country
    site_contacts = ct.site_contact.all().select_related()
    site_contacts_list = site_contacts.values('pk', 'firstname', 'middlename',
                            'lastname', 'address', 'city', 'zip', 'country_id', 'telephone',
                            'email', 'affiliation__name')

    for obj in site_contacts_list:
        try:
            country = CountryCode.objects.get(pk=obj['country_id'])
            obj['country_description'] = country.description
        except CountryCode.DoesNotExist:
            obj['country_description'] = ""

        try:
            t = VocabularyTranslation.objects.get_translation_for_object(
                                request.LANGUAGE_CODE.lower(), model=CountryCode,
                                object_id=obj['country_id'])
            if t.description:
                obj['country_description'] = t.description
        except ObjectDoesNotExist:
            pass

    enrollment_start_date = ct.enrollment_start_actual if \
        ct.enrollment_start_actual is not None else ct.enrollment_start_planned
    enrollment_end_date = ct.enrollment_end_actual if \
        ct.enrollment_end_actual is not None else ct.enrollment_end_planned

    return render_to_response('repository/clinicaltrial_detail_user.html',
                                {'object': ct,
                                'translations': translations,
                                'host': request.get_host(),
                                'remark_list': remark_list,
                                'review_mode': review_mode,
                                'can_approve': can_approve,
                                'can_resubmit': can_resubmit,
                                'languages': get_sorted_languages(request),
                                'recruitment_label': recruitment_label,
                                'recruitment_country': recruitment_country_list,
                                'scientific_contacts': scientific_contacts_list,
                                'public_contacts': public_contacts_list,
                                'site_contacts': site_contacts_list,
                                'enrollment_start_date': enrollment_start_date,
                                'enrollment_end_date': enrollment_end_date,
                                },
                                context_instance=RequestContext(request))

def get_sorted_languages(request):
    # This just copy managed languages to sorte with main language first
    languages = [lang.lower() for lang in settings.MANAGED_LANGUAGES]
    languages.sort(lambda a,b: -1 if a == request.trials_language else cmp(a,b))
    return languages

def trial_registered(request, trial_fossil_id, trial_version=None):
    ''' show details of a trial registered '''
    try:
        fossil = Fossil.objects.get(pk=trial_fossil_id)
    except Fossil.DoesNotExist:
        try:
            qs = Fossil.objects.indexed(trial_id=trial_fossil_id)
            if trial_version:
                fossil = qs.get(revision_sequential=trial_version)
            else:
                fossil = qs.get(is_most_recent=True)
        except Fossil.DoesNotExist:
            raise Http404

    ct = fossil.get_object_fossil()
    ct.fossil['language'] = ct.fossil.get('language', settings.DEFAULT_SUBMISSION_LANGUAGE)
    ct._language = ct.language
    ct.hash_code = fossil.pk
    ct.previous_revision = fossil.previous_revision
    try:
        ct.previous_revision_sequencial = fossil.previous_revision.revision_sequential
    except:
        ct.previous_revision_sequencial = None

    ct.version = fossil.revision_sequential

    translations = [ct.fossil] # the Fossil dictionary must be one of the translations
    translations.extend(ct.translations)
    try:
        scientific_title = [t['scientific_title'] for t in translations
                if t['language'] == get_language() and t['scientific_title'].strip()][0]
    except IndexError:
        scientific_title = ct.scientific_title

    created = datetime.datetime.strptime(ct.fossil['created'], "%Y-%m-%d %H:%M:%S")

    if len(trial_fossil_id) == 64:
        trial_fossil_id = str(fossil).split(' ')[0]

    trial = get_object_or_404(ClinicalTrial, trial_id=trial_fossil_id)
    attachs = [attach for attach in trial.trial_attach() if attach.public]

    try:
        time_perspective = trial.time_perspective
    except ObjectDoesNotExist:
        time_perspective = None
    observational_study_design = trial.observational_study_design

    return render_to_response('repository/clinicaltrial_detail_published.html',
                                {'object': ct,
                                'attachs': attachs,
                                'translations': translations,
                                'time_perspective':time_perspective,
                                'observational_study_design':observational_study_design,
                                'host': request.get_host(),
                                'fossil_created': created,
                                'register_number': trial_fossil_id,
                                'scientific_title': scientific_title,
                                'languages': get_sorted_languages(request),
                                'outdated_flag':settings.MEDIA_URL + 'media/img/admin/icon_error.gif',
                                },
                                context_instance=RequestContext(request))

@login_required
def new_institution(request):

    if request.method == 'POST':
        new_institution = NewInstitution(request.POST)
        if new_institution.is_valid():
            institution = new_institution.save(commit=False)
            institution.creator = request.user
            institution.save()
            json = serializers.serialize('json',[institution])
            return HttpResponse(json, mimetype='application/json')
        else:
            return HttpResponse(new_institution.as_table(), mimetype='text/html')

    else:
        new_institution = NewInstitution()

    return render_to_response('repository/new_institution.html',
                             {'form':new_institution},
                               context_instance=RequestContext(request))

@login_required
def contacts(request):
    from django import forms

    if request.method == 'POST':
        if request.POST.get('contact') != '-':
            contact = Contact.objects.get(pk=request.POST.get('contact'))
            contact.delete()
            contact.save()

    choices = [('-','-----------')] + [(c.pk, c.name()) for c in Contact.objects.filter(creator=request.user)]
    class ContactsForm(forms.Form):
        contact = forms.ChoiceField(label=_('Contact'),
                                  choices=choices,
                                  )

    form = ContactsForm()

    return render_to_response('repository/delete_contact.html',
                             { 'form':form,
                               'form_title':_('Delete Contact'),
                               'title':_('Delete Contact'),},
                               context_instance=RequestContext(request))


def step_list(trial_pk):
    import sys
    current_step = int( sys._getframe(1).f_code.co_name.replace('step_','') )
    steps = []
    for i in range(1,10):
        steps.append({'link': reverse('step_%d'%i,args=[trial_pk]),
                      'is_current': (i == current_step),
                      'name': MENU_SHORT_TITLE[i-1]})
    return steps

@login_required
@check_user_can_edit_trial
def step_1(request, trial_pk):
    ct = request.ct

    if not request.user.is_staff and not user_in_group(request.user, 'reviewers'):
        if request.user != ct.submission.creator:
            return render_to_response('403.html', {'site': Site.objects.get_current(),},
                            context_instance=RequestContext(request))

    if request.method == 'POST' and request.can_change_trial:
        form = TrialIdentificationForm(request.POST, instance=ct,
                                       display_language=request.user.get_profile().preferred_language)
        SecondaryIdSet = inlineformset_factory(ClinicalTrial, TrialNumber,
                                               form=SecondaryIdForm,
                                               extra=EXTRA_FORMS)
        secondary_forms = SecondaryIdSet(request.POST, instance=ct)

        if form.is_valid() and secondary_forms.is_valid():
            secondary_forms.save()
            form.save()
            return HttpResponseRedirect(reverse('step_1',args=[trial_pk]))
    else:
        form = TrialIdentificationForm(instance=ct,
                                       default_second_language=ct.submission.get_secondary_language(),
                                       display_language=request.user.get_profile().preferred_language,
                                       )
        SecondaryIdSet = inlineformset_factory(ClinicalTrial, TrialNumber,
                                               form=SecondaryIdForm,
                                               extra=EXTRA_FORMS, can_delete=True)
        secondary_forms = SecondaryIdSet(instance=ct)

    forms = [form]
    formsets = [secondary_forms]
    return render_to_response('repository/trial_form.html',
                              {'forms':forms,'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[0],
                               'steps': step_list(trial_pk),
                               'remarks':Remark.status_open.filter(submission=ct.submission,context=slugify(TRIAL_FORMS[0])),
                               'default_second_language': ct.submission.get_secondary_language(),
                               'available_languages': [lang.lower() for lang in ct.submission.get_mandatory_languages()],
                               },
                               context_instance=RequestContext(request))


@login_required
@check_user_can_edit_trial
def step_2(request, trial_pk):
    ct = request.ct

    if not request.user.is_staff and not user_in_group(request.user, 'reviewers'):
        if request.user != ct.submission.creator:
            return render_to_response('403.html', {'site': Site.objects.get_current(),},
                            context_instance=RequestContext(request))

    qs_primary_sponsor = Institution.objects.filter(creator=request.user).order_by('name')

    if request.method == 'POST' and request.can_change_trial:
        form = PrimarySponsorForm(request.POST, instance=ct, queryset=qs_primary_sponsor,
                                  display_language=request.user.get_profile().preferred_language)
        SecondarySponsorSet = inlineformset_factory(ClinicalTrial, TrialSecondarySponsor,
                           form=make_secondary_sponsor_form(request.user),extra=EXTRA_FORMS)
        SupportSourceSet = inlineformset_factory(ClinicalTrial, TrialSupportSource,
                           form=make_support_source_form(request.user),extra=EXTRA_FORMS)

        secondary_forms = SecondarySponsorSet(request.POST, instance=ct)
        sources_form = SupportSourceSet(request.POST, instance=ct)

        if form.is_valid() and secondary_forms.is_valid() and sources_form.is_valid():
            secondary_forms.save()
            sources_form.save()
            form.save()
        return HttpResponseRedirect(reverse('step_2',args=[trial_pk]))
    else:
        form = PrimarySponsorForm(instance=ct, queryset=qs_primary_sponsor,
                                  default_second_language=ct.submission.get_secondary_language(),
                                  display_language=request.user.get_profile().preferred_language)
        SecondarySponsorSet = inlineformset_factory(ClinicalTrial, TrialSecondarySponsor,
            form=make_secondary_sponsor_form(request.user),extra=EXTRA_FORMS, can_delete=True)
        SupportSourceSet = inlineformset_factory(ClinicalTrial, TrialSupportSource,
               form=make_support_source_form(request.user),extra=EXTRA_FORMS,can_delete=True)

        secondary_forms = SecondarySponsorSet(instance=ct)
        sources_form = SupportSourceSet(instance=ct)

    forms = [form]
    formsets = [secondary_forms,sources_form]
    return render_to_response('repository/step_2.html',
                              {'forms':forms,'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[1],
                               'steps': step_list(trial_pk),
                               'remarks':Remark.status_open.filter(submission=ct.submission,context=slugify(TRIAL_FORMS[1])),
                               'default_second_language': ct.submission.get_secondary_language(),
                               'available_languages': [lang.lower() for lang in ct.submission.get_mandatory_languages()],},
                               context_instance=RequestContext(request))


@login_required
@check_user_can_edit_trial
def step_3(request, trial_pk):
    ct = request.ct

    if not request.user.is_staff and not user_in_group(request.user, 'reviewers'):
        if request.user != ct.submission.creator:
            return render_to_response('403.html', {'site': Site.objects.get_current(),},
                            context_instance=RequestContext(request))

    GeneralDescriptorSet = modelformset_factory(Descriptor,
                                                formset=MultilingualBaseFormSet,
                                                form=GeneralHealthDescriptorForm,
                                                can_delete=True,
                                                extra=EXTRA_FORMS,
                                                extra_formset_attrs={
                                                    'default_second_language':ct.submission.get_secondary_language(),
                                                    'available_languages':[lang.lower() for lang in ct.submission.get_mandatory_languages()],
                                                    'display_language':request.user.get_profile().preferred_language,
                                                    },
                                                )

    SpecificDescriptorSet = modelformset_factory(Descriptor,
                                                formset=MultilingualBaseFormSet,
                                                form=SpecificHealthDescriptorForm,
                                                can_delete=True,
                                                extra=EXTRA_FORMS,
                                                extra_formset_attrs={
                                                    'default_second_language':ct.submission.get_secondary_language(),
                                                    'available_languages':[lang.lower() for lang in ct.submission.get_mandatory_languages()],
                                                    'display_language':request.user.get_profile().preferred_language,
                                                    },
                                                )

    general_qs = Descriptor.objects.filter(trial=trial_pk,
                                           aspect=choices.TRIAL_ASPECT[0][0],
                                           level=choices.DESCRIPTOR_LEVEL[0][0])

    specific_qs = Descriptor.objects.filter(trial=trial_pk,
                                           aspect=choices.TRIAL_ASPECT[0][0],
                                           level=choices.DESCRIPTOR_LEVEL[1][0])

    if request.method == 'POST' and request.can_change_trial:
        form = HealthConditionsForm(request.POST, instance=ct,
                                    display_language=request.user.get_profile().preferred_language)
        general_desc_formset = GeneralDescriptorSet(request.POST,queryset=general_qs,prefix='g')
        specific_desc_formset = SpecificDescriptorSet(request.POST,queryset=specific_qs,prefix='s')

        if form.is_valid() and general_desc_formset.is_valid() and specific_desc_formset.is_valid():
            descriptors = general_desc_formset.save(commit=False)
            descriptors += specific_desc_formset.save(commit=False)


            for descriptor in descriptors:
                descriptor.trial = ct

            general_desc_formset.save()
            specific_desc_formset.save()
            form.save()

            return HttpResponseRedirect(reverse('step_3',args=[trial_pk]))
    else:
        form = HealthConditionsForm(instance=ct,
                                    default_second_language=ct.submission.get_secondary_language(),
                                    display_language=request.user.get_profile().preferred_language)
        general_desc_formset = GeneralDescriptorSet(queryset=general_qs,prefix='g')
        specific_desc_formset = SpecificDescriptorSet(queryset=specific_qs,prefix='s')


    forms = [form]
    formsets = [general_desc_formset, specific_desc_formset]
    return render_to_response('repository/step_3.html',
                              {'forms':forms,'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[2],
                               'steps': step_list(trial_pk),
                               'remarks':Remark.status_open.filter(submission=ct.submission,context=slugify(TRIAL_FORMS[2])),
                               'default_second_language': ct.submission.get_secondary_language(),
                               'available_languages': [lang.lower() for lang in ct.submission.get_mandatory_languages()],},
                               context_instance=RequestContext(request))


@login_required
@check_user_can_edit_trial
def step_4(request, trial_pk):
    ct = request.ct

    if not request.user.is_staff and not user_in_group(request.user, 'reviewers'):
        if request.user != ct.submission.creator:
            return render_to_response('403.html', {'site': Site.objects.get_current(),},
                            context_instance=RequestContext(request))

    DescriptorFormSet = modelformset_factory(Descriptor,
                                          formset=MultilingualBaseFormSet,
                                          form=InterventionDescriptorForm,
                                          can_delete=True,
                                          extra=EXTRA_FORMS,
                                          extra_formset_attrs={
                                            'default_second_language':ct.submission.get_secondary_language(),
                                            'available_languages':[lang.lower() for lang in ct.submission.get_mandatory_languages()],
                                            'display_language':request.user.get_profile().preferred_language,
                                            },
                                          )

    queryset = Descriptor.objects.filter(trial=trial_pk,
                                           aspect=choices.TRIAL_ASPECT[1][0],
                                           level=choices.DESCRIPTOR_LEVEL[0][0])
    if request.method == 'POST' and request.can_change_trial:
        form = InterventionForm(request.POST, instance=ct,
                                display_language=request.user.get_profile().preferred_language)
        specific_desc_formset = DescriptorFormSet(request.POST, queryset=queryset)

        if form.is_valid() and specific_desc_formset.is_valid():
            descriptors = specific_desc_formset.save(commit=False)


            for descriptor in descriptors:
                descriptor.trial = ct

            specific_desc_formset.save()
            form.save()
            return HttpResponseRedirect(reverse('step_4',args=[trial_pk]))
    else:
        form = InterventionForm(instance=ct,
                                default_second_language=ct.submission.get_secondary_language(),
                                display_language=request.trials_language)
        specific_desc_formset = DescriptorFormSet(queryset=queryset)

    forms = [form]
    formsets = [specific_desc_formset]
    return render_to_response('repository/step_4.html',
                              {'forms':forms,'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[3],
                               'steps': step_list(trial_pk),
                               'remarks':Remark.status_open.filter(submission=ct.submission,context=slugify(TRIAL_FORMS[3])),
                               'default_second_language': ct.submission.get_secondary_language(),
                               'available_languages': [lang.lower() for lang in ct.submission.get_mandatory_languages()],},
                               context_instance=RequestContext(request))


@login_required
@check_user_can_edit_trial
def step_5(request, trial_pk):
    ct = request.ct

    if not request.user.is_staff and not user_in_group(request.user, 'reviewers'):
        if request.user != ct.submission.creator:
            return render_to_response('403.html', {'site': Site.objects.get_current(),},
                            context_instance=RequestContext(request))

    if request.method == 'POST' and request.can_change_trial:
        form = RecruitmentForm(request.POST, instance=ct,
                               display_language=request.user.get_profile().preferred_language)

        if form.is_valid():
            form.save()
            ct.outdated = is_outdate(ct)
            ct.save()
            return HttpResponseRedirect(reverse('step_5',args=[trial_pk]))
    else:
        form = RecruitmentForm(instance=ct,
                               default_second_language=ct.submission.get_secondary_language(),
                               display_language=request.trials_language)

    forms = [form]

    return render_to_response('repository/trial_form.html',
                              {'forms':forms,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[4],
                               'steps': step_list(trial_pk),
                               'remarks':Remark.status_open.filter(submission=ct.submission,context=slugify(TRIAL_FORMS[4])),
                               'default_second_language': ct.submission.get_secondary_language(),
                               'available_languages': [lang.lower() for lang in ct.submission.get_mandatory_languages()],
                               },
                               context_instance=RequestContext(request))


@login_required
@check_user_can_edit_trial
def step_6(request, trial_pk):
    ct = request.ct

    if not request.user.is_staff and not user_in_group(request.user, 'reviewers'):
        if request.user != ct.submission.creator:
            return render_to_response('403.html', {'site': Site.objects.get_current(),},
                            context_instance=RequestContext(request))

    if request.method == 'POST' and request.can_change_trial:
        form = StudyTypeForm(request.POST, instance=ct,
                             display_language=request.user.get_profile().preferred_language)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('step_6',args=[trial_pk]))
    else:
        form = StudyTypeForm(instance=ct,
                             default_second_language=ct.submission.get_secondary_language(),
                             display_language=request.trials_language)

    forms = [form]
    return render_to_response('repository/trial_form.html',
                              {'forms':forms,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[5],
                               'steps': step_list(trial_pk),
                               'remarks':Remark.status_open.filter(submission=ct.submission,context=slugify(TRIAL_FORMS[5])),
                               'default_second_language': ct.submission.get_secondary_language(),
                               'available_languages': [lang.lower() for lang in ct.submission.get_mandatory_languages()],},
                               context_instance=RequestContext(request))


@login_required
@check_user_can_edit_trial
def step_7(request, trial_pk):
    ct = request.ct

    if not request.user.is_staff and not user_in_group(request.user, 'reviewers'):
        if request.user != ct.submission.creator:
            return render_to_response('403.html', {'site': Site.objects.get_current(),},
                            context_instance=RequestContext(request))

    PrimaryOutcomesSet = modelformset_factory( Outcome,
                                formset=MultilingualBaseFormSet,
                                form=PrimaryOutcomesForm,extra=EXTRA_FORMS,
                                can_delete=True,
                                extra_formset_attrs={
                                    'default_second_language':ct.submission.get_secondary_language(),
                                    'available_languages':[lang.lower() for lang in ct.submission.get_mandatory_languages()],
                                    'display_language':request.trials_language
                                    },
                                )
    SecondaryOutcomesSet = modelformset_factory(Outcome,
                                formset=MultilingualBaseFormSet,
                                form=SecondaryOutcomesForm,extra=EXTRA_FORMS,
                                can_delete=True,
                                extra_formset_attrs={
                                    'default_second_language':ct.submission.get_secondary_language(),
                                    'available_languages':[lang.lower() for lang in ct.submission.get_mandatory_languages()],
                                    'display_language':request.user.get_profile().preferred_language,
                                    },
                                )

    primary_qs = Outcome.objects.filter(trial=ct, interest=choices.OUTCOME_INTEREST[0][0])
    secondary_qs = Outcome.objects.filter(trial=ct, interest=choices.OUTCOME_INTEREST[1][0])

    if request.method == 'POST' and request.can_change_trial:
        primary_outcomes_formset = PrimaryOutcomesSet(request.POST, queryset=primary_qs, prefix='primary')
        secondary_outcomes_formset = SecondaryOutcomesSet(request.POST, queryset=secondary_qs, prefix='secondary')

        if primary_outcomes_formset.is_valid() and secondary_outcomes_formset.is_valid():
            outcomes = primary_outcomes_formset.save(commit=False)
            outcomes += secondary_outcomes_formset.save(commit=False)

            for outcome in outcomes:
                outcome.trial = ct

            primary_outcomes_formset.save()
            secondary_outcomes_formset.save()

            # Executes validation of current trial submission (for mandatory fields)
            trial_validator.validate(ct)

            return HttpResponseRedirect(reverse('step_7',args=[trial_pk]))
    else:
        primary_outcomes_formset = PrimaryOutcomesSet(queryset=primary_qs, prefix='primary')
        secondary_outcomes_formset = SecondaryOutcomesSet(queryset=secondary_qs, prefix='secondary')

    formsets = [primary_outcomes_formset,secondary_outcomes_formset]
    return render_to_response('repository/trial_form.html',
                              {'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[6],
                               'steps': step_list(trial_pk),
                               'remarks':Remark.status_open.filter(submission=ct.submission,context=slugify(TRIAL_FORMS[6])),
                               'default_second_language': ct.submission.get_secondary_language(),
                               'available_languages': [lang.lower() for lang in ct.submission.get_mandatory_languages()],},
                               context_instance=RequestContext(request))


@login_required
@check_user_can_edit_trial
def step_8(request, trial_pk):
    ct = request.ct

    if not request.user.is_staff and not user_in_group(request.user, 'reviewers'):
        if request.user != ct.submission.creator:
            return render_to_response('403.html', {'site': Site.objects.get_current(),},
                            context_instance=RequestContext(request))

    contact_type = {
        'PublicContact': (PublicContact,make_public_contact_form(request.user)),
        'ScientificContact': (ScientificContact,make_scientifc_contact_form(request.user)),
        'SiteContact': (SiteContact,make_site_contact_form(request.user))
    }

    InlineFormSetClasses = []
    for model,form in contact_type.values():
        InlineFormSetClasses.append(
            inlineformset_factory(ClinicalTrial,model,form=form,can_delete=True,extra=EXTRA_FORMS)
        )

    ContactFormSet = modelformset_factory(Contact,
                                          form=make_contact_form(request.user,formset_prefix='new_contact'),
                                          extra=1)

    contact_qs = Contact.objects.none()

    if request.method == 'POST' and request.can_change_trial:
        inlineformsets = [fs(request.POST,instance=ct) for fs in InlineFormSetClasses]
        new_contact_formset = ContactFormSet(request.POST,queryset=contact_qs,prefix='new_contact')

        if not False in [fs.is_valid() for fs in inlineformsets] \
                and new_contact_formset.is_valid():

            for contactform in new_contact_formset.forms:
                if contactform.cleaned_data:
                    Relation = contact_type[contactform.cleaned_data.pop('relation')][0]
                    new_contact = contactform.save(commit=False)
                    new_contact.creator = request.user
                    new_contact.save()
                    Relation.objects.create(trial=ct,contact=new_contact)

            for fs in inlineformsets:
                fs.save()

            # Executes validation of current trial submission (for mandatory fields)
            trial_validator.validate(ct)

            return HttpResponseRedirect(reverse('step_8',args=[trial_pk]))
    else:
        inlineformsets = [fs(instance=ct) for fs in InlineFormSetClasses]
        new_contact_formset = ContactFormSet(queryset=contact_qs,prefix='new_contact')

    formsets = inlineformsets + [new_contact_formset]
    return render_to_response('repository/step_8.html',
                              {'formsets':formsets,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[7],
                               'steps': step_list(trial_pk),
                               'remarks':Remark.status_open.filter(submission=ct.submission,context=slugify(TRIAL_FORMS[7])),
                               'default_second_language': ct.submission.get_secondary_language(),
                               'available_languages': [lang.lower() for lang in ct.submission.get_mandatory_languages()],},
                               context_instance=RequestContext(request))

@login_required
@check_user_can_edit_trial
def step_9(request, trial_pk):
    # TODO: this function should be on another place
    ct = request.ct

    if not request.user.is_staff and not user_in_group(request.user, 'reviewers'):
        if request.user != ct.submission.creator:
            return render_to_response('403.html', {'site': Site.objects.get_current(),},
                            context_instance=RequestContext(request))

    su = Submission.objects.get(trial=ct)

    NewAttachmentFormSet = modelformset_factory(Attachment,
                                             extra=1,
                                             can_delete=False,
                                             form=NewAttachmentForm)

    existing_attachments = Attachment.objects.filter(submission=su)

    if request.method == 'POST' and request.can_change_trial:

        if 'remove' in request.POST:
            attach = Attachment.objects.get(id=request.POST.get('remove'))
            attach.delete()

            return HttpResponseRedirect(reverse('step_9',args=[trial_pk]))

        else:
            new_attachment_formset = NewAttachmentFormSet(request.POST,
                                                          request.FILES,
                                                          prefix='new')

            if new_attachment_formset.is_valid():
                new_attachments = new_attachment_formset.save(commit=False)

                for attachment in new_attachments:
                    attachment.submission = su

                new_attachment_formset.save()
                return HttpResponseRedirect(reverse('step_9',args=[trial_pk]))

    else:
        new_attachment_formset = NewAttachmentFormSet(queryset=Attachment.objects.none(),
                                                      prefix='new')

    formsets = [new_attachment_formset]

    return render_to_response('repository/attachments.html',
                              {'formsets':formsets,
                               'existing_attachments':existing_attachments,
                               'trial_pk':trial_pk,
                               'title':TRIAL_FORMS[8],
                               'host': request.get_host(),
                               'steps': step_list(trial_pk),
                               'remarks':Remark.status_open.filter(submission=ct.submission,context=slugify(TRIAL_FORMS[8])),
                               'default_second_language': ct.submission.get_secondary_language(),
                               'available_languages': [lang.lower() for lang in ct.submission.get_mandatory_languages()],},
                               context_instance=RequestContext(request))

from repository.xml.generate import xml_ictrp, xml_opentrials

def trial_ictrp(request, trial_fossil_id, trial_version=None):
    """
    Returns a XML content structured on ICTRP standard, you can find more details
    about it on:

    - http://reddes.bvsalud.org/projects/clinical-trials/wiki/RegistrationDataModel
    - http://reddes.bvsalud.org/projects/clinical-trials/attachment/wiki/RegistrationDataModel/who_ictrp_dtd.txt
    - http://reddes.bvsalud.org/projects/clinical-trials/attachment/wiki/RegistrationDataModel/ICTRP%20Data%20format%201.1%20.doc
    - http://reddes.bvsalud.org/projects/clinical-trials/attachment/wiki/RegistrationDataModel/xmlsample.xml
    - http://reddes.bvsalud.org/projects/clinical-trials/attachment/wiki/RegistrationDataModel/ICTRPTrials.xml
    """

    try:
        fossil = Fossil.objects.get(pk=trial_fossil_id)
    except Fossil.DoesNotExist:
        try:
            qs = Fossil.objects.indexed(trial_id=trial_fossil_id)
            if trial_version:
                fossil = qs.get(revision_sequential=trial_version)
            else:
                fossil = qs.get(is_most_recent=True)
        except Fossil.DoesNotExist:
            raise Http404

    ct = fossil.get_object_fossil()
    xml = xml_ictrp([fossil])

    resp = HttpResponse(xml,
            mimetype = 'text/xml'
            )

    resp['Content-Disposition'] = 'attachment; filename=%s-ictrp.xml' % ct.trial_id

    return resp

def all_trials_ictrp(request):

    trials = ClinicalTrial.fossils.published()
    xml = xml_ictrp(trials)

    resp = HttpResponse(xml,
            mimetype = 'text/xml'
            )

    resp['Content-Disposition'] = 'attachment; filename=%s-ictrp.xml' % settings.TRIAL_ID_PREFIX

    return resp

def trial_otxml(request, trial_id, trial_version=None):
    """
    Returns a XML content structured on OpenTrials standard, you can find more details
    about it on:

    - ToDo
    """

    try:
        fossil = Fossil.objects.get(pk=trial_id)
    except Fossil.DoesNotExist:
        try:
            qs = Fossil.objects.indexed(trial_id=trial_id)
            if trial_version:
                fossil = qs.get(revision_sequential=trial_version)
            else:
                fossil = qs.get(is_most_recent=True)
        except Fossil.DoesNotExist:
            raise Http404

    ct = fossil.get_object_fossil()
    ct.hash_code = fossil.pk
    ct.previous_revision = fossil.previous_revision
    ct.version = fossil.revision_sequential
    ct.status = fossil.indexers.key('status', fail_silent=True).value

    xml = xml_opentrials([ct])

    resp = HttpResponse(xml,
            mimetype = 'text/xml'
            )

    resp['Content-Disposition'] = 'attachment; filename=%s-ot.xml' % ct.trial_id

    return resp

def multi_otxml(request):
    trial_id_list = request.GET.getlist('trial_id')
    if not trial_id_list:
        return HttpResponse(status=205)

    ct_list = []

    for trial_id in trial_id_list:
        try:
            fossil = Fossil.objects.get(pk=trial_id)
        except Fossil.DoesNotExist:
            try:
                qs = Fossil.objects.indexed(trial_id=trial_id)
                fossil = qs.get(is_most_recent=True)
            except Fossil.DoesNotExist:
                raise Http404

        ct = fossil.get_object_fossil()
        ct.hash_code = fossil.pk
        ct.previous_revision = fossil.previous_revision
        ct.version = fossil.revision_sequential
        ct.status = fossil.indexers.key('status', fail_silent=True).value

        ct_list.append(ct)

    xml = xml_opentrials(ct_list)

    resp = HttpResponse(xml,
            mimetype = 'text/xml'
            )

    today = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')
    resp['Content-Disposition'] = 'attachment; filename=%s-ot.xml' % today

    return resp

def custom_otcsv(request):
    allsubmissions = Submission.objects.all()
    allsubmissions_list = allsubmissions.values('pk','trial_id','created','updated','creator','title','status')

    today = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')

    filename = "CustomCSV_OT_%s" % today

    output = cStringIO.StringIO() ## temp output csv file
    writer = csv.writer(output)

    writer.writerow(['trial','created','updated','status','creator','title'])

    for submission in allsubmissions_list:
        title = smart_str(submission['title'])
        login_creator = User.objects.get(pk=submission['creator'])

        try:
            trial_id = ClinicalTrial.objects.get(pk=submission['trial_id'])
            trial_id = str(trial_id).split(' ')[0]
        except:
            trial_id = "no_id"

        writer.writerow([trial_id,submission['created'],submission['updated'],submission['status'],login_creator,title])

    response = HttpResponse(mimetype='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % filename

    zipped_file = ZipFile(response, 'w', ZIP_DEFLATED)

    csv_name = '%s.csv' % filename
    zipped_file.writestr(csv_name, output.getvalue())

    return response

def advanced_search(request):
    q = request.GET.get('q', '').strip()
    rec_status = request.GET.getlist('rec_status')
    rec_country = request.GET.get('rec_country', '').strip()
    is_observational = request.GET.getlist('is_observ')
    i_type = request.GET.getlist('i_type')
    gender = request.GET.get('gender', '').strip()
    minimum_age = request.GET.get('age_min','').strip()
    maximum_age = request.GET.get('age_max','').strip()
    minimum_age_unit = request.GET.get('age_min_unit','').strip()
    maximum_age_unit = request.GET.get('age_max_unit','').strip()

    recruitment_country_list = localized_vocabulary(CountryCode, request.LANGUAGE_CODE.lower())
    recruitment_status_list = localized_vocabulary(RecruitmentStatus, request.LANGUAGE_CODE.lower())
    institution_type_list = localized_vocabulary(InstitutionType, request.LANGUAGE_CODE.lower())

    return render_to_response('repository/advanced_search.html',
                              {'rec_countries':recruitment_country_list,
                               'rec_status':recruitment_status_list,
                               'i_type':institution_type_list,
                               'q':q,
                               'age_min': minimum_age,
                               'age_max': maximum_age,
                               'search_filters':{'rec_status':rec_status,
                                                 'rec_country':rec_country,
                                                 'is_observ':is_observational,
                                                 'i_type': i_type,
                                                 'gender':gender,
                                                 'minimum_age':minimum_age,
                                                 'maximum_age':maximum_age,
                                                 'minimum_age_unit':minimum_age_unit,
                                                 'maximum_age_unit':maximum_age_unit,                                               },
                              },
                              context_instance=RequestContext(request))
