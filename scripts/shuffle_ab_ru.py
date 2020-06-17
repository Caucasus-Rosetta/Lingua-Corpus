import io
import os
import random
import re
import sys, getopt
from zipfile import ZipFile
import sentencepiece as spm
from mosestokenizer import *
import time
from tqdm import tqdm

# a funtion to open bitext files as a tupled list
def open_list(file_tuple):
    tuple0 = []
    tuple1 = []
    with open(file_tuple[0], 'r') as f:
        tuple0.extend(f.readlines())
    with open(file_tuple[1], 'r') as f:
        tuple1.extend(f.readlines())
    return list(zip(tuple0, tuple1))

# a function to clean the text from duplicates and noise
def clean(corpus):
    dirty_ab = re.compile('[^ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ]+')
    dirty_ru = re.compile('[^ёйцукенгшщзхъфывапролджэячсмитьбю]+')
    alphabet_ab = re.compile('[ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ]+',re.I)
    alphabet_ru = re.compile('[ёйцукенгшщзхъфывапролджэячсмитьбю]+',re.I)
    corpus = list(dict.fromkeys(corpus))    
    temp = list(corpus)
    print("\nData filtering:")
    for tuple in tqdm(corpus):
        if (len(dirty_ab.findall(tuple[0])) > 0 and len(alphabet_ab.findall(tuple[0])) == 0) \
        or (len(dirty_ru.findall(tuple[1])) > 0 and len(alphabet_ru.findall(tuple[1])) == 0) \
        or (len(tuple[0])/len(tuple[1]) <= 0.7) \
        or (len(tuple[0])/len(tuple[1]) >= 1.3):
            temp.remove(tuple)
    return temp    
    
def tokenize_moses(corpus):
    tokenize = MosesTokenizer('ru')    
    temp = []    
    print("\nTokenizing corpus with moses:")
    for i, tuple in enumerate(tqdm(corpus)):
        temp.append((tokenize(tuple[0]),tokenize(tuple[1])))
    return temp

def detokenize_moses(corpus):
    detokenize = MosesDetokenizer('ru')
    temp = []    
    print("\nDetokenizing corpus with moses:")
    for i, tuple in enumerate(tqdm(corpus)):
        temp.append((detokenize(tuple[0]),detokenize(tuple[1])))
    return temp

# TODO
def train_sentencepiece(corpus):
    spm.SentencePieceTrainer.Train('--input=ab_sp_train.txt,ab_sp_dic.txt --model_prefix=ab --vocab_size=4000 --model_type=BPE \
                                    --max_sentence_length=20000 --normalization_rule_name=nmt_nfkc_cf \
                                    --character_coverage=1')
    spm.SentencePieceTrainer.Train('--input=ru_sp_train.txt,ru_sp_dic.txt --model_prefix=ru --vocab_size=4000 --model_type=BPE \
                                    --max_sentence_length=20000 --normalization_rule_name=nmt_nfkc_cf \
                                    --character_coverage=1')

    archive.write("ab.model")
    archive.write("ru.model")
    archive.write("ab.vocab")
    archive.write("ru.vocab")
    os.remove("ab.model")
    os.remove("ru.model")
    os.remove("ab.vocab")
    os.remove("ru.vocab")

# TODO
def tokenize_sentencepiece(corpus):
    sp_ab = spm.SentencePieceProcessor()
    sp_ru = spm.SentencePieceProcessor()
    sp_ab.load("ab.model")
    sp_ru.load("ru.model")

# TODO
def detokenize_sentencepiece(corpus):
    sp_ab = spm.SentencePieceProcessor()
    sp_ru = spm.SentencePieceProcessor()
    sp_ab.load("ab.model")
    sp_ru.load("ru.model")

def zip_data(title,train_list,val_list,test_list):
    with ZipFile(title, 'w') as archive:
        with open('src-train.txt','w') as file:
            for tuple in train_list:
                file.writelines(tuple[0])
        archive.write('src-train.txt')
        with open('tgt-train.txt','w') as file:
            for tuple in train_list:            
                file.writelines(tuple[1])
        archive.write('tgt-train.txt')
        with open('src-val.txt','w') as file:
            for tuple in val_list:            
                file.writelines(tuple[0])
        archive.write('src-val.txt')
        with open('tgt-val.txt','w') as file:
            for tuple in val_list:            
                file.writelines(tuple[1])
        archive.write('tgt-val.txt')
        with open('src-test.txt','w') as file:
            for tuple in test_list:            
                file.writelines(tuple[0])
        archive.write('src-test.txt')
        with open('tgt-test.txt','w') as file:
            for tuple in test_list:            
                file.writelines(tuple[1])
        archive.write('tgt-test.txt')
    archive.close()   

def process():
    file_tuple_list = [("ab.txt","ru.txt"),("dictionary.ab","dictionary.ru"),("paraphrases.ab","paraphrases.ru")]
    parallel_corpus = open_list(file_tuple_list[0])
    dictionary_corpus = open_list(file_tuple_list[1])
    paraphrase_corpus = open_list(file_tuple_list[2])
#    random.shuffle(clean(parallel_corpus))
#    parallel_corpus = tokenize_moses(parallel_corpus)
#    parallel_corpus = detokenize_moses(parallel_corpus)
#    dictionary_corpus = tokenize_moses(dictionary_corpus)
#    dictionary_corpus = detokenize_moses(dictionary_corpus)
#    paraphrase_corpus = tokenize_moses(paraphrase_corpus)
#    paraphrase_corpus = detokenize_moses(paraphrase_corpus)
    zip_data('ab_ru_dev.zip',parallel_corpus[0:7000],\
        parallel_corpus[7000:10000],parallel_corpus[10000:11000])
    import pdb; pdb.set_trace()

process()
