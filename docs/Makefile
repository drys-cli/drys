
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

all: man html

.PHONY: help man html

html:
	@${SPHINXBUILD} -M $@ "${SOURCEDIR}" "${BUILDDIR}" ${SPHINXOPTS} ${O}
man:
	@${SPHINXBUILD} -M $@ "${SOURCEDIR}/man" "${BUILDDIR}" ${SPHINXOPTS} ${O}
	@# Replace <...> generic options with italic text
	@sed -i 's:<\([A-Z]\+\)>:\\fI\1\\fR\\fR:g' "${BUILDDIR}/man"/*.1

# Tweak manpage sources for inclusion in the HTML version of the docs.
# A NAME section containing the description is added to each manpage source file.
# The reason why the NAME section is excluded from the source files in the first
# place is because `sphinx-build -M man` automatically creates that section.
prepare-man: man
	@echo Converting manpages back to rst...
	@mkdir -p _intermediate/man
	@for file in man/tem*.rst; do \
		man/prepare-man.sh "$$file" _intermediate/man; \
	done

clean:
	rm -rf "${BUILDDIR}"
	rm -rf _intermediate/
