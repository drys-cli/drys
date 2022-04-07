VERSION ?= 0.0.1
PREFIX ?= /usr/local

MAN_DIR   = "${DESTDIR}/${PREFIX}/share/man/man1"
DOC_DIR   = "${DESTDIR}/${PREFIX}/share/doc/tem"
SHARE_DIR = "${DESTDIR}/${PREFIX}/share/tem"

build: build-base
	"${MAKE}" -C docs

build-base:
	mkdir -p build/lib/tem
	@echo "__version__ = '${VERSION}'"               > build/lib/tem/_meta.py

install: install-base
	@# Man page and other documentation
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
	@echo "__prefix__ = '/${PREFIX}'" | sed 's://:/:' >> build/lib/tem/_meta.py
	pip install --root="${DESTDIR}/" --prefix="${PREFIX}" .
	@# Set the current user and group as owners of build/
	@chown -R "$$(stat -c '%U' .)" build tem.egg-info tem/__pycache__ || true
	@chgrp -R "$$(stat -c '%G' .)" build tem.egg-info tem/__pycache__ || true
	@mkdir -p 	${SHARE_DIR}		\
  				${SHARE_DIR}/hooks	\
			 	${SHARE_DIR}/env	\
			 	${DESTDIR}/${PREFIX}/share/tuterm/scripts
	install -Dm644 share/config     ${SHARE_DIR}/
	install -Dm644 share/ignore     ${SHARE_DIR}/
	install -Dm644 share/repo       ${SHARE_DIR}/
	install -Dm744 share/hooks/*    ${SHARE_DIR}/hooks/
	install -Dm744 share/env/*      ${SHARE_DIR}/env/
	@rm -rf tem.egg-info

uninstall:
	rm -rf ${SHARE_DIR} ${DOC_DIR} \
		   ${DESTDIR}/${PREFIX}/bin/tem \
		   ${DESTDIR}/${PREFIX}/lib/python3.*/site-packages/tem \
		   ${DESTDIR}/${PREFIX}/share/tuterm/scripts/tem \
		   ${DESTDIR}/${PREFIX}/share/tuterm/scripts/.tem-home

test:
	@"${MAKE}" -C tests docker-all

clean:
	rm -rf build dist tem.egg-info
	rm -rf __pycache__ */__pycache__
	cd docs;  ${MAKE} clean
	cd tests; ${MAKE} clean

# Build official docker images for various distros
docker:
	base=archlinux shdocker -o docker/archlinux
