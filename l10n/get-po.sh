#!/bin/bash

echodo() { echo "${@}"; ${@}; }

[ -x tx_bin/tx ] && TXBIN=tx_bin/tx
: ${TXBIN:=$(which tx)}

[ ! -x "$TXBIN" ] && echo "Error: transifex client not found!" && exit 1

# [o:fehlix:p:testproject-do-not-use:r:mx-updater-test]
# RESOURCE="testproject-do-not-use.mx-updater-test"
# [o:anticapitalista:p:antix-development:r:mx-updater]
# RESOURCE="antix-development.mx-updater"

ORGANIZATION_SLUG="anticapitalista"
PROJECT_SLUG="antix-development"
RESOURCE_SLUG="mx-updater"
RESOURCE="${PROJECT_SLUG}.${RESOURCE_SLUG}"

POT_FILE="mx-updater.pot"
POT_FILE="mx-updater_new.pot"
PO_DIR="po"
PO_BAK="${PO_DIR}_$(date '+%Y-%m-%d_%H%M%S').bak"

# prepare transifex 
[ -d .tx ]  || mkdir -p .tx
[ -f .tx/config ] && rm .tx/config

cat <<EOF > .tx/config
[main]
host = https://app.transifex.com

[o:${ORGANIZATION_SLUG}:p:${PROJECT_SLUG}:r:${RESOURCE_SLUG}]

file_filter = ${PO_DIR}/<lang>.po
minimum_perc = 25
source_file = ${POT_FILE}
source_lang = en
type = PO

EOF

# backup existing
[ -d "${PO_DIR}" ] && echodo mv "${PO_DIR}" "${PO_BAK}"
mkdir "${PO_DIR}"
[ -f "${PO_BAK}/LINGUAS" ] && cp "${PO_BAK}/LINGUAS" "${PO_DIR}/LINGUAS"

echodo() {
    echo "${@}";
    ${@};
    }


# get all translations
# echodo ${TXBIN} pull --force  -r "$RESOURCE" --all 

# get all translations mentioned in LINGUAS
# and retrieve pot file from transifix as "mx-updater_new.pot"
echodo ${TXBIN} pull  -r "$RESOURCE" -s -t -l $(grep -v '^\s*#' ${PO_DIR}/LINGUAS | tr '\n' ',' | sed 's/,$//')

[ -f .tx/config ] && rm .tx/config
[ -d .tx ]  && rmdir .tx
