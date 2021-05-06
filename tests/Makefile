BATS = bats --formatter pretty --timing
EXE := $(realpath ../drys.py)

export EXE

test:
	@${BATS} test_help.bats
	@${BATS} test_config.bats
	@${BATS} test_ls.bats
	@${BATS} test_repo.bats
	@${BATS} test_add.bats
	@${BATS} test_put.bats

clean:
	rm -rf _out/
