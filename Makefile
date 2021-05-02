PREFIX ?= /usr/local

install:
	python3 setup.py install --root="$(DESTDIR)/" --prefix="$(PREFIX)"
	install -Dm644 conf/config $(DESTDIR)/$(PREFIX)/share/drys/config

test:
	cd tests; ${MAKE} test

clean:
	rm -rf build drys.egg-info
	rm -rf */__pycache__
	cd tests; ${MAKE} clean
	cd pkg;   ${MAKE} clean
