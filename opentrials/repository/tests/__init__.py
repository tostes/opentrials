#coding: utf-8

# FIXME: It seems it is with something missing from fixtures

"""
from django.test.client import Client
from django.test import TestCase

from repository.models import *

class SecondaryNumbers(TestCase):
    fixtures = ['first_3_trials.json']

    def setUp(self):
        title = 'Comparison of Ascorbic Acid and Grape Seed'
        self.asc_trial = ClinicalTrial.objects.get(
            public_title__istartswith=title)

    def test_short_title(self):
        start = 'Effect of Ascorbic Acid'
        self.assertTrue(self.asc_trial.short_title().startswith(start))

    def test_secondary_numbers(self):
        self.assertEquals(len(self.asc_trial.trialnumber_set.all()), 2)

    def test_public_contacts(self):
        contacts = list(self.asc_trial.public_contacts())
        self.assertEquals(len(contacts), 1)
        self.assertEquals(contacts[0].firstname, 'Naser')

    def test_scientific_contacts(self):
        contacts = list(self.asc_trial.scientific_contacts())
        self.assertEquals(len(contacts), 1)
        self.assertEquals(contacts[0].firstname, 'Naser')

class Step3Test(TestCase):
    fixtures = ['first_3_trials.json']

    def setUp(self):
        self.client = Client()
        self.trial = ClinicalTrial.objects.get(pk=1)

    def test_submit(self):
        self.client.login(username='admin',password='123456')
        response = self.client.post('/rg/step_3/1/',{
                'hc_freetext': 'test text to step 3',
                'hc_freetext|pt-br': '',
                'hc_freetext|es': '',
                'g-TOTAL_FORMS': 1, 
                'g-INITIAL_FORMS': 0,
                'g-0-vocabulary': 'DeCS',
                'g-0-code': 'C02',
                'g-0-text': 'Virus diseases',
                'g-0-text|pt-br': 'Viroses',
                'g-0-text|es': 'Virosis',
                's-TOTAL_FORMS': 1, 
                's-INITIAL_FORMS': 0,
                's-0-vocabulary': 'DeCS',
                's-0-code': 'C03.752.530',
                's-0-text': 'Malaria',
                's-0-text|pt-br': 'Malária',
                's-0-text|es': 'Malaria',
            })
        self.failUnlessEqual(response.status_code, 200)
"""

