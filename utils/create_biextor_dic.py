russian_word_list = []
abkhazian_word_list = []

outputfile = 'ru-ab.dic'
output = open(outputfile,"w+")

cyrillic_encoding="utf-8"
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


for translation_tuple in zip(russian_word_list, abkhazian_word_list):
    output.write(translation_tuple[0]+"\t"+translation_tuple[1]+"\n")
