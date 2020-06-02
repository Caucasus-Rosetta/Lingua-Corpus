import io
import random
import re
import sys, getopt
from zipfile import ZipFile
import sentencepiece as spm
import time
from tqdm import tqdm
from os import path

sp_ab = spm.SentencePieceProcessor()
sp_ru = spm.SentencePieceProcessor()
if not path.exists("ab.model"):
    spm.SentencePieceTrainer.Train('--input=ab.txt --model_prefix=ab --vocab_size=4000 --model_type=BPE')
    sp_ab.load("ab.model")
else:
    sp_ab.load("ab.model")
if not path.exists("ru.model"):
    spm.SentencePieceTrainer.Train('--input=ru.txt --model_prefix=ru --vocab_size=4000 --model_type=BPE')
    sp_ru.load("ru.model")
else:
    sp_ru.load("ru.model")

def open_parallel_file():
    abkhaz_list = []
    in_ab = io.open('ab.txt','r', encoding="utf-8")
    abkhaz_list.extend(in_ab.readlines())

    russian_list = []
    in_ru = io.open('ru.txt','r', encoding="utf-8")
    russian_list.extend(in_ru.readlines())

    parallel_corpus = list(zip(abkhaz_list, russian_list))
    def get_first(tuple):
        return len(tuple[0])
#    import pdb; pdb.set_trace()
    parallel_corpus = list(dict.fromkeys(parallel_corpus))
    parallel_corpus = sorted(parallel_corpus,key=get_first)
    random.shuffle(parallel_corpus)
    dirty_sym = re.compile('[0-9-\.№○●:\[\*a-z"▪\?+“\(\)\n]+')
    alphabet_ab = re.compile('[ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ]+',re.I)
    alphabet_ru = re.compile('[ёйцукенгшщзхъфывапролджэячсмитьбю]+',re.I)
    def is_dirty(tuple):
        dirty = False
        if (len(dirty_sym.findall(translation_tuple[0])) > 0 and len(alphabet_ab.findall(translation_tuple[0])) == 0) \
        or (len(dirty_sym.findall(translation_tuple[1])) > 0 and len(alphabet_ru.findall(translation_tuple[1])) == 0) \
        or (len(translation_tuple[0])/len(translation_tuple[1]) <= 0.7) \
        or (len(translation_tuple[0])/len(translation_tuple[1]) >= 1.2):
            dirty = True
#            import pdb; pdb.set_trace()
        return dirty
    for translation_tuple in tqdm(parallel_corpus):
        if is_dirty(translation_tuple):
            parallel_corpus.remove(translation_tuple)
    text_ab = ""
    text_ru = ""
    archive = ZipFile('ab_ru_'+str(int(len(parallel_corpus)/1000))+'k.zip', 'w')
    for translation_tuple in tqdm(parallel_corpus[0:-2000]):
            text_ab = text_ab + " ".join(sp_ab.EncodeAsPieces(translation_tuple[0].strip()))+"\n"
            text_ru = text_ru + " ".join(sp_ru.EncodeAsPieces(translation_tuple[1].strip()))+"\n"
    ab = io.StringIO(text_ab)
    ru = io.StringIO(text_ru)
    archive.writestr("src-train.txt", ab.getvalue())
    archive.writestr("tgt-train.txt", ru.getvalue())
    text_ab = ""
    text_ru = ""
    for translation_tuple in tqdm(parallel_corpus[-2000:-500]):
            text_ab = text_ab + " ".join(sp_ab.EncodeAsPieces(translation_tuple[0].strip()))+"\n"
            text_ru = text_ru + " ".join(sp_ru.EncodeAsPieces(translation_tuple[1].strip()))+"\n"
    ab = io.StringIO(text_ab)
    ru = io.StringIO(text_ru)
    archive.writestr("src-val.txt", ab.getvalue())
    archive.writestr("tgt-val.txt", ru.getvalue())
    text_ab = ""
    text_ru = ""
    for translation_tuple in tqdm(parallel_corpus[-500:-1]):
            text_ab = text_ab + " ".join(sp_ab.EncodeAsPieces(translation_tuple[0].strip()))+"\n"
            text_ru = text_ru + " ".join(sp_ru.EncodeAsPieces(translation_tuple[1].strip()))+"\n"
    ab = io.StringIO(text_ab)
    ru = io.StringIO(text_ru)
    archive.writestr("src-test.txt", ab.getvalue())
    archive.writestr("tgt-test.txt", ru.getvalue())
    archive.close()

open_parallel_file()
