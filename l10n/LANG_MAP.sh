#!/bin/bash


:<<'XXX'

LINGUA      LANG
ca          ca_ES.UTF-8          Catalan; Valencian
cs          cs_CZ.UTF-8          Czech
de          de_DE.UTF-8          German
el          el_GR.UTF-8          Greek, Modern (1453-)
es_ES       es_ES.UTF-8          Spanish; Castilian @ Spain
fi          fi_FI.UTF-8          Finnish
fr          fr_FR.UTF-8          French
fr_BE       fr_BE.UTF-8          French @ Belgium
gl_ES       gl_ES.UTF-8          Galician @ Spain
hi          hi_IN.UTF-8          Hindi
hu          hu_HU.UTF-8          Hungarian
it          it_IT.UTF-8          Italian
ja          ja_JP.UTF-8          Japanese
nb          nb_NO.UTF-8          Bokmål, Norwegian; Norwegian Bokmål
nl          nl_NL.UTF-8          Dutch; Flemish
pl          pl_PL.UTF-8         Polish
pt          pt_PT.UTF-8          Portuguese
pt_BR       pt_BR.UTF-8          Portuguese @ Brazil
ru          ru_RU.UTF-8          Russian
sl          sl_SI.UTF-8          Slovenian
sv          sv_SE.UTF-8          Swedish
tr          tr_TR.UTF-8          Turkish
sq          sq_AL.UTF-8          Albanian
nl_BE       nl_BE.UTF-8          Dutch; Flemish @ Belgium
da          da_DK.UTF-8          Danish
fil_PH      fil_PH.UTF-8         Filipino @ Philippines
fa          fa_IR.UTF-8          Persian
sk          sk_SK.UTF-8          Slovak
am          am_ET.UTF-8          Amharic
hr          hr_HR.UTF-8          Croatian
lt          lt_LT.UTF-8          Lithuanian
th          th_TH.UTF-8          Thai


for K in "${!LANGMAP[@]}"; do L="${LANGMAP[$K]}"; echo K=$K  L=$L; msginit -i mx-updater.pot -l "$L" -o po.init/$K.po.init --no-translator --no-wrap; done

XXX


unset LANGMAP

declare -A LANGMAP=(
#    "LINGUA"            "LANG"
    "ca"                "ca_ES.UTF-8"
    "cs"                "cs_CZ.UTF-8"
    "de"                "de_DE.UTF-8"
    "el"                "el_GR.UTF-8"
    "es_ES"             "es_ES.UTF-8"
    "fi"                "fi_FI.UTF-8"
    "fr"                "fr_FR.UTF-8"
    "fr_BE"             "fr_BE.UTF-8"
    "gl_ES"             "gl_ES.UTF-8"
    "hi"                "hi_IN.UTF-8"
    "hu"                "hu_HU.UTF-8"
    "it"                "it_IT.UTF-8"
    "ja"                "ja_JP.UTF-8"
    "nb"                "nb_NO.UTF-8"
    "nl"                "nl_NL.UTF-8"
    "pl"                "pl_PL.UTF-8"
    "pt"                "pt_PT.UTF-8"
    "pt_BR"             "pt_BR.UTF-8"
    "ru"                "ru_RU.UTF-8"
    "sl"                "sl_SI.UTF-8"
    "sv"                "sv_SE.UTF-8"
    "tr"                "tr_TR.UTF-8"
    "sq"                "sq_AL.UTF-8"
    "nl_BE"             "nl_BE.UTF-8"
    "da"                "da_DK.UTF-8"
    "fil_PH"            "fil_PH.UTF-8"
    "fa"                "fa_IR.UTF-8"
    "sk"                "sk_SK.UTF-8"
    "am"                "am_ET.UTF-8"
    "hr"                "hr_HR.UTF-8"
    "lt"                "lt_LT.UTF-8"
    "th"                "th_TH.UTF-8"
)

exit 0
exit 0
exit 0

for K in "${!LANGMAP[@]}"; do
    L="${LANGMAP[$K]}";
    echo K=$K  L=$L;
    msginit -i mx-updater.pot -l "$L" -o po.init/$K.po.init --no-translator --no-wrap;

    msgcat --no-wrap --use-first -o po/$K.po.init  po.init/$K.po.init po.apt-notifier/$K.po

    #msgmerge --no-fuzzy-matching --no-wrap   -o po/$K.po   po/$K.po.init  mx-updater.pot
    msgmerge  --no-wrap   -o po/$K.po   po/$K.po.init  mx-updater.pot

    rm po/$K.po.init
    sed -i  '1,/^msgid/{/^msgid/{h; s/.*/#, fuzzy/;p;x}}' po/$K.po
done
