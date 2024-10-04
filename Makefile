# systems this Makefile has been tested against (GNU make btw)
# macOS 14, M1 Mac, brew installed jq, awscli, uv, node. python 3.x installed via download.

#
# precondition section for this Makefile to work
#

# we need to have a standard set of binaries available (installed out of band)
EXECUTABLES = uv npx npm aws jq
K := $(foreach exec,$(EXECUTABLES), $(if $(shell which $(exec)),some string,$(error "No $(exec) in PATH")))

#
# DRY names for folders etc
#

TALLY_FOLDER = tally-lambda
DEPLOY_FOLDER = deploy
DOCKER_IMAGE_NAME = variant-tally

# note where Python is used in CDK lambdas there is also a version specified in the Construct to edit!
PYTHON_VERSION = 3.12

#
# by default we do everything to set up for running any of the backends
#

all: setup-${TALLY_FOLDER}

setup-${TALLY_FOLDER}: ${TALLY_FOLDER}/.venv/lib

.PHONY: all setup-${TALLY_FOLDER}

#
# the actual targets that should be targeted for deployments
#

deploy-umccr: setup-${TALLY_FOLDER}
	cd deploy; npx cdk deploy

.PHONY: deploy-umccr

#
# clean up working folders
#

clean: clean-python

clean-python:
	cd ${TALLY_FOLDER}; find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete; rm -rf .venv/

clean-deploy:
	cd ${DEPLOY_FOLDER}; rm -rf node_modules/ cdk.out/

.PHONY: clean clean-front-end clean-python

# actual rules that create files/folders and build things

${TALLY_FOLDER}/.venv/lib: ${TALLY_FOLDER}/requirements.txt
	cd ${TALLY_FOLDER}; uv venv -p ${PYTHON_VERSION} .venv; . .venv/bin/activate; uv pip install -r requirements.txt

${TALLY_FOLDER}/requirements.txt: ${TALLY_FOLDER}/requirements.in
	cd ${TALLY_FOLDER}; uv pip compile requirements.in --generate-hashes -o requirements.txt
