#!/usr/bin/env python3

import sys
from importlib import import_module
from pathlib import Path

here = Path(__file__).resolve().parent
project_root = here.parent
repo_root = project_root.parent

for path in {project_root, repo_root}:
    str_path = str(path)
    if str_path not in sys.path:
        sys.path.append(str_path)

INSTALLED_APPS = import_module('opentrials.settings').INSTALLED_APPS

print('rm -rf rebec-2011-12-13')
print('mkdir rebec-2011-12-13')
for app in INSTALLED_APPS:
    if app.startswith('django.contrib.'):
        short_app = app.replace('django.contrib.', '')
    else:
        short_app = app
    cmd = './manage.py dumpdata -n %s --indent=2 > rebec-2011-12-13/%s-2011-12-13.json'
    print(cmd % (short_app, app))
