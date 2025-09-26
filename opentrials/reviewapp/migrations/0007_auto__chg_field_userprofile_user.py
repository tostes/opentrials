# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'UserProfile.user'
        db.alter_column('reviewapp_userprofile', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True))


    def backwards(self, orm):
        
        # Changing field 'UserProfile.user'
        db.alter_column('reviewapp_userprofile', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True))


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'repository.clinicaltrial': {
            'Meta': {'ordering': "['-updated']", 'object_name': 'ClinicalTrial'},
            '_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'acronym_expansion': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'agemax_unit': ('django.db.models.fields.CharField', [], {'default': "'-'", 'max_length': '1'}),
            'agemax_value': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True'}),
            'agemin_unit': ('django.db.models.fields.CharField', [], {'default': "'-'", 'max_length': '1'}),
            'agemin_value': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True'}),
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.StudyAllocation']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_registration': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'enrollment_end_actual': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'enrollment_end_planned': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'enrollment_start_actual': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'enrollment_start_planned': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'exclusion_criteria': ('django.db.models.fields.TextField', [], {'max_length': '8000', 'blank': 'True'}),
            'expanded_access_program': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'exported': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'-'", 'max_length': '1'}),
            'hc_freetext': ('django.db.models.fields.TextField', [], {'max_length': '8000', 'blank': 'True'}),
            'i_code': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['vocabulary.InterventionCode']", 'symmetrical': 'False'}),
            'i_freetext': ('django.db.models.fields.TextField', [], {'max_length': '8000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inclusion_criteria': ('django.db.models.fields.TextField', [], {'max_length': '8000', 'blank': 'True'}),
            'intervention_assignment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.InterventionAssigment']", 'null': 'True', 'blank': 'True'}),
            'is_observational': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "u'en'", 'max_length': '10'}),
            'masking': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.StudyMasking']", 'null': 'True', 'blank': 'True'}),
            'number_of_arms': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'observational_study_design': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.ObservationalStudyDesign']", 'null': 'True', 'blank': 'True'}),
            'phase': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.StudyPhase']", 'null': 'True', 'blank': 'True'}),
            'primary_sponsor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.Institution']", 'null': 'True', 'blank': 'True'}),
            'public_contact': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'public_contact_of_set'", 'symmetrical': 'False', 'through': "orm['repository.PublicContact']", 'to': "orm['repository.Contact']"}),
            'public_title': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'purpose': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.StudyPurpose']", 'null': 'True', 'blank': 'True'}),
            'recruitment_country': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['vocabulary.CountryCode']", 'symmetrical': 'False'}),
            'recruitment_status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.RecruitmentStatus']", 'null': 'True', 'blank': 'True'}),
            'scientific_acronym': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'scientific_acronym_expansion': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'scientific_contact': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'scientific_contact_of_set'", 'symmetrical': 'False', 'through': "orm['repository.ScientificContact']", 'to': "orm['repository.Contact']"}),
            'scientific_title': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'site_contact': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'site_contact_of_set'", 'symmetrical': 'False', 'through': "orm['repository.SiteContact']", 'to': "orm['repository.Contact']"}),
            'staff_note': ('django.db.models.fields.CharField', [], {'max_length': "'255'", 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'processing'", 'max_length': '64'}),
            'study_design': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'}),
            'study_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.StudyType']", 'null': 'True', 'blank': 'True'}),
            'target_sample_size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'time_perspective': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.TimePerspective']", 'null': 'True', 'blank': 'True'}),
            'trial_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True', 'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'utrn_number': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'repository.clinicaltrialtranslation': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'language'),)", 'object_name': 'ClinicalTrialTranslation'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'acronym_expansion': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'exclusion_criteria': ('django.db.models.fields.TextField', [], {'max_length': '8000', 'blank': 'True'}),
            'hc_freetext': ('django.db.models.fields.TextField', [], {'max_length': '8000', 'blank': 'True'}),
            'i_freetext': ('django.db.models.fields.TextField', [], {'max_length': '8000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inclusion_criteria': ('django.db.models.fields.TextField', [], {'max_length': '8000', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '8', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'public_title': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'scientific_acronym': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'scientific_acronym_expansion': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'scientific_title': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'study_design': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'blank': 'True'})
        },
        'repository.contact': {
            'Meta': {'object_name': 'Contact'},
            '_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'affiliation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.Institution']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.CountryCode']", 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'contact_creator'", 'to': "orm['auth.User']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '255'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'middlename': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'telephone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'repository.institution': {
            'Meta': {'object_name': 'Institution'},
            '_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {'max_length': '1500', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.CountryCode']"}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'institution_creator'", 'to': "orm['auth.User']"}),
            'i_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vocabulary.InstitutionType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'repository.publiccontact': {
            'Meta': {'unique_together': "(('trial', 'contact'),)", 'object_name': 'PublicContact'},
            '_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.Contact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Active'", 'max_length': '255'}),
            'trial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.ClinicalTrial']"})
        },
        'repository.scientificcontact': {
            'Meta': {'unique_together': "(('trial', 'contact'),)", 'object_name': 'ScientificContact'},
            '_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.Contact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Active'", 'max_length': '255'}),
            'trial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.ClinicalTrial']"})
        },
        'repository.sitecontact': {
            'Meta': {'unique_together': "(('trial', 'contact'),)", 'object_name': 'SiteContact'},
            '_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.Contact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'Active'", 'max_length': '255'}),
            'trial': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.ClinicalTrial']"})
        },
        'reviewapp.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'attach_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '8000', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '250'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reviewapp.Submission']"})
        },
        'reviewapp.news': {
            'Meta': {'object_name': 'News'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'news_creator'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '16'}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '2048'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'reviewapp.newstranslation': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'language'),)", 'object_name': 'NewsTranslation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '8', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '2048'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'reviewapp.recruitmentcountry': {
            'Meta': {'object_name': 'RecruitmentCountry'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submissionrecruitmentcountry_set'", 'to': "orm['vocabulary.CountryCode']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reviewapp.Submission']"})
        },
        'reviewapp.remark': {
            'Meta': {'object_name': 'Remark'},
            'context': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'open'", 'max_length': '16'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['reviewapp.Submission']"}),
            'text': ('django.db.models.fields.TextField', [], {'max_length': '2048'})
        },
        'reviewapp.submission': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Submission'},
            '_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submission_creator'", 'to': "orm['auth.User']"}),
            'fields_status': ('django.db.models.fields.TextField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "u'en'", 'max_length': '10'}),
            'primary_sponsor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.Institution']", 'null': 'True', 'blank': 'True'}),
            'staff_note': ('django.db.models.fields.TextField', [], {'max_length': '255', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'draft'", 'max_length': '64'}),
            'title': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'trial': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['repository.ClinicalTrial']", 'unique': 'True', 'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'updater': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submission_updater'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'reviewapp.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preferred_language': ('django.db.models.fields.CharField', [], {'default': "u'pt-br'", 'max_length': '10'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'vocabulary.countrycode': {
            'Meta': {'ordering': "['description']", 'object_name': 'CountryCode'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'submission_language': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'vocabulary.institutiontype': {
            'Meta': {'ordering': "['order']", 'object_name': 'InstitutionType'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.interventionassigment': {
            'Meta': {'ordering': "['order']", 'object_name': 'InterventionAssigment'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.interventioncode': {
            'Meta': {'ordering': "['order']", 'object_name': 'InterventionCode'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.observationalstudydesign': {
            'Meta': {'ordering': "['order']", 'object_name': 'ObservationalStudyDesign'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.recruitmentstatus': {
            'Meta': {'object_name': 'RecruitmentStatus'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.studyallocation': {
            'Meta': {'ordering': "['order']", 'object_name': 'StudyAllocation'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.studymasking': {
            'Meta': {'ordering': "['order']", 'object_name': 'StudyMasking'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.studyphase': {
            'Meta': {'ordering': "['order']", 'object_name': 'StudyPhase'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.studypurpose': {
            'Meta': {'ordering': "['order']", 'object_name': 'StudyPurpose'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.studytype': {
            'Meta': {'ordering': "['order']", 'object_name': 'StudyType'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.timeperspective': {
            'Meta': {'ordering': "['order']", 'object_name': 'TimePerspective'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'vocabulary.vocabularytranslation': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'language'),)", 'object_name': 'VocabularyTranslation'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '8', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['reviewapp']
