PREFIX ?= /usr/local

__INIT__ = "$$(ls "${DESTDIR}/${PREFIX}"/lib/python3*/site-packages/tem/__init__.py)"

MAN_DIR = "${DESTDIR}/${PREFIX}/share/man/man1"
DOC_DIR = "${DESTDIR}/${PREFIX}/share/doc/tem"

install:
	@[ -f ${__INIT__} ] && rm -f ${__INIT__} || true
	python3 setup.py install --root="${DESTDIR}/" --prefix="${PREFIX}"
	@echo "__prefix__ = '/${PREFIX}'" >> ${__INIT__}
	install -Dm644 conf/config "${DESTDIR}/${PREFIX}/share/tem/config"
	@cd docs; "${MAKE}" man
	mkdir -p ${MAN_DIR} ${DOC_DIR}
	install -Dm444 docs/_build/man/*.1  ${MAN_DIR}
	install -Dm444 LICENSE ${DOC_DIR}

test:
	cd tests; ${MAKE} test

test-pip:
	cd tests; ${MAKE} test-pip

clean:
	rm -rf build tem.egg-info
	rm -rf */__pycache__
	cd docs;  ${MAKE} clean
	cd tests; ${MAKE} clean
	cd pkg;   ${MAKE} clean
