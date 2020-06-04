import io
import os
import random
import re
import sys, getopt
from zipfile import ZipFile
import sentencepiece as spm
import time
from tqdm import tqdm

sp_ab = spm.SentencePieceProcessor()
sp_ru = spm.SentencePieceProcessor()
spm.SentencePieceTrainer.Train('--input=ab.txt,dictionary.ab --model_prefix=ab --vocab_size=32000 --model_type=BPE \
                                --normalization_rule_name=nmt_nfkc_cf --max_sentence_length=20000 \
                                --character_coverage=1')
sp_ab.load("ab.model")
spm.SentencePieceTrainer.Train('--input=ru.txt,dictionary.ru --model_prefix=ru --vocab_size=32000 --model_type=BPE \
                                --normalization_rule_name=nmt_nfkc_cf --max_sentence_length=20000 \
                                --character_coverage=1')
sp_ru.load("ru.model")

def open_parallel_file():
    abkhaz_list = []
    in_ab = io.open('ab.txt','r', encoding="utf-8")
    abkhaz_list.extend(in_ab.readlines())

    russian_list = []
    in_ru = io.open('ru.txt','r', encoding="utf-8")
    russian_list.extend(in_ru.readlines())

    parallel_corpus = list(zip(abkhaz_list, russian_list))
    # def get_first(tuple):
        # return len(tuple[0])
#    import pdb; pdb.set_trace()
    parallel_corpus = list(dict.fromkeys(parallel_corpus))
    # parallel_corpus = sorted(parallel_corpus,key=get_first)
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
#            import pdb; pdb.set_trace()
        return dirty
    temp = list(parallel_corpus)
    for translation_tuple in tqdm(parallel_corpus):
        if is_dirty(translation_tuple):
            temp.remove(translation_tuple)
    parallel_corpus = temp
    random.shuffle(parallel_corpus)
    archive_ab = ZipFile('ab_ru_'+str(int(len(parallel_corpus)/1000))+'k.zip', 'w')
    archive_ru = ZipFile('ru_ab_'+str(int(len(parallel_corpus)/1000))+'k.zip', 'w')
    text_ab = ""
    text_ru = ""
    for translation_tuple in tqdm(parallel_corpus):
            text_ab = text_ab + " ".join(sp_ab.EncodeAsPieces(translation_tuple[0].strip()))+"\n"
            text_ru = text_ru + " ".join(sp_ru.EncodeAsPieces(translation_tuple[1].strip()))+"\n"
    ab = io.StringIO(text_ab)
    ru = io.StringIO(text_ru)
    archive_ab.writestr("src-train.txt", ab.getvalue())
    archive_ab.writestr("tgt-train.txt", ru.getvalue())
    archive_ru.writestr("src-train.txt", ru.getvalue())
    archive_ru.writestr("tgt-train.txt", ab.getvalue())
    text_ab = ""
    text_ru = ""
    for translation_tuple in tqdm(parallel_corpus[-2000:-500]):
            text_ab = text_ab + " ".join(sp_ab.EncodeAsPieces(translation_tuple[0].strip()))+"\n"
            text_ru = text_ru + " ".join(sp_ru.EncodeAsPieces(translation_tuple[1].strip()))+"\n"
    ab = io.StringIO(text_ab)
    ru = io.StringIO(text_ru)
    archive_ab.writestr("src-val.txt", ab.getvalue())
    archive_ab.writestr("tgt-val.txt", ru.getvalue())
    archive_ru.writestr("src-val.txt", ru.getvalue())
    archive_ru.writestr("tgt-val.txt", ab.getvalue())
    text_ab = ""
    text_ru = ""
    for translation_tuple in tqdm(parallel_corpus[-500:-1]):
            text_ab = text_ab + " ".join(sp_ab.EncodeAsPieces(translation_tuple[0].strip()))+"\n"
            text_ru = text_ru + " ".join(sp_ru.EncodeAsPieces(translation_tuple[1].strip()))+"\n"
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
