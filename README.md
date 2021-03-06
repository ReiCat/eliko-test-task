# eliko-test-task

1. Create database & user with password

`$ sudo -u postgres psql`

`postgres=# create database eliko;`

`postgres=# create user eliko with encrypted password 'eliko';`

`postgres=# grant all privileges on database eliko to eliko;`

2. Create virtual environment for the project
* It is assumed you have virtualenv installed globally

`$ virtualenv -p python3 venv`

3. Activate it

`$ source venv/bin/activate`

4. Install all the requirements

`$ pip install -r requirements.txt`

5. Create .env file and add database dsn 

`$ touch .env && echo "DATABASE_URL=postgresql://eliko:eliko@localhost:5432/eliko" >> .env`

6. Run migrations 

`$ make migrate-up`

7. Run the script

`$ make run path=data/example_data.txt`