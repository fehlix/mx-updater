#!/bin/bash

# Update PO files from a POT file
# Usage: ./update-po.sh

# Set the path to the POT file
POT_FILE="mx-updater.pot"
LINGUAS="po/LINGUAS"
# Check if the POT file exists
if [ ! -f "${POT_FILE}" ]; then
    echo "Error: POT file ${POT_FILE} not found"
    exit 1
fi

if [ ! -f "$LINGUAS" ]; then
    echo "Error: LINGUAS file $LINGUAS not found"
    exit 1
fi

# Read the list of languages from LINGUAS file
LANGUAGES=$(grep -v '^#' "$LINGUAS")

# Loop through each language and update its PO file
for LANG in $LANGUAGES; do
    PO_FILE="po/${LANG}.po"
    
    # Check if the PO file exists
    if [ ! -f "${PO_FILE}" ]; then
        echo "Warning: PO file for language $LANG not found, skipping"
        continue
    fi
    
    # Update the PO file using msgmerge
    msgmerge --backup=simple --no-fuzzy-matching --no-wrap  -U "${PO_FILE}" "${POT_FILE}"
    # --no-location

    # Check if msgmerge was successful
    if [ $? -eq 0 ]; then
        echo "Updated PO file for $LANG"

        # remove python replace format comments
        sed -i '/^#, python/d' "${PO_FILE}"
    
        # remove locations
        sed -i '/^#:/d' "${PO_FILE}"
    
        # remove old translations
        sed -i '/^#~/d' "${PO_FILE}"
    
    else
        echo "Error updating PO file for $LANG"
    fi
done

echo "PO file update process completed"
