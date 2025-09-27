# OpenTrials NG

This directory contains a fresh Django 4.x implementation of the OpenTrials
registry.  The new project keeps the legacy data model and business rules in a
modern code base so that the clinical trial registry can evolve independently
from the original Python 2 / Django 1 stack.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The default settings use SQLite for local development.  Controlled vocabularies
can be managed from the Django admin after creating a superuser.
