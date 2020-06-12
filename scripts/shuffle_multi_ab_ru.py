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

sp = spm.SentencePieceProcessor()
spm.SentencePieceTrainer.Train('--input=ab.txt,dictionary.ab,ru.txt,dictionary.ru --model_prefix=ab-ru --vocab_size=32000 --model_type=BPE \
                                --max_sentence_length=20000 \
                                --character_coverage=1')
sp.load("ab-ru.model")

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
    normalize = MosesPunctuationNormalizer('ru')
    tokenize = MosesTokenizer('ru')
    def moses(sent):
        sent = normalize(sent)
        temp = tokenize(sent)
        for i, item in enumerate(temp):
            temp[i] = " ".join(sp.EncodeAsPieces(item))
        return " ".join(temp)+"\n"
    temp = list(parallel_corpus)
    print("\nFiltering data:")
    for translation_tuple in tqdm(parallel_corpus):
        if is_dirty(translation_tuple):
            temp.remove(translation_tuple)
    parallel_corpus = temp
    random.shuffle(parallel_corpus)
    print("-----------------------")
    archive = ZipFile('ab_ru_'+str(int(len(parallel_corpus)/1000))+'k.zip', 'w')
    print("\nProcessing abkhazian dictionary:")
    text_dic_ab_src = ""
    text_dic_ab_tgt = ""
    for line in tqdm(dic_ab_list):
        ab_tok = moses(line)
        text_dic_ab_src = text_dic_ab_src + "__opt_src_ab __opt_tgt_ru " + ab_tok
        text_dic_ab_tgt = text_dic_ab_tgt + ab_tok
    print("\nProcessing russian dictionary:")
    text_dic_ru_src = ""
    text_dic_ru_tgt = ""
    for line in tqdm(dic_ru_list):
        ru_tok = moses(line)
        text_dic_ru_src = text_dic_ru_src + "__opt_src_ru __opt_tgt_ab " + ru_tok
        text_dic_ru_tgt = text_dic_ru_tgt + ru_tok
    print("\nProcessing abkhazian paraphrases:")
    text_para_ab_src = ""
    text_para_ab_tgt = ""
    for line in tqdm(para_ab_list):
        ab_tok = moses(line)
        text_para_ab_src = text_para_ab_src + "__opt_src_ab __opt_tgt_ru " + ab_tok
        text_para_ab_tgt = text_para_ab_tgt + ab_tok
    print("\nProcessing russian paraphrases:")
    text_para_ru_src = ""
    text_para_ru_tgt = ""
    for line in tqdm(para_ru_list):
        ru_tok = moses(line)
        text_para_ru_src = text_para_ru_src + "__opt_src_ru __opt_tgt_ab " + ru_tok
        text_para_ru_tgt = text_para_ru_tgt + ru_tok
    print("\nProcessing training data:")
    text_ab_src = ""
    text_ru_src = ""
    text_ab_tgt = ""
    text_ru_tgt = ""
    for translation_tuple in tqdm(parallel_corpus[0:-2000]):
            ab_tok = moses(translation_tuple[0])
            ru_tok = moses(translation_tuple[1])
            text_ab_src = text_ab_src + "__opt_src_ab __opt_tgt_ru " + ab_tok
            text_ru_src = text_ru_src + "__opt_src_ru __opt_tgt_ab " + ru_tok
            text_ab_tgt = text_ab_tgt + ab_tok
            text_ru_tgt = text_ru_tgt + ru_tok
    src = io.StringIO(text_dic_ab_src+text_ab_src+text_para_ab_src+text_dic_ru_src+text_ru_src+text_para_ru_src)
    tgt = io.StringIO(text_dic_ru_tgt+text_ru_tgt+text_para_ru_tgt+text_dic_ab_tgt+text_ab_tgt+text_para_ab_tgt)
    archive.writestr("src-train.txt", src.getvalue())
    archive.writestr("tgt-train.txt", tgt.getvalue())
    print("\nProcessing validation data:")
    text_ab_src = ""
    text_ru_src = ""
    text_ab_tgt = ""
    text_ru_tgt = ""
    for translation_tuple in tqdm(parallel_corpus[-2000:-500]):
            ab_tok = moses(translation_tuple[0])
            ru_tok = moses(translation_tuple[1])
            text_ab_src = text_ab_src + "__opt_src_ab __opt_tgt_ru " + ab_tok
            text_ru_src = text_ru_src + "__opt_src_ru __opt_tgt_ab " + ru_tok
            text_ab_tgt = text_ab_tgt + ab_tok
            text_ru_tgt = text_ru_tgt + ru_tok
    src = io.StringIO(text_ab_src+text_ru_src)
    tgt = io.StringIO(text_ru_tgt+text_ab_tgt)
    archive.writestr("src-val.txt", src.getvalue())
    archive.writestr("tgt-val.txt", tgt.getvalue())
    print("\nProcessing testing data:")
    text_ab_src = ""
    text_ru_src = ""
    text_ab_tgt = ""
    text_ru_tgt = ""
    for translation_tuple in tqdm(parallel_corpus[-500:-1]):
            ab_tok = moses(translation_tuple[0])
            ru_tok = moses(translation_tuple[1])
            text_ab_src = text_ab_src + "__opt_src_ab __opt_tgt_ru " + ab_tok
            text_ru_src = text_ru_src + "__opt_src_ru __opt_tgt_ab " + ru_tok
            text_ab_tgt = text_ab_tgt + ab_tok
            text_ru_tgt = text_ru_tgt + ru_tok
    src = io.StringIO(text_ab_src+text_ru_src)
    tgt = io.StringIO(text_ru_tgt+text_ab_tgt)
    archive.writestr("src-test.txt", src.getvalue())
    archive.writestr("tgt-test.txt", tgt.getvalue())

    archive.write("ab-ru.model")
    archive.write("ab-ru.vocab")
    archive.close()
    os.remove("ab-ru.model")
    os.remove("ab-ru.vocab")

open_parallel_file()
