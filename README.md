# eliko-test-task

1. Create database & user with password

sudo -u postgres psql
postgres=# create database eliko;
postgres=# create user eliko with encrypted password 'eliko';
postgres=# grant all privileges on database eliko to eliko;

2. Create virtual environment for the project
* It is assumed you have virtualenv installed globally

$ virtualenv -p python3 venv

3. Run migrations 

$ make migrate-up

4. Run tests to ensure everything works as expected

$ make test

5. Run the script

$ make run