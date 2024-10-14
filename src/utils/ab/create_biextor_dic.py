russian_word_list = []
abkhazian_word_list = []

outputfile = 'ab-ru-probability.dic'
output = open(outputfile,"w+")

cyrillic_encoding="utf-8"
probability = 0.9
#read the russian word into the list
with open('../draft/dictionary_prescript.ru', 'r+',encoding=cyrillic_encoding) as f:
    russian_word_list = f.read().splitlines()
with open('../draft/dictionary.ru', 'r+',encoding=cyrillic_encoding) as f:
    russian_word_list += f.read().splitlines()

# read also the abkhazian translations
with open('../draft/dictionary_prescript.ab', 'r+',encoding=cyrillic_encoding) as f:
    abkhazian_word_list = f.read().splitlines()
with open('../draft/dictionary.ab', 'r+',encoding=cyrillic_encoding) as f:
    abkhazian_word_list += f.read().splitlines()


for translation_tuple in zip(abkhazian_word_list, russian_word_list):
    if probability:
        output.write(translation_tuple[0]+"\t"+translation_tuple[1]+"\t"+str(probability)+"\n")
    else:
        output.write(translation_tuple[0]+"\t"+translation_tuple[1]+"\n")

'''
The generated dictionary can be used with https://github.com/bitextor

bifixer:
python3 bifixer/bifixer.py --scol 1 --tcol 2 --ignore_duplicates ru-ab-parallel.txt ru-ab-parallel.bifixed ru ab

apply the hardrules:

python3 bicleaner/bicleaner_hardrules.py ru-ab-parallel.bifixed ru-ab-parallel.clean -s ru -t ab --scol 1 --tcol 2 --disable_lm_filter

train bicleaner:

python3.7 bicleaner/bicleaner_train.py \
ru-ab-parallel.clean \
--treat_oovs --normalize_by_length \
-s ru -t ab \
-d ru-ab-probability.dic.gz -D ab-ru-probability.dic.gz \
-b 1000 -c ru-ab.classifier \
-g 10000 -w 10000 \
-m ru-ab.yaml \
--classifier_type random_forest \
--lm_training_file_sl lmtrain.ru-ab.ru --lm_training_file_tl lmtrain.ru-ab.ab \
--lm_file_sl model.ru-ab.ru  --lm_file_tl model.ru-ab.ab

'''
