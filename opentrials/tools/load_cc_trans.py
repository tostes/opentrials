#!/usr/bin/env python3

'''
Load translations for country names by country code
'''

############# spells to setup the django machinery
import os
import sys
from pathlib import Path

import django

here = Path(__file__).resolve().parent
project_root = here.parent
repo_root = project_root.parent

for path in {project_root, repo_root}:
    str_path = str(path)
    if str_path not in sys.path:
        sys.path.append(str_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opentrials.settings')
django.setup()
############# /spells

from vocabulary.models import CountryCode, VocabularyTranslation

for language in ('pt', 'es'):
    print(f'loading {language}', end=' ')
    filename = here / f'countries_{language}.txt'

    unknown = []
    with filename.open('r', encoding='utf-8') as lines:
        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            cc, name = line.split(None, 1)
            try:
                country = CountryCode.objects.get(label=cc)
            except CountryCode.DoesNotExist:
                unknown.append(cc)
                continue
            translation = VocabularyTranslation(language=language, label=cc, description=name)
            country.translations.add(translation)
    if unknown:
        print(f'*** unknown: {unknown}')
    print('done')
