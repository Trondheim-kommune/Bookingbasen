How to run
----------

1. Create a new virtualenv (virtualenv venv)
2. source venv/bin/activate
3. pip install -r requirements.txt
4. python app.py


Installation on ubuntu 13.10
----------------------------

1. sudo sh -c "echo 'deb http://apt.postgresql.org/pub/repos/apt/ saucy-pgdg main' > /etc/apt/sources.list.d/pgdg.list"
2. sudo apt-get install postgresql-9.3
3. sudo apt-get install postgresql-9.3-postgis-2.1
4. sudo apt-get install postgresql-contrib
5. Create a database and enable the postgis and hstore extensions:
create extension postgis;
create extension hstore;

