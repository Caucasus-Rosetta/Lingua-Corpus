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
        temp.append((' '.join(tokenize(tuple[0])),' '.join(tokenize(tuple[1]))))
    return temp

def detokenize_moses(corpus):
    detokenize = MosesDetokenizer('ru')
    temp = []    
    print("\nDetokenizing corpus with moses:")
    for i, tuple in enumerate(tqdm(corpus)):
        temp.append((detokenize(tuple[0].split(' ')),detokenize(tuple[1].split(' '))))
    return temp

def train_sentencepiece(corpus):
    corpus_src, corpus_tgt = zip(*corpus)
    with open('src.txt','w+') as f:
        for t in corpus_src:
            f.write(''.join(str(s) for s in t))
    with open('tgt.txt','w+') as f:
        for t in corpus_tgt:
            f.write(''.join(str(s) for s in t))
    spm.SentencePieceTrainer.Train(input='src.txt', model_prefix='src',vocab_size=32000, model_type='BPE', max_sentence_length=20000, \
                                    normalization_rule_name='nmt_nfkc_cf', character_coverage=1)
    spm.SentencePieceTrainer.Train(input='tgt.txt', model_prefix='tgt',vocab_size=32000, model_type='BPE', max_sentence_length=20000, \
                                    normalization_rule_name='nmt_nfkc_cf', character_coverage=1)
    with ZipFile('sentencepiece_models', 'w') as archive:
        archive.write("src.model")
        archive.write("tgt.model")
        archive.write("src.vocab")
        archive.write("tgt.vocab")
        os.remove("src.txt")
        os.remove("tgt.txt")

def tokenize_sentencepiece(corpus):
    corpus_src, corpus_tgt = zip(*corpus)
    sp_src = spm.SentencePieceProcessor()
    sp_tgt = spm.SentencePieceProcessor()
    sp_src.load("src.model")
    sp_tgt.load("tgt.model")
    print("\nTokenizing corpus with sentencepiece:")
    corpus_src = sp_src.encode(list(corpus_src), out_type=str)
    corpus_tgt = sp_tgt.encode(list(corpus_tgt), out_type=str)
#    out = sp.encode(abkhaz_list, enable_sampling=True, alpha=0.1, nbest_size=-1, out_type=str)
    return list(zip(corpus_src, corpus_tgt))

def detokenize_sentencepiece(corpus):
    corpus_src, corpus_tgt = zip(*corpus)
    sp_src = spm.SentencePieceProcessor()
    sp_tgt = spm.SentencePieceProcessor()
    sp_src.load("src.model")
    sp_tgt.load("tgt.model")
    print("\nDetokenizing corpus with sentencepiece:")
    corpus_src = sp_src.decode(list(corpus_src))
    corpus_tgt = sp_tgt.decode(list(corpus_tgt))
    return list(zip(corpus_src, corpus_tgt))

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
    parallel_corpus = open_list(("ab.txt","ru.txt"))
    dictionary_corpus = open_list(("dictionary.ab","dictionary.ru"))
    paraphrase_corpus = open_list(("paraphrases.ab","paraphrases.ru"))
    parallel_corpus = clean(parallel_corpus[0:4000])    
#    random.shuffle(parallel_corpus)
    parallel_corpus_src, parallel_corpus_tgt = zip(*parallel_corpus)
    dictionary_corpus_src, dictionary_corpus_tgt = zip(*dictionary_corpus)
    paraphrase_corpus_src, paraphrase_corpus_tgt = zip(*paraphrase_corpus)
#    dictionary_corpus_src.extend(parallel_corpus_src)
    import pdb; pdb.set_trace()
    train_sentencepiece()
    train_corpus = tokenize_sentencepiece(dictionary_corpus.extend(parallel_corpus[:-2000]).extend(paraphrase_corpus))
    val_corpus = tokenize_sentencepiece(parallel_corpus[-2000:-500])
    test_corpus = tokenize_sentencepiece(parallel_corpus[-500:-1])
    import pdb; pdb.set_trace()
    zip_data('ab_ru_dev.zip',train_corpus, val_corpus, test_corpus)

process()
