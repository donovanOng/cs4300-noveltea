# CS4300 SP 2018 - NovelTea

## Notes
This is a simplified README to get you started on your local host.

This guide will be utilizing `PostgreSQL` to drive persistent storage on the backend.

### Get PyPI

This guide depends on you being able to easily download Python modules.  In order to do so, you should get `PyPI`.  Follow the basic guide [here](https://pip.pypa.io/en/stable/installing/).

### Virtualenv - The Key to Python Projects

To create, activate and enter the virtual environment, run the following:

```bash
virtualenv venv
source venv/bin/activate
```

Run the following on downloading and using the Python project:

```bash
pip install -r requirements.txt
```

### Database Setup

Once you have `Postgres` setup and running, and have your `$PATH` configured accordingly, run the following:

```bash
# Enter postgres command line interface
$ psql
# Create your database
CREATE DATABASE noveltea_db;
# Quit out
\q
```

Set your enivronment variables:

```bash
# Set the environment type of the app (see config.py)
export APP_SETTINGS=config.DevelopmentConfig
# Set the DB url to a local database for development
export DATABASE_URL=postgresql://localhost/noveltea_db
```

Run the following commands to create the Tea table:

``` bash
# Initialize migrations
python manage.py db init
# Create a migration
python manage.py db migrate
# Apply it to the DB
python manage.py db upgrade
```

### Add data to database

Run the commands to add the Tea data from `/data/scraper/clean_data.csv` to the database:

``` bash
python populatedb.py
```

### Running the app

Now, at the root of your application, you can run:

``` bash
python app.py
```

Your server is now running!