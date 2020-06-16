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

sp_ab = spm.SentencePieceProcessor()
sp_ru = spm.SentencePieceProcessor()
spm.SentencePieceTrainer.Train('--input=ab.txt,dictionary.ab --model_prefix=ab --vocab_size=4000 --model_type=BPE \
                                --max_sentence_length=20000 --normalization_rule_name=nmt_nfkc_cf \
                                --character_coverage=1')
sp_ab.load("ab.model")
spm.SentencePieceTrainer.Train('--input=ru.txt,dictionary.ru --model_prefix=ru --vocab_size=4000 --model_type=BPE \
                                --max_sentence_length=20000 --normalization_rule_name=nmt_nfkc_cf \
                                --character_coverage=1')
sp_ru.load("ru.model")

def open_parallel_file():
    abkhaz_list = []
    in_ab = io.open('ab.txt','r', encoding="utf-8")
    abkhaz_list.extend(in_ab.readlines())

    russian_list = []
    in_ru = io.open('ru.txt','r', encoding="utf-8")
    russian_list.extend(in_ru.readlines())

    dic_ab_list = []
    dic_ab = io.open('dictionary.ab','r', encoding="utf-8")
    dic_ab_list.extend(dic_ab.readlines())

    dic_ru_list = []
    dic_ru = io.open('dictionary.ru','r', encoding="utf-8")
    dic_ru_list.extend(dic_ru.readlines())

    para_ab_list = []
    para_ab = io.open('paraphrases.ab','r', encoding="utf-8")
    para_ab_list.extend(para_ab.readlines())

    para_ru_list = []
    para_ru = io.open('paraphrases.ru','r', encoding="utf-8")
    para_ru_list.extend(para_ru.readlines())

    parallel_corpus = list(zip(abkhaz_list, russian_list))
    # def get_first(tuple):
        # return len(tuple[0])
    # import pdb; pdb.set_trace()
    # parallel_corpus = sorted(parallel_corpus,key=get_first)
    parallel_corpus = list(dict.fromkeys(parallel_corpus))
    dirty_ab = re.compile('[^ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ]+')
    dirty_ru = re.compile('[^ёйцукенгшщзхъфывапролджэячсмитьбю]+')
    alphabet_ab = re.compile('[ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ]+',re.I)
    alphabet_ru = re.compile('[ёйцукенгшщзхъфывапролджэячсмитьбю]+',re.I)
    def is_dirty(tuple):
        dirty = False
        if (len(dirty_ab.findall(tuple[0])) > 0 and len(alphabet_ab.findall(tuple[0])) == 0) \
        or (len(dirty_ru.findall(tuple[1])) > 0 and len(alphabet_ru.findall(tuple[1])) == 0) \
        or (len(tuple[0])/len(tuple[1]) <= 0.7) \
        or (len(tuple[0])/len(tuple[1]) >= 1.2):
            dirty = True
        return dirty
    tokenize = MosesTokenizer('ru')
    detokenize = MosesDetokenizer('ru')
    def moses_ab(sent):
        temp = tokenize(sent)
        sent = detokenize(temp)
        return " ".join(sp_ab.encode(sent, out_type=str, enable_sampling=True, alpha=0.1, nbest=64))+"\n"
    def moses_ru(sent):
        temp = tokenize(sent)
        sent = detokenize(temp)
        return " ".join(sp_ru.encode(sent, out_type=str, enable_sampling=True, alpha=0.1, nbest=64))+"\n"
    temp = list(parallel_corpus)
    print("\nFiltering data:")
    for translation_tuple in tqdm(parallel_corpus):
        if is_dirty(translation_tuple):
            temp.remove(translation_tuple)
    parallel_corpus = temp
    random.shuffle(parallel_corpus)
    print("-----------------------")
    archive_ab = ZipFile('ab_ru_'+str(int(len(parallel_corpus)/1000))+'k.zip', 'w')
    archive_ru = ZipFile('ru_ab_'+str(int(len(parallel_corpus)/1000))+'k.zip', 'w')
    print("\nProcessing abkhazian dictionary:")
    text_dic_ab = ""
    for line in tqdm(dic_ab_list):
        text_dic_ab = text_dic_ab + moses_ab(line)
    print("\nProcessing russian dictionary:")
    text_dic_ru = ""
    for line in tqdm(dic_ru_list):
        text_dic_ru = text_dic_ru + moses_ru(line)
    print("\nProcessing abkhazian paraphrases:")
    text_para_ab = ""
    for line in tqdm(para_ab_list):
        text_para_ab = text_para_ab + moses_ab(line)
    print("\nProcessing russian paraphrases:")
    text_para_ru = ""
    for line in tqdm(para_ru_list):
        text_para_ru = text_para_ru + moses_ru(line)
    print("\nProcessing training data:")
    text_ab = ""
    text_ru = ""
    for translation_tuple in tqdm(parallel_corpus[0:-2000]):
            text_ab = text_ab + moses_ab(translation_tuple[0])
            text_ru = text_ru + moses_ru(translation_tuple[1])
    ab = io.StringIO(text_dic_ab+text_ab+text_para_ab)
    ru = io.StringIO(text_dic_ru+text_ru+text_para_ru)
    archive_ab.writestr("src-train.txt", ab.getvalue())
    archive_ab.writestr("tgt-train.txt", ru.getvalue())
    archive_ru.writestr("src-train.txt", ru.getvalue())
    archive_ru.writestr("tgt-train.txt", ab.getvalue())
    print("\nProcessing validation data:")
    text_ab = ""
    text_ru = ""
    for translation_tuple in tqdm(parallel_corpus[-2000:-500]):
            text_ab = text_ab + moses_ab(translation_tuple[0])
            text_ru = text_ru + moses_ru(translation_tuple[1])
    ab = io.StringIO(text_ab)
    ru = io.StringIO(text_ru)
    archive_ab.writestr("src-val.txt", ab.getvalue())
    archive_ab.writestr("tgt-val.txt", ru.getvalue())
    archive_ru.writestr("src-val.txt", ru.getvalue())
    archive_ru.writestr("tgt-val.txt", ab.getvalue())
    print("\nProcessing testing data:")
    text_ab = ""
    text_ru = ""
    for translation_tuple in tqdm(parallel_corpus[-500:-1]):
            text_ab = text_ab + moses_ab(translation_tuple[0])
            text_ru = text_ru + moses_ru(translation_tuple[1])
    ab = io.StringIO(text_ab)
    ru = io.StringIO(text_ru)
    archive_ab.writestr("src-test.txt", ab.getvalue())
    archive_ab.writestr("tgt-test.txt", ru.getvalue())
    archive_ru.writestr("src-test.txt", ru.getvalue())
    archive_ru.writestr("tgt-test.txt", ab.getvalue())

    archive_ab.write("ab.model")
    archive_ab.write("ru.model")
    archive_ru.write("ab.model")
    archive_ru.write("ru.model")
    archive_ab.write("ab.vocab")
    archive_ab.write("ru.vocab")
    archive_ru.write("ab.vocab")
    archive_ru.write("ru.vocab")
    archive_ab.close()
    archive_ru.close()
    os.remove("ab.model")
    os.remove("ru.model")
    os.remove("ab.vocab")
    os.remove("ru.vocab")

open_parallel_file()
