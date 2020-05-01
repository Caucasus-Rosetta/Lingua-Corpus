from synonyms import abkhaz_synonyms, russian_synonyms
from os import listdir
import io
import random

'''
The dictionary abkhazian_paraphrases is structured like {
"original sentence":["paraphrase1","paraphrase2"],
"original sentence2":["paraphrase sentence2","second paraphrase"]
}
'''

# we exlude the validation and test set
#exclude_text = ["parliament ru","parliament ab","constitution ab","constitution ru"]
exclude_text = ["shuffled_abkhaz.test","shuffled_abkhaz.valid", "shuffled_russian.test", "shuffled_russian.valid"]
parallel_corpus = [] #list of translation tuples
parallel_paraphrases = {} # dictionary of paraphrases with translation tuples as keys

def exchange_synonym(synonym_key, synonyms,translation_tuple, tuple_index, language):
    global parallel_paraphrases
    paraphrases = []
    # search and exchange the synonym
    # the search space could be advanced to the start and end of the sentence
    # how can we make this case sensitive?
    if " "+synonym_key+" " in translation_tuple[tuple_index]:
        # we have found a match
        for i,synonym in enumerate(synonyms[synonym_key]):
            if len(paraphrases) == i:
                paraphrases.append(translation_tuple[tuple_index][:])
            if " "+synonym_key+" " in paraphrases[i]:
                paraphrases[i] = paraphrases[i].replace(" "+synonym_key+" ", " "+synonym+" ")
    if len(paraphrases) > 0:
        parallel_paraphrases[translation_tuple][language] = paraphrases

def generate_paraphrases(translation_tuple):
    global parallel_paraphrases
    parallel_paraphrases[translation_tuple]["abkhaz"] = []
    for synonym_key in abkhaz_synonyms.keys():
        exchange_synonym(synonym_key, abkhaz_synonyms, translation_tuple, 0, "abkhaz")

    parallel_paraphrases[translation_tuple]["russian"] = []
    for synonym_key in russian_synonyms.keys():
        exchange_synonym(synonym_key, russian_synonyms, translation_tuple, 0, "russian")

source_folder = "../cleaned"
def open_parallel_corpus():
    global parallel_corpus
    abkhaz_list = []
    for file_name in sorted(listdir(source_folder+'/ab')):
        if file_name not in exclude_text:
            file = io.open(source_folder+'/ab/'+file_name,'r', encoding="utf-8")
            abkhaz_list.extend(file.readlines())

    russian_list = []
    for file_name in sorted(listdir(source_folder+'/ru')):
        if file_name not in exclude_text:
            file = io.open(source_folder+'/ru/'+file_name,'r', encoding="utf-8")
            russian_list.extend(file.readlines())

    parallel_corpus = list(zip(russian_list, abkhaz_list))

def fill_list(list_to_fill, filler, length_to_align, max_length=3):
    length_to_fill = min(length_to_align, max_length)
    for fill in range(length_to_fill-len(list_to_fill)):
        list_to_fill.append(filler)
    return list_to_fill[:length_to_fill]

def save_paraphrases():
    russian_outputfile = open('../draft/paraphrases ru',"w+")
    abkhaz_outputfile = open('../draft/paraphrases ab',"w+")
    for translation_tuple in parallel_paraphrases:
        abkhazian_paraphrases = parallel_paraphrases[translation_tuple]["abkhaz"] or []
        russian_paraphrases = parallel_paraphrases[translation_tuple]["russian"] or []
        max_paraphrase_length = max(len(russian_paraphrases), len(abkhazian_paraphrases))
        # we fill the list to the same length
        abkhazian_paraphrases = fill_list(abkhazian_paraphrases, translation_tuple[0], max_paraphrase_length)
        russian_paraphrases = fill_list(russian_paraphrases, translation_tuple[1], max_paraphrase_length)
        # and shuffle the result
        random.shuffle(abkhazian_paraphrases)
        random.shuffle(russian_paraphrases)

        '''
        # we only take the minimal amount of paraphrases
        # this only works if there many paraphrases on both sides for one translation
        # min_paraphrases = min(len(abkhazian_paraphrases), len(russian_paraphrases))
        '''
        print(str(len(russian_paraphrases))+" : "+str(len(abkhazian_paraphrases)))
        russian_outputfile.writelines(russian_paraphrases)
        abkhaz_outputfile.writelines(abkhazian_paraphrases)

open_parallel_corpus()
print("raw lines: "+str(len(parallel_corpus)))

for translation_tuple in parallel_corpus:
    parallel_paraphrases[translation_tuple] = {} # dic for russian and abkhaz paraphrases
    generate_paraphrases(translation_tuple)

save_paraphrases()
