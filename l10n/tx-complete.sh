#!/bin/bash

#-----------------------------------
PODIR=po
LOG=$PODIR/TX-COMPLETE.LOG
LINGUAS=$PODIR/LINGUAS
EN_POT=mx-updater.pot

which isoquery >/dev/null || { 
    echo "Needed 'isoquery' not found. Install with: apt install isoquery"; 
    exit 1;
    }

GEN_DATE=$(TZ=America/New_York  date -R)
# total number of "strings": msgid's to be translated

T=$(grep -cw msgid $EN_POT) ; ((T--))
#-----------------------------------
echo "# Languages codes with translation completness  >= 25%" | tee    $LOG
echo "# generated with tx-complete.sh at $GEN_DATE"           | tee -a $LOG
echo "# Number of translations: $T"                           | tee -a $LOG
printf '%6s\t\t%4s\t%7s\t\t%s\t\t%s\n' "Nr." "Cnt." "Compl." "Code" "Language" | tee -a $LOG
printf '%6s\t\t%4s\t%7s\t\t%s\t\t%s\n' "---" "----" "------" "----" "--------" | tee -a $LOG


for P in $PODIR/*.po ; do 
    L=${P##*/}; 
    L=${L%.po};
    ll=${L%%_*}
    rr=${L##*_}
    [[ -n ${L##*_*} ]] && rr=
    L="$(printf '%-8s' ${L})";

    Z=$(msggrep --no-wrap -T -e '.' $P  | grep -cw msgid); 
    ((Z>0)) && ((Z--))
    printf '\t%4d\t%6d%%    \t%s\t%s%s\n' $Z $((Z*100/T)) "$L" \
        "$( isoquery --iso=639-${#ll} -n $ll | sed 's/L\t\t//' | cut -f3- )"  \
        "${rr:+ @ $(isoquery -i 3166-1 $rr   | cut -f4 )}"; 
done | sort -t $'\t' -k2nr,2 -k4,4 | cat -n | tee -a $LOG

#
echo "# languages codes with translation completness  >= 25%"  >  $LINGUAS
echo "# generated with tx-complete.sh at $GEN_DATE"            >> $LINGUAS 
echo "# "                                                      >> $LINGUAS
grep -E '([5-9]|[0-9]{2})%' $LOG | grep -v '^#'  | awk '{print $4}' | sort -u >> $LINGUAS

# create LINGUAS with translations completness >= 10%
# grep -E '[0-9]{2}%' $LOG | awk '{print $4}' | sort -u > $LINGUAS
echo ""
echo "$LINGUAS:"
grep '#' $LINGUAS
echo $( grep -v '#' $LINGUAS )

exit

