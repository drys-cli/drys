PREFIX ?= /usr/local

__INIT__ = "$$(ls "${DESTDIR}/${PREFIX}"/lib/python3*/site-packages/drys/__init__.py)"

install:
	@[ -f ${__INIT__} ] && rm -f ${__INIT__}
	python3 setup.py install --root="${DESTDIR}/" --prefix="${PREFIX}"
	@echo "__prefix__ = '/${PREFIX}'" >> ${__INIT__}
	install -Dm644 conf/config ${DESTDIR}/${PREFIX}/share/drys/config

test:
	cd tests; ${MAKE} test

clean:
	rm -rf build drys.egg-info
	rm -rf */__pycache__
	cd tests; ${MAKE} clean
	cd pkg;   ${MAKE} clean
