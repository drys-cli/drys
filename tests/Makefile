BATS = bats --formatter pretty --timing
EXE := drys

export EXE

tests:
	@${BATS} test_help.bats
	@${BATS} test_add.bats
	@${BATS} test_ls.bats

clean:
	rm -rf _out/
