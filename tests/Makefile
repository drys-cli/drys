BATS = bats --formatter pretty --timing
EXE := ../drys.py

export EXE

tests:
	@${BATS} test_help.bats
	@${BATS} test_add.bats
	@${BATS} test_ls.bats
	@${BATS} test_config.bats

clean:
	rm -rf _out/
