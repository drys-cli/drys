
export ACTUAL_HOME    ?= $(shell echo $$HOME)
export TEM_PROJECTROOT = $(shell realpath ../)
export TESTS           = $(shell realpath ./)

ifdef __TEM_TESTS_INSIDE_DOCKER_CONTAINER__
	# We are currently inside a docker container
    export OUTDIR   = /t
else
	# We are not inside a docker container
    export OUTDIR   = ${TESTS}/_out
endif
export HOME         = ${OUTDIR}
export PATH         = $(shell echo "${TESTS}/cli/path:$$PATH")
export DEFAULT_REPO = ${HOME}/.local/share/tem/repo

PIPENV_RUN = cd "${TEM_PROJECTROOT}" && HOME="${ACTUAL_HOME}" pipenv run
BATS = "${TESTS}"/bats

.PHONY: all cli py clean \
	    put ls add repo config env var find git \
		_cli _py _protections

docker-all:
	@echo "\033[1;34mDocker: Building tem:develop image...\033[0m"
	@docker build -t tem:develop "${TEM_PROJECTROOT}"
	@echo "\033[1;34mDocker: Building tem-tests image...\033[0m"
	@docker build -t tem-tests "${TESTS}"
	@docker run -a stdout -it tem-tests "${MAKE}" all

all: _protections
	@"${MAKE}" py
	@"${MAKE}" cli

cli: _protections
	@${PIPENV_RUN} "${MAKE}" -C "${TESTS}" _cli

py: _protections
	${PIPENV_RUN} python --version
	@${PIPENV_RUN} "${MAKE}" -C "${TESTS}" _py

# Tests for individual subcommands
put: _protections
	@${BATS} put
ls: _protections
	@${BATS} ls
add: _protections
	@${BATS} add
repo: _protections
	@${BATS} repo
config: _protections
	@${BATS} config
env: _protections
	@${BATS} env
var: _protections
	@${BATS} var
find: _protections
	@${BATS} find
git: _protections
	@${BATS} git

clean:
	rm -rf "${OUTDIR}"

_cli: _protections
	@rm -rf "${OUTDIR}/.config"
	@${BATS} tem
	@${BATS} put
	@${BATS} ls
	@${BATS} add
	@${BATS} repo
	@${BATS} config
	@${BATS} env
	@${BATS} var
	@${BATS} find
	@${BATS} git

_py: _protections
	@export PYTHONPATH="${TEM_PROJECTROOT}" \
		&& pytest "${TESTS}/py" -s

# Some redundancy to avoid making a mess of your system
# If you make any changes to this target, verify that they work inside the
# container first.
_protections:
	@# For increased safety when dealing with HOME
	@if [ "$$(realpath "$$HOME")" != "$$(realpath "${OUTDIR}")" ]; then\
		echo "Wrongly configured HOME variable";\
		exit 1;\
	fi
