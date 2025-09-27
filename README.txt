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

OS dependencies (Ubuntu)
~~~~~~~~~~~~~~~~~~~~~~~~

sudo apt-get install build-essential python2.6-dev libxml2-dev libxslt1-dev
sudo apt-get install apache2 libapache2-mod-wsgi
sudo apt-get install mysql-server-5.1 libmysqlclient-dev

Python libraries
~~~~~~~~~~~~~~~~

- Python 2.4 or higher. Preference for 2.6
- Django 1.2 or higher
- Some of database wrappers, like psycopg2 or MySQLDb
- Python Imaging Library ( http://www.pythonware.com/products/pil/ )
- south
- BeautifulSoup
- mysql-python
- lxml
- Markdown
- django-registration ( http://bitbucket.org/bireme/django-registration )
- django_compressor
- django-nose
- django-rosetta
- django-reversion
- django-plus
- django-fossil

We suggest you read a more detailed page at:

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



