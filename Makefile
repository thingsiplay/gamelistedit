SHELL = /bin/bash

.PHONY: doc ui

CPWD := $(shell pwd)
CPWD := $(shell realpath "${CPWD}")
APPDIR := app
MODULESDIR := modules
IMGDIR := img
APPNAME := $(shell python3 -m ${MODULESDIR}.meta name)
APPTITLE := $(shell python3 -m ${MODULESDIR}.meta title)
VERSION := $(shell python3 -m ${MODULESDIR}.meta version)
PROJECTDIR := $(shell realpath "./${APPNAME}.py")
PROJECTDIR := $(shell dirname "${PROJECTDIR}")
RUNSCRIPT := ${APPNAME}
DISTNAME := ${APPNAME}-${VERSION}
DISTPATH := ./${DISTNAME}
INSTALLSCRIPT := install.sh
UNINSTALLSCRIPT := uninstall.sh
DESKTOPFILE := ${APPNAME}.desktop
DESKTOPFILEALT := ${APPNAME}-alt.desktop
# CAREFUL: sudo rm -r INSTALLDIR
INSTALLDIR := /opt/${APPNAME}
INSTALLLINKDIR := /usr/local/bin/${APPNAME}
INSTALLDESKTOPDIR := $$HOME/.local/share/applications
APPICON := ${IMGDIR}/icon.svg

.DEFAULT_GOAL := default

default: test doc ui tags

all: test cleaner dist pack

help:
	@echo "${APPNAME} v${VERSION} Makefile arguments:"
	@echo
	@echo "help         show this help message"
	@echo "test         check if few dependency stuff are installed and working"
	@echo
	@echo "all:         build everything, from document to release packages"
	@echo "dist:        build the standalone binary bundle"
	@echo "pack:        create archives for release"
	@echo "install:     installs dist build and symbolic link to system"
	@echo "uninstall:   removes installation from system"
	@echo "clean:       delete temporary files"
	@echo "cleaner:     clean, plus delete additional created files"
	@echo
	@echo "default:     without arguments converts README and generate ui code"

test:
	test $(shell uname) = 'Linux'
	test "${PROJECTDIR}" = "${CPWD}"
	test -f "./${APPNAME}.py"
	test -d "./${MODULESDIR}"
	python3 -c "import PyQt5"
	python3 -c "import xmltodict"
	command -v pyuic5
	command -v pandoc
	command -v pyinstaller

testdist:
	test -f "${DISTPATH}/${APPDIR}/${APPNAME}"

ui: "${MODULESDIR}/${APPNAME}_ui.py"

doc: README.html

tags:
	ctags -R .

scripts: "${RUNSCRIPT}" "${INSTALLSCRIPT}" "${UNINSTALLSCRIPT}" "${DESKTOPFILE}" "${DESKTOPFILEALT}"

distfolder:
	-mkdir -p "${DISTPATH}"

dist: distfolder doc ui scripts
	pyinstaller --clean --noconfirm --distpath "${DISTPATH}" --name "${APPDIR}" "${APPNAME}.py"
	mv "${DISTPATH}/${APPDIR}/${APPDIR}" "${DISTPATH}/${APPDIR}/${APPNAME}"
	cp -r "${IMGDIR}" "${DISTPATH}/${APPDIR}/"
	cp README.html "${DISTPATH}/${APPDIR}/"
	cp LICENSE "${DISTPATH}/${APPDIR}/"
	cp "${RUNSCRIPT}" "${DISTPATH}/"
	cp "${INSTALLSCRIPT}" "${DISTPATH}/"
	cp "${UNINSTALLSCRIPT}" "${DISTPATH}/"
	cp "${UNINSTALLSCRIPT}" "${DISTPATH}/${APPDIR}/"
	cp "${DESKTOPFILE}" "${DISTPATH}/${APPDIR}/"
	cp "${DESKTOPFILEALT}" "${DISTPATH}/${APPDIR}/"

pack: packpy packdist

packpy: distfolder doc ui
	tar -czvf "${DISTNAME}.tar.gz" \
	--exclude="${MODULESDIR}/${APPNAME}.ui" \
	--exclude="${MODULESDIR}/__pycache__" \
	"${MODULESDIR}/" "${IMGDIR}/" "README.html" "LICENSE" "${APPNAME}.py"
	mv "${DISTNAME}.tar.gz" "${DISTPATH}/"

packdist: distfolder dist
	cd "${DISTPATH}" && \
	tar -czvf "${DISTNAME}-Linux-64Bit.tar.gz" \
	"${RUNSCRIPT}" "${INSTALLSCRIPT}" "${UNINSTALLSCRIPT}" ${APPDIR} && \
	cd "${CPWD}"

install: testdist uninstall
	cd "${DISTPATH}" && \
	"./${INSTALLSCRIPT}" && \
	cd "${CPWD}"

uninstall:
	cd "${DISTPATH}" && \
	"./${UNINSTALLSCRIPT}" && \
	cd "${CPWD}"

clean:
	-rm -rf __pycache__
	-rm -rf modules/__pycache__
	-rm -f *.pyc
	-rm -f modules/*.pyc
	-rm -f *.spec
	-rm -rf build
	-rm -f "${RUNSCRIPT}"
	-rm -f "${INSTALLSCRIPT}"
	-rm -f "${UNINSTALLSCRIPT}"
	-rm -f "${DESKTOPFILE}"
	-rm -f "${DESKTOPFILEALT}"
	-rm -r tags

cleaner: clean
	-rm -f README.html
	-rm -f "${MODULESDIR}/${APPNAME}_ui.py"
	-rm -rf "${DISTPATH}"

README.html: README.md README.css
	pandoc README.md -f markdown -t html -s -H README.css -o README.html

"${MODULESDIR}/${APPNAME}_ui.py":
	pyuic5 "${MODULESDIR}/${APPNAME}.ui" --import-from=gui -o "${MODULESDIR}/${APPNAME}_ui.py"

"${RUNSCRIPT}":
	touch "${RUNSCRIPT}"
	chmod a+x "${RUNSCRIPT}"
	@echo '#!/bin/bash' > "${RUNSCRIPT}"
	@echo 'APPNAME='${APPNAME} >> "${RUNSCRIPT}"
	@echo 'APPDIR='${APPDIR} >> "${RUNSCRIPT}"
	@echo 'cpwd=`pwd`' >> "${RUNSCRIPT}"
	@echo 'SCRIPTPATH=$$(realpath "$$0")' >> "${RUNSCRIPT}"
	@echo 'SCRIPTDIR=$$(dirname "$$SCRIPTPATH")' >> "${RUNSCRIPT}"
	@echo 'cd "$$cpwd"' >> "${RUNSCRIPT}"
	@echo 'APP=$$SCRIPTDIR/$$APPDIR/$$APPNAME' >> "${RUNSCRIPT}"
	@echo '$$APP "$$@"' >> "${RUNSCRIPT}"

"${INSTALLSCRIPT}": "${DESKTOPFILE}"
	touch "${INSTALLSCRIPT}"
	chmod u+x "${INSTALLSCRIPT}"
	@echo '#!/bin/bash' > "${INSTALLSCRIPT}"
	@echo '[ ! -f "${APPDIR}/${APPNAME}" ] && echo "${APPDIR}/${APPNAME} does not exist." && exit 2' >> "${INSTALLSCRIPT}"
	@echo 'sudo mkdir -p "${INSTALLDIR}"' >> "${INSTALLSCRIPT}"
	@echo 'sudo cp -r "${APPDIR}" "${APPNAME}" "${INSTALLDIR}"' >> "${INSTALLSCRIPT}"
	@echo 'sudo ln -s "${INSTALLDIR}/${APPNAME}" "${INSTALLLINKDIR}"' >> "${INSTALLSCRIPT}"
	@echo 'cp "${APPDIR}/${DESKTOPFILE}" "${INSTALLDESKTOPDIR}"' >> "${INSTALLSCRIPT}"
	@echo 'cp "${APPDIR}/${DESKTOPFILEALT}" "${INSTALLDESKTOPDIR}"' >> "${INSTALLSCRIPT}"

"${UNINSTALLSCRIPT}": "${DESKTOPFILE}" "${DESKTOPFILEALT}"
	touch "${UNINSTALLSCRIPT}"
	chmod u+x "${UNINSTALLSCRIPT}"
	@echo '#!/bin/bash' > "${UNINSTALLSCRIPT}"
	@echo 'sudo rm -rf "${INSTALLDIR}"' >> "${UNINSTALLSCRIPT}"
	@echo 'sudo rm -f "${INSTALLLINKDIR}"' >> "${UNINSTALLSCRIPT}"
	@echo 'rm -f "${INSTALLDESKTOPDIR}/${DESKTOPFILE}"' >> "${UNINSTALLSCRIPT}"
	@echo 'rm -f "${INSTALLDESKTOPDIR}/${DESKTOPFILEALT}"' >> "${UNINSTALLSCRIPT}"

"${DESKTOPFILE}":
	touch "${DESKTOPFILE}"
	chmod u+x "${DESKTOPFILE}"
	@echo '[Desktop Entry]' > "${DESKTOPFILE}"
	@echo 'Exec=${INSTALLDIR}/${APPNAME}' >> "${DESKTOPFILE}"
	@echo 'Version=${VERSION}' >> "${DESKTOPFILE}"
	@echo 'Name=${APPTITLE}' >> "${DESKTOPFILE}"
	@echo 'GenericName=Standard options' >> "${DESKTOPFILE}"
	@echo 'Comment=gamelist.xml file editor for EmulationStation in RetroPie' >> "${DESKTOPFILE}"
	@echo 'Icon=${INSTALLDIR}/${APPDIR}/${APPICON}' >> "${DESKTOPFILE}"
	@echo 'Categories=Application;Qt;Utility;' >> "${DESKTOPFILE}"
	@echo 'Encoding=UTF-8' >> "${DESKTOPFILE}"
	@echo 'Type=Application' >> "${DESKTOPFILE}"
	@echo 'Terminal=false' >> "${DESKTOPFILE}"

"${DESKTOPFILEALT}":
	touch "${DESKTOPFILEALT}"
	chmod u+x "${DESKTOPFILEALT}"
	@echo '[Desktop Entry]' > "${DESKTOPFILEALT}"
	@echo 'Exec=${INSTALLDIR}/${APPNAME} -i -e -E -O -a -g -m -n -z' >> "${DESKTOPFILEALT}"
	@echo 'Version=${VERSION}' >> "${DESKTOPFILEALT}"
	@echo 'Name=${APPTITLE} (Alternative)' >> "${DESKTOPFILEALT}"
	@echo 'GenericName=Alternative options: -i -e -E -O -a -g -m -n -z' >> "${DESKTOPFILEALT}"
	@echo 'Comment=gamelist.xml file editor for EmulationStation in RetroPie' >> "${DESKTOPFILEALT}"
	@echo 'Icon=${INSTALLDIR}/${APPDIR}/${APPICON}' >> "${DESKTOPFILEALT}"
	@echo 'Categories=Application;Qt;Utility;' >> "${DESKTOPFILEALT}"
	@echo 'Encoding=UTF-8' >> "${DESKTOPFILEALT}"
	@echo 'Type=Application' >> "${DESKTOPFILEALT}"
	@echo 'Terminal=false' >> "${DESKTOPFILEALT}"
