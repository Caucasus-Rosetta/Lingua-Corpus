import random
import io
import re
from os import listdir
import random
import json
import datetime
import argparse
import sys

#we define the functions to create the synonyme for the paraphrase generation
russian_synonyms = {}
"""
The synonym dictionaries are constructed like:
synonyms = {
"key_word":set(synonym1,synonym2,synonym3),
"key_word2":set(...),...
}
"""
cyrillic_encoding = "utf-8"

def load_russian_synonyms(json_path='../utils/dictionary.json'):
    with io.open(json_path, 'r+',encoding=cyrillic_encoding) as f:
        ru_dictionary = json.loads(f.read())

    russian_dictionay_mixin = ru_dictionary["wordlist"]
    # we extract the synonyms from the dictionary
    for word in russian_dictionay_mixin:
        if "synonyms" in word.keys():
            if word["name"] in russian_synonyms.keys():
                russian_synonyms[word["name"]].update(word["synonyms"])
            else:
                russian_synonyms[word["name"]] = set(word["synonyms"])

russian_word_list = []
abkhazian_word_list = []
dictionary_ru_ab = {}
dictionary_ab_ru = {}
abkhaz_synonyms = {}

def load_ab_ru_dictionary(dic_one='../draft/dictionary_prescript.ru', dic_two='../draft/dictionary.ru', translation_dic_one='../draft/dictionary_prescript.ab', translation_dic_two='../draft/dictionary.ab'):
    global russian_word_list,abkhazian_word_list, dictionary_ru_ab, dictionary_ab_ru
    #read the russian word into the list
    with open(dic_one, 'r+',encoding=cyrillic_encoding) as f:
        russian_word_list = f.read().splitlines()
    with open(dic_two, 'r+',encoding=cyrillic_encoding) as f:
        russian_word_list += f.read().splitlines()

    # read also the abkhazian translations
    with open(translation_dic_one, 'r+',encoding=cyrillic_encoding) as f:
        abkhazian_word_list = f.read().splitlines()
    with open(translation_dic_two, 'r+',encoding=cyrillic_encoding) as f:
        abkhazian_word_list += f.read().splitlines()

    # we combine the lists to a translation dictionary
    for translation_tuple in zip(russian_word_list, abkhazian_word_list):
        if translation_tuple[0] in dictionary_ru_ab:
            dictionary_ru_ab[translation_tuple[0]].append(translation_tuple[1])
        else:
            dictionary_ru_ab[translation_tuple[0]] = [translation_tuple[1]]

    for translation_tuple in zip(abkhazian_word_list, russian_word_list):
        if translation_tuple[0] in dictionary_ab_ru:
            dictionary_ab_ru[translation_tuple[0]].append(translation_tuple[1])
        else:
            dictionary_ab_ru[translation_tuple[0]] = [translation_tuple[1]]

def extract_ab_synonyms():
    global abkhaz_synonyms
    # we extract the synonyms from the dictionary
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


#alphabets with sentence signs
dirty_ab = re.compile('[^ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ\.\:,;\ 0-9-\(\)"!?]+')
dirty_ru = re.compile('[^ёйцукенгшщзхъфывапролджэячсмитьбю\.\:,;\ 0-9-\(\)"!?]+')
alphabet_ab = re.compile('[ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ\.\:,;\ 0-9-\(\)"!?]+',re.I)
alphabet_ru = re.compile('[ёйцукенгшщзхъфывапролджэячсмитьбю\.\:,;\ 0-9-\(\)"!?]+',re.I)
sentence_signs = re.compile('[\.\:!?0-9…\(\)\[\]«»]+',re.I)

def filter_out(tuple, min_length_ratio, max_length_ratio, min_length, max_words, verbose, punctuation_filter_boolean):
    ru_words = 1.0*len(tuple[0].split(" "))
    ab_words = 1.0*len(tuple[1].split(" "))
    ru_length = 1.0*len(tuple[0])
    ab_length = 1.0*len(tuple[1])
    # There should be at last one letter of the alphabet
    if (len(dirty_ab.findall(tuple[0].lower())) > 0 and len(alphabet_ab.findall(tuple[0].lower())) == 0) \
    or (len(dirty_ru.findall(tuple[1].lower())) > 0 and len(alphabet_ru.findall(tuple[1].lower())) == 0):
        if verbose:
            print("\nno letter:")
            print(tuple)
        return True
    if ru_length/ab_length < min_length_ratio \
    or ru_length/ab_length > max_length_ratio:
        if verbose:
            print("\n"+str(ru_length/ab_length)+" is not in the length ratio scope with "+str(ru_length)+" russian and "+str(ab_length)+ " abkhazian letters.")
            print(tuple)
        return True
    if len(tuple[0].split(" ")) > max_words or len(tuple[1].split(" ")) > max_words \
    or len(tuple[0]) < min_length or len(tuple[1]) < min_length:
        if verbose:
            print("\ntoo long or too short:")
            print(tuple)
        return True
    if punctuation_filter_boolean and filter_punctuation(tuple):
        if verbose:
            print("wrong punctuation order")
            print(tuple)
        return True
    return False

ignored_count = 0

def read_splitted_corpus(min_length_ratio, max_length_ratio, min_length, max_words, verbose, test_lines, valid_lines, punctuation_filter_boolean):
    global ignored_count
    for i,sentences in enumerate(parallel_text):
        splitted =  sentences.split("\t")
        if len(splitted) == 2 and not filter_out(splitted, min_length_ratio, max_length_ratio, min_length, max_words, verbose, punctuation_filter_boolean):
            ru_sentence = splitted[0]
            ab_sentence = splitted[1]
            if i < test_lines:
                ab_text_valid.write(ab_sentence)
                ru_text_valid.write(ru_sentence+"\n")
            elif i < test_lines+valid_lines and i > test_lines:
                ab_text_test.write(ab_sentence)
                ru_text_test.write(ru_sentence+"\n")
            else:
                ab_train_list.append(ab_sentence)
                ru_train_list.append(ru_sentence+"\n")
        else:
            ignored_count += 1

# now we generate and add the parallel_paraphrases
parallel_paraphrases = {} # dictionary of paraphrases with translation tuples as keys

def exchange_synonym(synonym_key, synonyms,translation_tuple, tuple_index, language):
    global parallel_paraphrases
    paraphrases = []
    # search and exchange the synonym
    # the search space could be advanced to the start and end of the sentence
    # how can we make this case sensitive?
    if " "+synonym_key+" " in translation_tuple[tuple_index]:
        # we have found a match
        for i,synonym in enumerate(synonyms[synonym_key]):
            if len(paraphrases) == i:
                paraphrases.append(translation_tuple[tuple_index][:])
            if " "+synonym_key+" " in paraphrases[i]:
                paraphrases[i] = paraphrases[i].replace(" "+synonym_key+" ", " "+synonym+" ")
    if len(paraphrases) > 0:
        parallel_paraphrases[translation_tuple][language] = paraphrases

def generate_paraphrases(translation_tuple):
    global parallel_paraphrases
    parallel_paraphrases[translation_tuple]["abkhaz"] = []
    for synonym_key in abkhaz_synonyms.keys():
        exchange_synonym(synonym_key, abkhaz_synonyms, translation_tuple, 1, "abkhaz")

    parallel_paraphrases[translation_tuple]["russian"] = []
    for synonym_key in russian_synonyms.keys():
        exchange_synonym(synonym_key, russian_synonyms, translation_tuple, 0, "russian")

def fill_list(list_to_fill, filler, length_to_align, max_length=3):
    length_to_fill = min(length_to_align, max_length)
    for fill in range(length_to_fill-len(list_to_fill)):
        list_to_fill.append(filler)
    return list_to_fill[:length_to_fill]

def save_paraphrases(paraphrase_scale, only_paraphrases):
    global ru_train_list
    global ab_train_list
    if only_paraphrases:
        # we only store the paraphrases into the output files
        ru_train_list = []
        ab_train_list = []
    for translation_tuple in parallel_paraphrases:
        abkhazian_paraphrases = parallel_paraphrases[translation_tuple]["abkhaz"] or []
        russian_paraphrases = parallel_paraphrases[translation_tuple]["russian"] or []
        max_paraphrase_length = min(paraphrase_scale,max(len(russian_paraphrases), len(abkhazian_paraphrases)))
        # we fill the list to the same length
        abkhazian_paraphrases = fill_list(abkhazian_paraphrases, translation_tuple[0], max_paraphrase_length)
        russian_paraphrases = fill_list(russian_paraphrases, translation_tuple[1], max_paraphrase_length)
        # and write them to the train list
        ru_train_list.extend(russian_paraphrases)
        ab_train_list.extend(abkhazian_paraphrases)

def generate_lists(max_list_lengths, enumerate_list):
    # we combine the lists to a translation dictionary
    parallel_translations = list(zip(russian_word_list, abkhazian_word_list))
    for max_list_length in max_list_lengths:
        random.shuffle(parallel_translations)
        current_list_length = 0
        ru_sentence = ""
        ab_sentence = ""
        for i, dic_tuple in enumerate(parallel_translations):
            if current_list_length >= max_list_length:
                ru_train_list.append(ru_sentence)
                ab_train_list.append(ab_sentence)
                ru_sentence = ""
                ab_sentence = ""
                current_list_length = 0

            tuple_number = i % max_list_length + 1
            if tuple_number is not 1:
                ru_sentence += ", "
                ab_sentence += ", "

            if enumerate_list:
                ru_sentence += str(tuple_number)+" "+dic_tuple[0]
                ab_sentence += str(tuple_number)+" "+dic_tuple[1]

            ru_sentence += dic_tuple[0]
            ab_sentence += dic_tuple[1]

            current_list_length += 1

filtered_punctuations = 0
def filter_punctuation(translation):
    global filtered_punctuations
    ru_signs = sentence_signs.findall(translation[0])
    ab_signs = sentence_signs.findall(translation[1])

    if ru_signs == ab_signs:
        return False
    else:
        filtered_punctuations += 1
    return True


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process the corpus with paraphrases and the dictionary')
    parser.add_argument('--dictionary', action='store_true',
                        help='We use the dictionary lists as an additional translation source.')
    parser.add_argument('list_lengths', metavar='ll', type=int, nargs='+',
                        help='the lengths for dictionary lists', default=[1])
    parser.add_argument('--numerate', action='store_true',
                        help='The dictionary list has a numeration')
    # min_length_ratio, max_length_ratio, min_length, max_words
    parser.add_argument('min_length_ratio', metavar='min_ratio', type=float,
                        help='We only use translation with this minimum ratio')
    parser.add_argument('max_length_ratio', metavar='max_ratio', type=float,
                        help='We only use translation with this maximum ratio')
    parser.add_argument('min_length', metavar='min_length', type=int,
                        help='We only use translation with this minimum length')
    parser.add_argument('max_words', metavar='max_words', type=int,
                        help='We only use translation with this maximum words')
    parser.add_argument('paraphrase_scale', metavar='paraphrase_scale', type=int,
                        help='Definies how many paraphrases are generated per sentence pair.')
    parser.add_argument('test_lines', metavar='test_lines', type=int,
                        help='We define the number of lines that are filtered for the test set.')
    parser.add_argument('valid_lines', metavar='valid_lines', type=int,
                        help='The number of lines that are filtered for the validation set.')
    parser.add_argument('--paraphrase', action='store_true',
                        help='We paraphrase the filtered training corpus.')
    parser.add_argument('--verbose', action='store_true',
                        help='We print the filtered lines to the terminal.')
    parser.add_argument('--random', action='store_true',
                        help='We randomize the corpus before splitting it into the training, validation and test sets.')
    # ('Aligning parallel bilingual corpora statistically with punctuation criteria'; Thomas C Chuang and Kevin C Yeh)
    parser.add_argument('--punctuation', action='store_true',
                        help='We use the punctuation criteria as filter in such way that each translation have the same order of sentence signs. The sentence signs are ".:!?0-9…()[]«»".')
    parser.add_argument('corpus_file', metavar='corpus_file', default='ru-ab-parallel-27-07.bifixed',
                        help='We define the path to the aligned corpus file.')
    parser.add_argument('--only_paraphrase', action='store_true',
                        help="We simply generate paraphrases and don't store the original translations into the output file.")

    args = parser.parse_args()

    # arguments_length = len(sys.argv) - 1

    now = datetime.datetime.now()
    current_date = now.strftime('%m-%d-%Y')
    folder = "joined_translation_data/"

    parallel_text = io.open(args.corpus_file,"r+").readlines()

    # we initialize the output files
    if args.only_paraphrase:

        ab_train_list = []
        ru_train_list = []
        ab_paraphrase_file = io.open(folder+current_date+'_paraphrases.ab',"w+", encoding="utf-8")
        ru_paraphrase_file = io.open(folder+current_date+'_paraphrases.ru',"w+", encoding="utf-8")

    else:

        ab_text_train = io.open(folder+current_date+'_corpus_abkhaz.train',"w+", encoding="utf-8")
        ab_train_list = []
        ab_text_valid = io.open(folder+current_date+'_corpus_abkhaz.valid',"w+", encoding="utf-8")
        ab_text_test = io.open(folder+current_date+'_corpus_abkhaz.test',"w+", encoding="utf-8")

        ru_text_train = io.open(folder+current_date+'_corpus_russian.train',"w+", encoding="utf-8")
        ru_train_list = []
        ru_text_valid = io.open(folder+current_date+'_corpus_russian.valid',"w+", encoding="utf-8")
        ru_text_test = io.open(folder+current_date+'_corpus_russian.test',"w+", encoding="utf-8")

    # we process the corpus
    if args.random:
        random.Random(5).shuffle(parallel_text)

    print("\nlines before filtration: "+str(len(parallel_text)))

    if args.only_paraphrase:
        read_splitted_corpus(args.min_length_ratio, args.max_length_ratio, args.min_length, args.max_words, args.verbose, 0, 0, args.punctuation)
    else:
        read_splitted_corpus(args.min_length_ratio, args.max_length_ratio, args.min_length, args.max_words, args.verbose, args.test_lines, args.valid_lines, args.punctuation)

    parallel_corpus = list(zip(ru_train_list,ab_train_list))
    if args.only_paraphrase:
        original_corpus_lines = 0
    else:
        original_corpus_lines = len(parallel_corpus)
    print("\nraw lines: "+str(len(parallel_corpus)))
    print("\nignored lines due to the filter criterion: "+str(ignored_count))
    if args.punctuation:
        print("including sentence order filration: "+str(filtered_punctuations))

    if args.only_paraphrase or args.paraphrase or args.dictionary:
        # we load the dictionaries
        load_ab_ru_dictionary()

    paraphrase_lines = 0
    if args.only_paraphrase or args.paraphrase:
        # we extract the synonyme and paraphrase the corpus
        load_russian_synonyms()
        extract_ab_synonyms()
        for translation_tuple in parallel_corpus:
            parallel_paraphrases[translation_tuple] = {} # dic for russian and abkhaz paraphrases
            generate_paraphrases(translation_tuple)

        save_paraphrases(args.paraphrase_scale, args.only_paraphrase)
        paraphrase_lines = len(ru_train_list) - original_corpus_lines
        print("\nnew paraphrase lines: "+str(paraphrase_lines))

    dictionary_lists = 0
    if args.dictionary:
        generate_lists(args.list_lengths, args.numerate)
        dictionary_lists = len(ru_train_list) - original_corpus_lines - paraphrase_lines
        print("\nadded dictionary lines: "+str(dictionary_lists))

    print("\nwhole lines with paraphrases and dictionary lines: "+str(len(ru_train_list)))

    parallel_corpus = list(zip(ru_train_list, ab_train_list))
    if args.random:
        # we shuffle the training data before we save it
        random.shuffle(parallel_corpus)

    if args.only_paraphrase:
        for sentences in parallel_corpus:
            ru_paraphrase_file.write(sentences[0])
            ab_paraphrase_file.write(sentences[1])
    else:
        for sentences in parallel_corpus:
            ru_text_train.write(sentences[0])
            ab_text_train.write(sentences[1])
