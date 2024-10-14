import json
import io

"""
We can export abkhaz_synonyms and russian_synonyms.
The synonym dictionaries are constructed like:
synonyms = {
"key_word":set(synonym1,synonym2,synonym3),
"key_word2":set(...),...
}
"""

cyrillic_encoding = "utf-8"
with io.open('dictionary.json', 'r+',encoding=cyrillic_encoding) as f:
    ru_dictionary = json.loads(f.read())

russian_dictionay_mixin = ru_dictionary["wordlist"]
# we extract the synonyms from the dictionary
russian_synonyms = {}
for word in russian_dictionay_mixin:
    if "synonyms" in word.keys():
        if word["name"] in russian_synonyms.keys():
            russian_synonyms[word["name"]].update(word["synonyms"])
        else:
            russian_synonyms[word["name"]] = set(word["synonyms"])

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
abkhaz_synonyms = {}
for translations in dictionary_ru_ab.values():
    if len(translations) >= 2:
        #the abkhazian words are translated to the same russian word
        for translation in translations:
            #we save the other words as synonym values for the translation
            synonym_list = translations.copy()
            #the translation shouldn't be in list
            synonym_list.remove(translation)
            if translation in abkhaz_synonyms.keys():
                abkhaz_synonyms[translation].update(synonym_list)
            else:
                abkhaz_synonyms[translation] = set(synonym_list)
