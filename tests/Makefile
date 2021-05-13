BATS = bats --formatter pretty --timing
EXE ?= $(realpath ../tem.py)

export EXE

test:
	@${BATS} test_help.bats
	@${BATS} test_config.bats
	@${BATS} test_ls.bats
	@${BATS} test_repo.bats
	@${BATS} test_add.bats
	@${BATS} test_put.bats
	@${BATS} test_env.bats

test-pip:
	pipenv install
	pipenv run "${MAKE}" test

clean:
	rm -rf _out/
