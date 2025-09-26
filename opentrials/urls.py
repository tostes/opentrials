# -*- encoding: utf-8 -*-

# OpenTrials: a clinical trials registration system
#
# Copyright (C) 2010 BIREME/PAHO/WHO, ICICT/Fiocruz e
#                    Ministério da Saúde do Brasil
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from registration.forms import RegistrationFormUniqueEmail
from registration.views import register

import utilities

from django.contrib import admin # Django admin UI
admin.autodiscover()             # Django admin UI

urlpatterns = [
    # Repository application
    path('rg/', include('opentrials.repository.urls')),

    # Tickets application
    path('ticket/', include('opentrials.tickets.urls')),

    # Assistance application
    path('assistance/', include('opentrials.assistance.urls')),

    # Review application
    path('', include('opentrials.reviewapp.urls')),

    # Django admin UI and documentation
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),

    path('decs/', include('opentrials.decsclient.urls')),

    path('icd10/', include('opentrials.icd10client.urls')),

    # setting django-registration to use unique email form
    path(
        'accounts/register/',
        register,
        {
            'backend': 'registration.backends.default.DefaultBackend',
            'form_class': RegistrationFormUniqueEmail,
        },
        name='registration_register'
    ),

    # django-registration views
    path('accounts/', include('registration.urls')),

    # system diagnostic views (may be disabled in production)
    path('diag/', include('opentrials.diagnostic.urls')),

    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    # serve static files from development server
    urlpatterns += static('static/', document_root=settings.MEDIA_ROOT)

    # Serve static XML files, specially DTD for XML references
    import os
    import repository

    REPOSITORY_XML_ROOT = os.path.join(os.path.dirname(repository.__file__), 'xml')
    urlpatterns += static('xml/', document_root=REPOSITORY_XML_ROOT)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls')),
    ]

