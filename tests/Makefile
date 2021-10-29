BATS = bats --formatter pretty --timing

# ../tem.py uses this variable
export PROJECT_ROOT   	= $(shell realpath ../)
export HOME             = $(shell pwd)/_out
export DEFAULT_REPO     = ${HOME}/.local/share/tem/repo
export PATH             = $(shell echo "$$PWD/path:$$PATH")

.PHONY: all put ls add repo config env git test-pip clean

all:
	@# Some redundancy for increased safety when dealing with HOME
	@if [ "$$HOME" != "$(shell pwd)/_out" ]; then\
		echo "Wrongly configured HOME variable";\
		exit 1;\
	fi

	@rm -rf $(shell pwd)/_out/.config
	@${BATS} tem.bats
	@${BATS} put.bats
	@${BATS} ls.bats
	@${BATS} add.bats
	@${BATS} repo.bats
	@${BATS} config.bats
	@${BATS} env.bats
	@${BATS} var.bats
	# FIXME Fails when run as a pre-commit hook
	{ [ -z "$$SKIP_GIT" ] && ${BATS} git.bats; } || true

put:
	@${BATS} put.bats
ls:
	@${BATS} ls.bats
add:
	@${BATS} add.bats
repo:
	@${BATS} repo.bats
config:
	@${BATS} config.bats
env:
	@${BATS} env.bats
var:
	@${BATS} var.bats
git:
	@${BATS} git.bats

test-pip:
	pipenv install
	pipenv run "${MAKE}" all

clean:
	rm -rf _out/
