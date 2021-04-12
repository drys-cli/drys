BATS = bats --pretty
EXE := drys

export EXE

tests:
	@${BATS} test_help.bats
	@${BATS} test_add_ls_put.bats

clean:
	rm -rf _out/
