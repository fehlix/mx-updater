#!/bin/bash

echodo() { echo "${@}"; ${@}; }

[ -x tx_bin/tx ] && TXBIN=tx_bin/tx
: ${TXBIN:=$(which tx)}

[ ! -x "$TXBIN" ] && echo "Error: transifex client not found!" && exit 1

ORGANIZATION_SLUG="anticapitalista"
PROJECT_SLUG="antix-development"
RESOURCE_SLUG="mx-updater"
RESOURCE="${PROJECT_SLUG}.${RESOURCE_SLUG}"

POT_FILE="mx-updater.pot"
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

# tx push -r <project-slug>.<resource-slug> -s
#echodo ${TXBIN} push -r ${RESOURCE} -s 
echo "Run this command manually if you realy want to do this:"
echo ${TXBIN} push -r ${RESOURCE} -s 

exit

