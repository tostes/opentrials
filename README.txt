This is the Clinical Trials Registration System developed by BIREME/PAHO/WHO
with the Brazilian Ministry of Health (Ministério da Saúde/DECIT), Fiocruz 
(Fundação Oswaldo Cruz/ICICT) and the Pan American Health Organization
(PAHO/WHO).

The project Web site, documentation wiki and issue tracker are at:

http://reddes.bvsalud.org/projects/clinical-trials

The main Subversion repository is at:

http://svn.reddes.bvsalud.org/clinical-trials

There is also a git-svn mirror at:

http://github.com/bireme/opentrials


Dependencies
------------

The project targets Python 3.10+ and Django 4.2.  The ``requirements.txt``
file lists the Python packages that need to be installed in order to run the
project and to bootstrap the Django site successfully.

OS dependencies (Ubuntu)
~~~~~~~~~~~~~~~~~~~~~~~~

The following packages cover the native dependencies required by the Python
libraries listed above:

sudo apt-get install build-essential python3-dev libxml2-dev libxslt1-dev
sudo apt-get install apache2 libapache2-mod-wsgi-py3
sudo apt-get install default-mysql-server default-libmysqlclient-dev


Third-party Django apps
~~~~~~~~~~~~~~~~~~~~~~~

``INSTALLED_APPS`` references a couple of reusable Django applications that
are not part of this repository.  They are mapped below to the packages that
need to be present in your virtual environment:

=====================  ======================
``INSTALLED_APPS``     PyPI package
=====================  ======================
``compressor``         ``django-compressor``
``haystack``           ``django-haystack``
``rosetta``            ``django-rosetta``
=====================  ======================

The ``registration`` entry is shipped as part of this repository (a local
fork of ``django-registration``) and therefore does not require an external
dependency.

The ``requirements.txt`` file pins versions of these packages that are known
to work with Django 4.2.


Installation
------------

We recommend working inside a virtual environment:

    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip

Install the Python dependencies:

    pip install -r requirements.txt

If some package is already installed globally, make sure it matches the
version constraints in ``requirements.txt``; otherwise, reinstall it inside
the virtual environment.

Legacy documentation describing the original Subversion-based deployment is
available at:

    http://reddes.bvsalud.org/projects/clinical-trials/wiki/HowToInstall


Local configuration
-------------------

The default settings now ship with a safe SQLite database that lives inside
the project tree.  This allows the test suite or ad-hoc development servers to
run without any additional configuration.  To override these defaults create a
``settings_local.py`` module (or reuse the legacy ``settings_local.include``)
alongside ``opentrials/settings.py``.  The
``opentrials/settings_local.include-SAMPLE`` file documents the options that a
deployment typically needs to provide.

During startup the project will also ensure that the
``static/attachments`` directory exists.  Confirm that the account running the
application can write to that directory so user uploads continue to work in
production environments.


virtualenv/setuptools
---------------------

A way to install easilly a development/production environment is working with Virtualenv.

To install it you just have to run the following commands:

    virtualenv --distribute --no-site-packages dev
    source dev/bin/activate

The following command will install all dependencies you need:

    $ python setup.py install

If some package wasn't installed properly, check one of those situations:

- Setuptools will install only packages that aren't
  already installed in your default Python library path;
- Maybe some package is a new version with backward incompatibilities that are
  conflicting with what we need.

So, if you face one of above situations, please contact us so we can write it in
our documentation.



