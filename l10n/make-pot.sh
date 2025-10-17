#!/bin/bash

#set -x
# creates a mx-updater.pot file 

export TZ="America/New_York"

PKGNAME=mx-updater
POTFILE=mx-updater.pot
ITSRULES=./mx-updater.its

echodo() { local run="$1"; shift; echo "$run" "${@@Q}"; "$run" "$@"; }

unset PYTHON_FILES DESKTOP_FILES SHELL_FILES POLICY_FILES

PYTHON_FILES=( $(grep -l -E 'gettext|_\(|_tn\(' ../libexec/mx-updater/*[a-z].py) )
declare -p PYTHON_FILES

DESKTOP_FILES=( 
    #$(ls -1 ../xdg/*.desktop) 
    ../xdg/mx-updater.desktop
    ../xdg/mx-updater-settings.desktop
    ../xdg/mx-updater-autostart.desktop
    )
declare -p DESKTOP_FILES

SHELL_FILES=( $(ls -1 ../bin/* )
              $(ls -1 ../lib/mx-updater/bin/*)
              ../lib/mx-updater/shlib/updater_shlib
            )
declare -p SHELL_FILES

POLICY_FILES=( $(ls -1 ../polkit/actions/org.mxlinux.mx-updater.*.policy ))
declare -p POLICY_FILES

# Create an ITS rules file
cat > ${ITSRULES} << 'EOL'
<?xml version="1.0"?>
<its:rules xmlns:its="http://www.w3.org/2005/11/its" version="2.0">
  <its:translateRule selector="//*" translate="no"/>
  <its:translateRule selector="//action/description" translate="no"/>
  <its:translateRule selector="//action/message" translate="yes"/>
</its:rules>
EOL


# Create a base header template
[ -f "${POTFILE}" ] && mv "${POTFILE}" "${POTFILE}~"
cat > ${POTFILE} << EOL
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR THE COPYRIGHT HOLDER
# This file is distributed under the same license as the PACKAGE package.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
msgid ""
msgstr ""
"Project-Id-Version: $PKGNAME\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: $(TZ=America/New_York date +"%Y-%m-%d %H:%M%z")\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
EOL


NO_LOCATION="--no-location"
NO_LOCATION=""

OPTS="--join-existing --no-wrap ${NO_LOCATION} --package-name=$PKGNAME"

echodo xgettext $OPTS --add-comments -L Desktop -o $POTFILE "${DESKTOP_FILES[@]}"

echodo xgettext $OPTS  --its=${ITSRULES} -o ${POTFILE} "${POLICY_FILES[@]}"

echodo xgettext $OPTS --add-comments -L Shell -o $POTFILE "${SHELL_FILES[@]}"

echodo xgettext $OPTS -L Python -cTRANSLATORS: -o $POTFILE "${PYTHON_FILES[@]}"

# set charset to UTF-8, if needed
sed -i '/Content-Type/s/CHARSET/UTF-8/' ${POTFILE}

# remove python replace format comments
sed -i '/^#, python/d' ${POTFILE}

if [ -f "${POTFILE%.pot}_w_location.pot" ]; then
    mv "${POTFILE%.pot}_w_location.pot"  "${POTFILE%.pot}_w_location.pot~" 
    cp "${POTFILE}"  "${POTFILE%.pot}_w_location.pot" 
fi
# remove locations
sed -i '/^#:/d' ${POTFILE}


if [ -f "${POTFILE}" ] &&  [ -f "${POTFILE}~" ]; then

    if diff -I 'POT-Creation-Date' "${POTFILE}~" "${POTFILE}" | grep . ; then 
        # changed
        BAK_DATE="$(date '+%Y-%m-%d_%H%M%S')"
        POTFILE_BAK="${POTFILE}_${BAK_DATE}.bak"
        echo "POT-file changed, backup to ${POTFILE_BAK}"
        mv "${POTFILE}~" "${POTFILE_BAK}"
        mv "${POTFILE%.pot}_w_location.pot~" "${POTFILE%.pot}_w_location.pot_${BAK_DATE}.bak"
    else 
        # not changed
        echo "POT-file not changed"
        mv "${POTFILE}~" "${POTFILE}"
        mv "${POTFILE%.pot}_w_location.pot~" "${POTFILE%.pot}_w_location.pot"
    fi

fi

[ -f  "${ITSRULES}" ] && rm  "${ITSRULES}"

exit 0
