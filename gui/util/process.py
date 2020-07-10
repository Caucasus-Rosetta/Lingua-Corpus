import sentencepiece as spm
from mosestokenizer import *
import ctranslate2

def translate(src_list,sp_path_src,sp_path_tgt,ct_path):
    tokenize = MosesTokenizer('ru')
    sp_src = spm.SentencePieceProcessor()
    sp_src.load(sp_path_src)
    for i, text in enumerate(src_list):
        text = ' '.join(tokenize(text)).lower()
        text = sp_src.encode(text, out_type=str)
        src_list[i] = text
    translator = ctranslate2.Translator(ct_path)
    tgt_list = translator.translate_batch(src_list)
    for i, text in enumerate(tgt_list):
        detokenize = MosesDetokenizer('ru')
        sp_tgt = spm.SentencePieceProcessor()
        sp_tgt.load(sp_path_tgt)
        text = sp_tgt.decode(text[0]['tokens'])
        text = detokenize(text.split(' '))
        tgt_list[i] = text
    return tgt_list
