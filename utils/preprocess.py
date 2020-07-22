import io
import os
import random
import re
import sys, getopt
from zipfile import ZipFile, ZIP_DEFLATED
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

def save_list(title, corpus, **kwargs):
    join = True
    for key, value in kwargs.items():
      if key in ['join']:
        join = value
    corpus_src, corpus_tgt = zip(*corpus)
    if join:
        with open(title,'w') as file:
            for i, line in tqdm(enumerate(corpus)):
                file.writelines(line[0].strip()+'\t'+line[1].strip()+'\n')
    else:
        with open('1_'+title,'w') as file:
            for i, line in tqdm(enumerate(corpus)):
                file.writelines(line[0].strip()+'\n')
        with open('2_'+title,'w') as file:
            for i, line in tqdm(enumerate(corpus)):
                file.writelines(line[1].strip()+'\n')

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

def remove_duplicate(test,train):
  temp = list(test)
  for line_test in tqdm(test):
    for line_train in train:
      if line_test[0] == line_train[0] or line_test[1] == line_train[1]:
        try:
          temp.remove(line_test)
        except ValueError:
          pass  # do nothing!
  return temp

def add_tag(tag, corpus):
    corpus_src, corpus_tgt = zip(*corpus)
    corpus_src = list(corpus_src)
    print("\Tagging corpus with "+tag+":")
    for i, line in tqdm(enumerate(corpus_src)):
        corpus_src[i] = tag +" "+ line
    corpus_tgt = list(corpus_tgt)
    return list(zip(corpus_src, corpus_tgt))

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
        temp.append((detokenize(tuple[0].strip().split(' ')),detokenize(tuple[1].strip().split(' '))))
    return temp

def train_sentencepiece(corpus):
    corpus_src, corpus_tgt = zip(*corpus)
    with open('src.txt','w+') as file:
        for line in corpus_src:
            file.writelines(line.strip()+'\n')
    with open('tgt.txt','w+') as file:
        for line in corpus_tgt:
            file.writelines(line.strip()+'\n')
    spm.SentencePieceTrainer.Train(input='src.txt', model_prefix='src',vocab_size=32000, model_type='BPE', max_sentence_length=20000, \
                                    normalization_rule_name='nmt_nfkc_cf', character_coverage=1)
    spm.SentencePieceTrainer.Train(input='tgt.txt', model_prefix='tgt',vocab_size=32000, model_type='BPE', max_sentence_length=20000, \
                                    normalization_rule_name='nmt_nfkc_cf', character_coverage=1)
    with ZipFile('sentencepiece_models.zip', 'w', compression=ZIP_DEFLATED) as archive:
        archive.write("src.model")
        archive.write("tgt.model")
        archive.write("src.vocab")
        archive.write("tgt.vocab")
        os.remove("src.txt")
        os.remove("tgt.txt")

def tokenize_sentencepiece(corpus,**kwargs):
    dropout = False
    for key, value in kwargs.items():
      if key in ['corpus']:
        corpus = value
      elif key in ['dropout']:
        dropout = value
    corpus_src, corpus_tgt = zip(*corpus)
    sp_src = spm.SentencePieceProcessor()
    sp_tgt = spm.SentencePieceProcessor()
    sp_src.load("src.model")
    sp_tgt.load("tgt.model")
    if dropout:
      print("\nTokenizing corpus with sentencepiece(dropout):")
      corpus_src = sp_src.encode(list(corpus_src), enable_sampling=True, alpha=0.1, nbest_size=64, out_type=str)
      corpus_tgt = sp_tgt.encode(list(corpus_tgt), enable_sampling=True, alpha=0.1, nbest_size=64, out_type=str)
    else:
      print("\nTokenizing corpus with sentencepiece:")
      corpus_src = sp_src.encode(list(corpus_src), out_type=str)
      corpus_tgt = sp_tgt.encode(list(corpus_tgt), out_type=str)
    for i in tqdm(range(len(corpus))):
      corpus_src[i] = ' '.join(corpus_src[i])
      corpus_tgt[i] = ' '.join(corpus_tgt[i])
    return list(zip(corpus_src, corpus_tgt))

def detokenize_sentencepiece(corpus):
    corpus_src, corpus_tgt = zip(*corpus)
    sp_src = spm.SentencePieceProcessor()
    sp_tgt = spm.SentencePieceProcessor()
    sp_src.load("src.model")
    sp_tgt.load("tgt.model")
    print("\nDetokenizing corpus with sentencepiece:")
    corpus_src = list(corpus_src)
    corpus_tgt = list(corpus_tgt)
    for i in tqdm(range(len(corpus))):
      corpus_src[i] = corpus_src[i].split(' ')
      corpus_tgt[i] = corpus_tgt[i].split(' ')
    corpus_src = sp_src.decode(corpus_src)
    corpus_tgt = sp_tgt.decode(corpus_tgt)
    return list(zip(corpus_src, corpus_tgt))

def zip_data(title,train_list,val_list,test_list):
    print("\nZipping data:")
    with ZipFile(title, 'w', compression=ZIP_DEFLATED) as archive:
        with open('src-train.txt','w') as file:
            for tuple in train_list:
                file.writelines(tuple[0].strip()+'\n')
        archive.write('src-train.txt')
        os.remove("src-train.txt")
        with open('tgt-train.txt','w') as file:
            for tuple in train_list:
                file.writelines(tuple[1].strip()+'\n')
        archive.write('tgt-train.txt')
        os.remove("tgt-train.txt")
        with open('src-val.txt','w') as file:
            for tuple in val_list:
                file.writelines(tuple[0].strip()+'\n')
        archive.write('src-val.txt')
        os.remove("src-val.txt")
        with open('tgt-val.txt','w') as file:
            for tuple in val_list:
                file.writelines(tuple[1].strip()+'\n')
        archive.write('tgt-val.txt')
        os.remove("tgt-val.txt")
        with open('src-test.txt','w') as file:
            for tuple in test_list:
                file.writelines(tuple[0].strip()+'\n')
        archive.write('src-test.txt')
        os.remove("src-test.txt")
        with open('tgt-test.txt','w') as file:
            for tuple in test_list:
                file.writelines(tuple[1].strip()+'\n')
        archive.write('tgt-test.txt')
        os.remove("tgt-test.txt")
    archive.close()
