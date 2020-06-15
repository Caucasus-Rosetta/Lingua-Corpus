import random
import io
import re

#alphabets with sentence signs
dirty_ab = re.compile('[^ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ\.\:,;\ 0-9-\(\)"!?]+')
dirty_ru = re.compile('[^ёйцукенгшщзхъфывапролджэячсмитьбю\.\:,;\ 0-9-\(\)"!?]+')
alphabet_ab = re.compile('[ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ\.\:,;\ 0-9-\(\)"!?]+',re.I)
alphabet_ru = re.compile('[ёйцукенгшщзхъфывапролджэячсмитьбю\.\:,;\ 0-9-\(\)"!?]+',re.I)

def filter_out(tuple, min_word_ratio, max_word_ratio, min_length, max_words):
    ru_words = 1.0*len(tuple[0].split(" "))
    ab_words = 1.0*len(tuple[1].split(" "))
    # There should be at last one letter of the alphabet
    if (len(dirty_ab.findall(tuple[0].lower())) > 0 and len(alphabet_ab.findall(tuple[0].lower())) == 0) \
    or (len(dirty_ru.findall(tuple[1].lower())) > 0 and len(alphabet_ru.findall(tuple[1].lower())) == 0):
        print("\nno letter:")
        print(tuple)
        return True
    if ru_words/ab_words < min_word_ratio \
    or ru_words/ab_words > max_word_ratio:
        print("\n"+str(ru_words/ab_words)+" is not in the word_ratio scope with "+str(ru_words)+" russian and "+str(ab_words)+ " abkhazian words.")
        print(tuple)
        return True
    if len(tuple[0].split(" ")) > max_words or len(tuple[1].split(" ")) > max_words \
    or len(tuple[0]) < min_length or len(tuple[1]) < min_length:
        print("\ntoo long or too short:")
        print(tuple)
        return True
    return False

parallel_text = io.open('ru-ab-parallel-juni-sorted-date.bifixed',"r+").readlines()

# shuffled_list = parallel_text
# random.shuffle(shuffled_list)

ab_text_train = io.open('corpus_shuffled_abkhaz.train',"w+", encoding="utf-8")
ab_train_list = []
ab_text_valid = io.open('corpus_abkhaz.valid',"w+", encoding="utf-8")
ab_text_test = io.open('corpus_abkhaz.test',"w+", encoding="utf-8")

ru_text_train = io.open('corpus_shuffled_russian.train',"w+", encoding="utf-8")
ru_train_list = []
ru_text_valid = io.open('corpus_russian.valid',"w+", encoding="utf-8")
ru_text_test = io.open('corpus_russian.test',"w+", encoding="utf-8")

ignored_count = 0

for i,sentences in enumerate(parallel_text):
    splitted =  sentences.split("\t")
    if len(splitted) == 2 and not filter_out(splitted, 0.5, 2.5, 10, 50):
        ru_sentence = splitted[0]
        ab_sentence = splitted[1]
        if i <= 500:
            ab_text_valid.write(ab_sentence)
            ru_text_valid.write(ru_sentence+"\n")
        elif i<=1000 and i > 500:
            ab_text_test.write(ab_sentence)
            ru_text_test.write(ru_sentence+"\n")
        else:
            ab_train_list.append(ab_sentence)
            ru_train_list.append(ru_sentence+"\n")
    else:
        ignored_count += 1

# we shuffle the training data before we save it
random.shuffle(ru_train_list)
random.shuffle(ab_train_list)

for ru_sentence in ru_train_list:
    ru_text_train.write(ru_sentence)

for ab_sentence in ab_train_list:
    ab_text_train.write(ab_sentence)

print("\nignored lines: "+str(ignored_count))
