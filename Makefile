VERSION ?= 0.0.1
PREFIX ?= /usr/local

MAN_DIR   = "${DESTDIR}/${PREFIX}/share/man/man1"
DOC_DIR   = "${DESTDIR}/${PREFIX}/share/doc/tem"
SHARE_DIR = "${DESTDIR}/${PREFIX}/share/tem"

install: install-base
	@# Man page and other documentation
	@cd docs; "${MAKE}" man
	mkdir -p ${MAN_DIR} \
			 ${DOC_DIR}
	install -Dm444 docs/_build/man/*.1 	${MAN_DIR}
	install -Dm444 LICENSE 				${DOC_DIR}
	@# tuterm tutorial files
	install -Dm644 docs/demo/tem    	${DESTDIR}/${PREFIX}/share/tuterm/scripts/tem
	cp -r 		   docs/demo/.tem-home  ${DESTDIR}/${PREFIX}/share/tuterm/scripts/.tem-home
	chmod 755 ${DESTDIR}/${PREFIX}/share/tuterm/scripts/.tem-home

# Install without documentation files
install-base:
	@echo "__prefix__ = '/${PREFIX}'" | sed 's://:/:' > tem/_meta.py
	@echo "__version__ = '${VERSION}'" >> tem/_meta.py
	python3 setup.py install --root="${DESTDIR}/" --prefix="${PREFIX}"
	@# Restore tem/_meta.py to the version from git
	@if which git >/dev/null 2>&1; then git restore -- tem/_meta.py; fi
	@mkdir -p 	${SHARE_DIR}		\
  				${SHARE_DIR}/hooks	\
			 	${SHARE_DIR}/env	\
			 	${DESTDIR}/${PREFIX}/share/tuterm/scripts
	install -Dm644 conf/config  		${SHARE_DIR}/
	install -Dm644 conf/ignore  		${SHARE_DIR}/
	install -Dm644 conf/repo    		${SHARE_DIR}/
	install -Dm744 conf/hooks/* 		${SHARE_DIR}/hooks/
	install -Dm744 conf/env/* 			${SHARE_DIR}/env/

uninstall:
	rm -rf ${SHARE_DIR} ${DOC_DIR} \
		   ${DESTDIR}/${PREFIX}/bin/tem \
		   ${DESTDIR}/${PREFIX}/lib/python3.*/site-packages/tem \
		   ${DESTDIR}/${PREFIX}/share/tuterm/scripts/tem \
		   ${DESTDIR}/${PREFIX}/share/tuterm/scripts/.tem-home

test:
	cd tests; ${MAKE} test

test-pip:
	cd tests; ${MAKE} test-pip

clean:
	rm -rf build dist tem.egg-info
	rm -rf __pycache__ */__pycache__
	cd docs;  ${MAKE} clean
	cd tests; ${MAKE} clean
