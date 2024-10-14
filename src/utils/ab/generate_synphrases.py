# -*- coding: utf_8 -*-

outputfile = 'output paraphrase.txt'
output = open(outputfile,"w+")

cyrillic_encoding = "utf-8"

russian_word_list = []
abkhazian_word_list = []

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

# we combine the lists to a translation dictionary
dictionary_ru_ab = {}
for translation_tuple in zip(russian_word_list, abkhazian_word_list):
    if translation_tuple[0] in dictionary_ru_ab:
        dictionary_ru_ab[translation_tuple[0]].append(translation_tuple[1])
    else:
        dictionary_ru_ab[translation_tuple[0]] = [translation_tuple[1]]


dictionary_ab_ru = {}
for translation_tuple in zip(abkhazian_word_list, russian_word_list):
    if translation_tuple[0] in dictionary_ab_ru:
        dictionary_ab_ru[translation_tuple[0]].append(translation_tuple[1])
    else:
        dictionary_ab_ru[translation_tuple[0]] = [translation_tuple[1]]

# we extract the synonyms from the dictionary
synonyms = {}
for translations in dictionary_ru_ab.values():
    if len(translations) >= 2:
        #the abkhazian words are translated to the same russian word
        for translation in translations:
            #we save the other words as synonym values for the translation
            synonym_list = translations.copy()
            #the translation shouldn't be in list
            synonym_list.remove(translation)
            if translation in synonyms.keys():
                synonyms[translation].update(synonym_list)
            else:
                synonyms[translation] = set(synonym_list)
# there could be even more synonyms, if the translation word occurs in different pairs

abkhazian_paraphrases = {}
# Let's generate paraphrases
# and store them like
# abkhazian_paraphrases = {"original sentence":["paraphrase1","paraphrase2"]}

def generate_paraphrases(sentence):
    for synonym_key in synonyms.keys():
        paraphrases = []
        # search and exchange the synonym
        # the search space could be advanced to the start and end of the sentence
        # how can we make this case sensitive?
        if " "+synonym_key+" " in sentence:
            # we have found a match
            output.write("\n"+sentence+"\n")
            for i,synonym in enumerate(synonyms[synonym_key]):
                if len(paraphrases) == i:
                    paraphrases.append(sentence[:])
                if " "+synonym_key+" " in paraphrases[i]:
                    paraphrases[i] = paraphrases[i].replace(" "+synonym_key+" ", " "+synonym+" ")
                    #write the exchanhe to the output_type
                    output.write("\t"+synonym_key+" --> "+synonym+"\n")
        if len(paraphrases) > 0:
            abkhazian_paraphrases[sentence] = paraphrases

with open('../ab/parliament ab', 'r+',encoding=cyrillic_encoding) as f:
    abkhazian_sentences = f.read().splitlines()
    for sentence in abkhazian_sentences:
        generate_paraphrases(sentence)

import random
print("random paraphrase sample:")
sample_key = random.choice(list(abkhazian_paraphrases.keys()))
print(sample_key+"\n"+abkhazian_paraphrases[sample_key][0])
print("synonym count:")
print(len(synonyms))
print("paraphrase count:")
print(sum([len(abkhazian_paraphrases[sentence]) for sentence in abkhazian_paraphrases.keys()]))

'''
for paraphrases_key in list(abkhazian_paraphrases.keys()):
    for paraphrase in abkhazian_paraphrases[paraphrases_key]:
        output.write(paraphrase+"\n")
'''
