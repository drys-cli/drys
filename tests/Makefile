BATS = bats --formatter pretty --timing

# ../tem.py uses this variable
export TEM_EXECUTABLE = $(shell realpath ../tem.py)
export HOME = $(shell pwd)

test:
	@${BATS} test_help.bats
	@${BATS} test_config.bats
	@${BATS} test_ls.bats
	@${BATS} test_repo.bats
	@${BATS} test_add.bats
	@${BATS} test_put.bats
	@${BATS} test_env.bats
	@${BATS} test_git.bats

test-pip:
	pipenv install
	pipenv run "${MAKE}" test

clean:
	rm -rf _out/
