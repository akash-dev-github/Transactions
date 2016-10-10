A simple accounts-transactions setup.

Setup:

The following setup is done on ubuntu 14.04 but should work with later version as well. For OS X just use the
corresponding commands respectively.

As for any django project, to setup Transactions project we need to work at three fronts:

    actual code base
    OS level requirements
    python specific dependencies

1> actual code base:
Just clone this repo to get the complete code required to run the app. The details of using it will be covered in the next
section once the setup is done.

2: OS level requirements: At the OS level we need to take care of two things:
a> Libraries required: For this just run the following command in your terminal to install from the Ubuntu Repositories:
sudo apt-get update
sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib

b> Database setup:
Now we need to create the DB to be used by our django app.
By default, Django applications are configured to store data into a lightweight SQLite database file.
While this works well for dev setup it is always best to have the same database as in production.
If you wish to use SQLite skip further steps in this section and just change the DATABASE settings to:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

With the first step we have already installed postgres. During the Postgres installation, an operating system user named postgres was created to correspond to the
postgres PostgreSQL administrative user. We need to change to this user to perform administrative tasks:

        sudo su - postgres

Now create the database you wish to use for the project. We will call it 'django_db' in this guide:

    CREATE DATABASE django_db;

Next, we will create a database user which we will use to connect to and interact with the database.
Set the password to something strong and secure:

CREATE USER myprojectuser WITH PASSWORD 'password';

Afterwards, we'll modify a few of the connection parameters for the user we just created. This will speed up database operations so that the correct values do not have to be queried and set each time a connection is established.

We are setting the default encoding to UTF-8, which Django expects. We are also setting the default transaction isolation scheme to "read committed", which blocks reads from uncommitted transactions.
Lastly, we are setting the timezone. By default, our Django projects will be set to use UTC:

ALTER ROLE myprojectuser SET client_encoding TO 'utf8';
ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE myprojectuser SET timezone TO 'UTC';

Now, all we need to do is give our database user access rights to the database we created:

GRANT ALL PRIVILEGES ON DATABASE django_db TO myprojectuser;

Exit the SQL prompt to get back to the postgres user's shell session:

\q

Exit out of the postgres user's shell session to get back to your regular user's shell session:

exit


3: python specific dependencies

For better flexibility, we will install Django and all of its dependencies within a Python virtual environment.
You can get the virtualenv package that allows you to create these environments by typing:

    sudo pip install virtualenv

We can create a virtual environment to store our Django project's Python requirements by typing:

    virtualenv myprojectenv

This will install a local copy of Python and pip into a directory called myprojectenv within your project directory.
Before we install applications within the virtual environment, we need to activate it. You can do so by typing:

    source myprojectenv/bin/activate

Your prompt will change to indicate that you are now operating within the virtual environment.
It will look something like this (myprojectenv)user@host:~/myproject$

Once virtualenv is created and active you can install all python packages for the project using:
    pip install -r requirements.pip

If you wish to see what packages are being used just use:

    pip freeze

After adding any new package ensure an update to the requirements file:

    pip freeze > requirements.pip

Now that the database, code and environment is setup, this is the right time to create your tables.
Ensure the database settings in settings.py file contains the correct values as setup by you above:

python manage.py makemigrations
python manage.py migrate

Your tables should be created now.



API Usage:

Now that we are setup, lets see how we can use the APIs exposed by the project.
Firstly, a note on authentication used for the project.

Authentication for the API:

Authentication for the project is done as an independent OAuth capable Token based authorization server powered by
DOT (Django OAuth Toolkit). Following setting informs django to use our new authentication backend:
    REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    )
}

To obtain a valid access_token first we must register an application. Just point your browser at:
http://localhost:8000/accounts/oauth/applications/

Click on the link to create a new application and fill the form with the following data:

Name: just a name of your choice
Client Type: confidential
Authorization Grant Type: Resource owner password-based
Save your app!

At this point we’re ready to request an access_token. Open your terminal and curl:

    curl -X POST -d "grant_type=password&username=<user_name>&password=<password>" -u"<client_id>:<client_secret>" http://localhost:8000/o/token/

The user_name and password are the credential of the users for which access token is required. Response should be something like:

{
    "access_token": "<your_access_token>",
    "token_type": "Bearer",
    "expires_in": 36000,
    "refresh_token": "<your_refresh_token>",
    "scope": "read write groups"
}

Grab your access_token and you can use it as follows:

curl -H "Authorization: Bearer <your_access_token>" <API URL>

For further info check out DOT Documentation:
    https://django-oauth-toolkit.readthedocs.io/en/latest/index.html



# Style Guide:

Tool used For Style Guide Enforcement: Flake8
PEP8 conformed.











