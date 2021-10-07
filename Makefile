# Read .env file
ifneq (,$(wildcard ./.env))
    include ./.env
    export
endif

VENV_PATH?=./venv
PYTHON=${VENV_PATH}/bin/python3

run: 
	${PYTHON} main.py --path $(path)

migration:
	@migrate create --path migrations $(name)

migrate-up: 
	@migrate up --url $(DATABASE_URL) --path migrations

migrate-down: 
	@migrate down 1 --url $(DATABASE_URL) --path migrations