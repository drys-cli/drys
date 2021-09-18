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
	@${BATS} test_tem.bats
	@${BATS} test_put.bats
	@${BATS} test_ls.bats
	@${BATS} test_add.bats
	@${BATS} test_repo.bats
	@${BATS} test_config.bats
	@${BATS} test_env.bats
	@${BATS} test_git.bats

put:
	@${BATS} test_put.bats
ls:
	@${BATS} test_ls.bats
add:
	@${BATS} test_add.bats
repo:
	@${BATS} test_repo.bats
config:
	@${BATS} test_config.bats
env:
	@${BATS} test_env.bats
git:
	@${BATS} test_git.bats

test-pip:
	pipenv install
	pipenv run "${MAKE}" test

clean:
	rm -rf _out/
