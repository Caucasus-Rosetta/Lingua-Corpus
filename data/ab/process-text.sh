# Manual cleanup
# [_—−–]$ and [_]
# [ёйщъэяю]
# 4: Chane Alpha to ALPHA for misplaced single words in a line.
alpha="аәбвгӷдежзӡикқҟлмнопԥрстҭуфхҳцҵчҷҽҿџшыьҩ"
regex=$(sed -z -r 's/([[:alpha:]])\n([[:alpha:]])/\1|\2/g' caps.txt)
for file in $(ls | grep '^[0-9]\+.txt$');
do
  cp $file $file.temp;
done

for file in $(ls | grep '^[0-9]\+.txt.temp$')
do
  ### preprocess
  sed -ni '/['$alpha']/p' $file;
  # 4
  sed -i -r '/^[АӘБВГӶДЕЖЗӠИКҚҞЛМНОПԤРСТҬУФХҲЦҴЧҶҼҾЏШЫЬҨ ]+$/d' $file;
  sed -i -r 's/\xE2\x80\x89/ /g' $file;
  sed -i -z 's/\xCC\x81//g' $file;
  sed -i -z 's/\x0C//g' $file;
  sed -i -z 's/\xC2\xAD[\n]*//g' $file;
  sed -i -e 's/[:;]/…/g' -e 's/ҕ/ӷ/g' -e 's/Ҕ/Ӷ/g' -e 's/ҧ/ԥ/g' -e 's/Ҧ/Ԥ/g' $file;
  sed -i -r 's/[\.]{2,3}/…/g' $file;
  sed -i -r 's/[,]+/,/g' $file;
  sed -i -r 's/[!]+/!/g' $file;
  sed -i -r 's/[?]+/?/g' $file;
  sed -i -r 's/,([[:alpha:]])/, \1/g' $file;
  sed -i -r 's/([!?])[,\.]+/\1/g' $file;
  sed -i -r 's/ ([…,!?\.])/\1/g' $file;
  sed -i -e 's/- / /g' -e 's/ - / /g' $file;
  sed -i -e 's/[«»“”\(\)\*№]//g' $file;
  sed -i -r 's/([[:alpha:]])–([[:alpha:]])/\1-\2/g' $file;
  ### Splitting
  sed -i -z 's/[-]\n//g' $file;
  # 1
  sed -i -z -r 's/([[:alpha:],])\n\b('$regex')\b/\1 #\U\2/g' $file;
  sed -i -r 's/#([[:upper:]])([[:upper:]]+)/\1\L\2/g' $file;
  sed -i -z -r 's/([[:alpha:],])\n([[:upper:]])/\1 \L\2/g' $file;
  sed -i -z 's/\n/ /g' $file;
  sed -i -r 's/([?!…][!]*)|–[ ]*([[:upper:]])/\1\n\2/g' $file;
  sed -i -r 's/([[:alpha:]]{3,}\.)/\1\n/g' $file;
  ### postprocess
  # 2
  sed -i -r 's/–/ /g' $file;
  sed -i -r 's/,[ ]*\b([аисршлҳ]ҳә[аое][и]*[нтп])\b/, – \1/g' $file;
  # 3
  sed -i -r 's/^.*[0-9]+[ ,]*([[:upper:]])/\1/g' $file;
  #
  sed -i -r 's/^[ ]+|[ ]+$//g' $file;
  sed -i -r 's/([[:alpha:]])[,]*$/\1…/g' $file;
  sed -i -r 's/[ ]+/ /g' $file;
  sed -i -r 's/^(['$alpha'])/\U\1/' $file
  ### Sorting and removing duplicates
  sort $file | uniq > $file+2;
  cat $file+2 | awk '{ print length, $0 }' | sort -n -s | cut -d" " -f2- > $file;
  sed -i -r 's/^/'${file/.txt.temp/}'\t/g' $file;
  rm $file+2;
done
