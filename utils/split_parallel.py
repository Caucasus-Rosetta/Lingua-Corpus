import nltk.tokenize.punkt
from os import listdir
from os import path
import re
import io
import shutil
import os

# load the sentence tokenizer
ab_tokenizer = nltk.data.load("abkhaz_tokenizer.pickle")
ru_tokenizer = nltk.data.load("russian.pickle")

ab_files = sorted(listdir('../preprocessed/ab'))
ru_files = sorted(listdir('../preprocessed/ru'))
total_match = 0
total_mismatch = 0
total_tokenized_sentences = 0
try:
    if path.exists('../preprocessed/splitted'):
        shutil.rmtree('../preprocessed/splitted')
    os.mkdir('../preprocessed/splitted')
    if path.exists('../preprocessed/splitted/ab'):
        shutil.rmtree('../preprocessed/splitted/ab')
    os.mkdir('../preprocessed/splitted/ab')
    if path.exists('../preprocessed/splitted/ru'):
        shutil.rmtree('../preprocessed/splitted/ru')
    os.mkdir('../preprocessed/splitted/ru')
except OSError:
    print ("Creation of the directory %s failed" % path)

speech_tokenset = (
"иҳәеит", "рҳәеит", "сҳәеит", "шәҳәеит", "ҳҳәеит", "бҳәеит", "лҳәеит",
"иҳәоит", "рҳәоит", "сҳәоит", "шәҳәоит", "ҳҳәоит", "бҳәоит", "лҳәоит",
"иҳәон", "рҳәон", "сҳәон", "шәҳәон", "ҳҳәон", "бҳәон", "лҳәон",
"ҳәа", "лҳәаит","иҳәит","иӡбит","Дыхәнет","рҳәит", "дҵааит")

acronyms = [
"А.","Ҟ.","Ц.","Ҵ.","У.","К.","Қ.","Е.","Н.","Г.","Ӷ.","Ш.","З.","Ӡ.","Х.","Ҳ.",
"Ҿ.","Ф.","В.","П.","Ԥ.","Р.","Л.","Д.","Ж.","Ҽ.","Џ.","Ч.","Ҷ.","С.","М.","Т.",
"Ҭ.","Ҩ.","Ҟә.","Цә.","Ҵә.","Кә.","Қә.","Гә.","Ӷә.","Шә.","Ӡә.","Хә.","Ҳә.",
"Дә.","Жә.","Тә.","Ҭә.","Ҟь.","Кь.","Қь.","Гь.","Ӷь.","Хь.","Жь.","Џь.","Шь."
]
def ends_with_acronym(sentence):
    for acronym in acronyms:
        if sentence.endswith(acronym):
            return True
    return False

def change_hypen(text):
    '''
    We change all the new lines with hyphens
    '''
    text = text.replace("-\n","")

    return text

remHyphen = re.compile("^ – |^– |^- |^ - ")
upper_lower = re.compile('([ҞЦУКЕНГШӘЗХҾФЫВАПРОЛДЖҼЏЧСМИТЬБҨҴҚӶӠҲԤҶҬ]{2,})([^ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭҞЦУКЕНГШӘЗХҾФЫВАПРОЛДЖҼЏЧСМИТЬБҨҴҚӶӠҲԤҶҬ]+)([ҞЦУКЕНГШӘЗХҾФЫВАПРОЛДЖҼЏЧСМИТЬБҨҴҚӶӠҲԤҶҬ]{2,})')

def correct_sentences(sentences):
    for i,sentence in enumerate(sentences[:]):
        if sentence.startswith(".>>"):
            #the newline should start after ".>>"
            #so we delete the start from the sentence
            sentences[i] = sentence[3:]
            sentence = sentence[3:]
            # and put it to the sentence before
            sentences[i-1] += ".>>"
        if sentence.startswith(">>"):
            #the newline should start after ">>"
            #so we delete the start from the sentence
            sentences[i] = sentence[2:]
            sentence = sentence[2:]
            # and put it to the sentence before
            sentences[i-1] += ">>"
        if sentence.startswith("!»"):
            #the newline should start after "!»"
            #so we delete the start from the sentence
            sentences[i] = sentence[2:]
            sentence = sentence[2:]
            # and put it to the sentence before
            sentences[i-1] += "!»"
        # the sentence should not end with an acronym
        if i+1<len(sentences) and ends_with_acronym(sentence):
            # let us combine those sentences
            sentences[i] = sentence + sentences[i+1]
            # and empty the following sentence in the list
            sentences[i+1] = ""
        if sentence.startswith(speech_tokenset):
            # we combine the speech with the post word of the speech
            sentences[i-1] += sentence
            # and empty the post word
            sentences[i] = ""

    for i,sentence in enumerate(sentences[:]):
        sentences[i] = remHyphen.sub('', sentence)
        sentences[i] = sentence.capitalize()

    if len(sentences) > 0 and sentences[-1] == "":
        del sentences[-1]

    return sentences


def split_parallel_list(file_name,parallel_list):
    global total_mismatch
    global total_match
    global total_tokenized_sentences
    mismatched_paragraphs = 0
    matched_paragraphs = 0
    preprocessed_list = []
    for i, translation_tuple in enumerate(parallel_list):
        ab_sentences = correct_sentences(ab_tokenizer.tokenize(translation_tuple[0]))
        ru_sentences = correct_sentences(ru_tokenizer.tokenize(translation_tuple[1]))

        if len(ab_sentences) != len(ru_sentences):
            # the paragraphs are mismatched
            mismatched_paragraphs += 1

            print("\n")
            print(ab_sentences)
            print(ru_sentences)

        else:
            # the paragraph should be well preprocessed
            matched_paragraphs += 1
            preprocessed_list.extend(list(zip(ab_sentences, ru_sentences)))
    print(file_name+" mismatched "+str(mismatched_paragraphs)+", matched "+str(matched_paragraphs) \
         +" ("+str(round(mismatched_paragraphs*100/(matched_paragraphs+mismatched_paragraphs)))+"%)")
    total_mismatch+=mismatched_paragraphs
    total_match+=matched_paragraphs
    total_tokenized_sentences = total_tokenized_sentences + len(preprocessed_list)
    return preprocessed_list

def open_parallel_file(file_number):
    abkhaz_list = []
    ab_file_name = ab_files[file_number]
    ab_file = io.open('../ab/'+ab_file_name,'r', encoding="utf-8")
    abkhaz_list.extend(ab_file.readlines())

    russian_list = []
    ru_file_name = ru_files[file_number]
    ru_file = io.open('../ru/'+ru_file_name,'r', encoding="utf-8")
    russian_list.extend(ru_file.readlines())

    parallel_corpus = list(zip(abkhaz_list, russian_list))
    return parallel_corpus

print("PARAGRAPHS:")
for i, file_name in enumerate(ab_files):

    parallel_list = open_parallel_file(i)
    preprocessed_list = split_parallel_list(file_name, parallel_list)

    save_file_ab = io.open('../preprocessed/splitted/ab/'+ab_files[i],'w+', encoding="utf-8")
    save_file_ru = io.open('../preprocessed/splitted/ru/'+ru_files[i],'w+', encoding="utf-8")

    for translation_tuple in preprocessed_list:
        save_file_ab.write(translation_tuple[0])
        if not translation_tuple[0].endswith("\n"):
            save_file_ab.write("\n")
        save_file_ru.write(translation_tuple[1])
        if not translation_tuple[1].endswith("\n"):
            save_file_ru.write("\n")
print("Total mismatched "+str(total_mismatch)+", total matched "+str(total_match) \
         +" ("+str(round(total_mismatch*100/(total_match+total_mismatch)))+"%)")
print("SIZE OF PARALLEL CORPUS AFTER TOKENIZING AND FILTERING: "+str(total_tokenized_sentences))
