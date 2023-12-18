value="";
value=$(ls | grep -o '^[0-9]\+.tsv.temp$');
if [ ! -z "$value" ]; then sed -r 's/[^[:print:]\t]//g' [0-9]*.tsv.temp|cat - > all.tsv.temp && rm [0-9]*.tsv.temp; fi
cat all.tsv.temp > all.tsv.clean.temp
file="all.tsv.clean.temp"
# Remove all but the following symbols and patterns
sed -i -r '/^[0-9+-]*\t[аәбвгӷдежзӡикқҟлмнопԥрстҭуфхҳцҵчҷҽҿџшыьҩ ,?—-]+[…\.!?]\t[ёйцукенгшщзхъфывапролджэячсмитьбю ,?—-]+[…\.!?]\t0$/I!d' $file;
sed -i -r '/\tҲәа[н, ]|\t[АИСРШЛҲ]ҳә[аое]|[[:alpha:]]-[[:alpha:]]+-[[:alpha:]]|^[0-9+-]*\t[[:print:]]*\b[[:alpha:]]\b[^-][[:print:]]*\t|[[:upper:]][[:upper:]]/d' $file;
# Remove duplicates from source
cut -f2,3 $file | sed -e 's/[[:punct:]]//g' | sed 's/./\L&/g' | \
paste $file - > $file.temp;
sort -t$'\t' -k4 -u $file.temp | cut -f1,2,3 | shuf > $file && rm $file.temp;
### Replace more or less than 40-200 characters.
sed -r 's/…//g' $file |sed -r '/^-|^9|^\+9/d' | \
perl -e 'print sort { length($a) <=> length($b) } <>' > all.tsv.clean && rm all.tsv.clean.temp;
# grep -Ex $'[0-9+-]*\t.{20,100}' > all.tsv.clean && rm all.tsv.clean.temp;
