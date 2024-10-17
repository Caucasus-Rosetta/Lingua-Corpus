for file in $(ls | grep '^[0-9]\+.tsv$');
do
  cp $file $file.temp;
done

for file in $(ls | grep '^[0-9]\+.tsv.temp$')
do
  ### preprocess
  sed -i -e '/^\t$/d' $file;
  sed -i -e 's/[«»"“”\(\)\*№]//g' $file;
  sed -i -e 's/[:;]/…/g' $file;
  sed -i -r 's/[\.]{2,3}/…/g' $file;
  sed -i -r 's/[,]+/,/g' $file;
  sed -i -r 's/[!]+/!/g' $file;
  sed -i -r 's/[?]+/?/g' $file;
  sed -i -r 's/,([[:alpha:]])/, \1/g' $file;
  sed -i -r 's/([!?])[,\.]+/\1/g' $file;
  sed -i -r 's/[ ]+([…,!?\.])/\1/g' $file;
  sed -i -e 's/- / /g' -e 's/ - / /g' $file;
  sed -i -r 's/([[:alpha:]])–([[:alpha:]])/\1-\2/g' $file;
  sed -i -r 's/–/—/g' $file;
  sed -z -i -r 's/([[:alpha:][:digit:]])[,]*([\t\n])/\1…\2/g' $file;
  ### Splitting
  sed -i -r 's/([?!…][!]*)/\1#/g' $file;
  sed -i -r 's/([[:alpha:]]{3,}\.)/\1#/g' $file;
  ### postprocess
  sed -i -r 's/([#\t])[[:punct:] ]*([[:alpha:]])/\1\U\2/g' $file;
  sed -i -r 's/^[[:punct:] ]*([[:alpha:]])/\U\1/g' $file;
  sed -z -i -r 's/#([\t\n])/\1/g' $file;
  sed -i -r 's/([^ ])—/\1 —/g' $file;
  sed -i -r 's/—([^ ])/— \1/g' $file;
  sed -i -r 's/^[ ]+|[ ]+$//g' $file;
  sed -i -r 's/[ ]+/ /g' $file;
done
