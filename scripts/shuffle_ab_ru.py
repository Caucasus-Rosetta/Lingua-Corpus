import io
import random
import re
import sys, getopt
inputfile = ["",""]
outputfile = ['output ab.txt', 'output ru.txt']

def main(argv):
   global inputfile
   global outputfile
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifiles=","ofiles="])
   except getopt.GetoptError:
      print('shuffle_ab_ru.py -i <inputfiles> -o <outputfiles>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('shuffle_ab_ru.py -i <inputfiles> -o <outputfiles>')
         sys.exit()
      elif opt in ("-i", "--ifiles"):
         inputfile[0] = argv[1]
         inputfile[1] = argv[2]
      elif opt in ("-o", "--ofiles"):
         outputfile[0] = argv[1]
         outputfile[1] = argv[2]
         import pdb; pdb.set_trace()
count = 0
def open_parallel_file():
    out_ab = io.open('../output_shuffled ab.txt','w+', encoding="utf-8")
    out_ru = io.open('../output_shuffled ru.txt','w+', encoding="utf-8")
    abkhaz_list = []
    in_ab = io.open('../ab.txt','r', encoding="utf-8")
    abkhaz_list.extend(in_ab.readlines())

    russian_list = []
    in_ru = io.open('../ru.txt','r', encoding="utf-8")
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
        global count
        dirty = False
        if (len(dirty_sym.findall(translation_tuple[0])) > 0 and len(alphabet_ab.findall(translation_tuple[0])) == 0) \
        or (len(dirty_sym.findall(translation_tuple[1])) > 0 and len(alphabet_ru.findall(translation_tuple[1])) == 0) \
        or (len(translation_tuple[0])/len(translation_tuple[1]) <= 0.7) \
        or (len(translation_tuple[0])/len(translation_tuple[1]) >= 1.2):
            dirty = True
            count = count + 1
            print(count)
#            import pdb; pdb.set_trace()
        return dirty
    for translation_tuple in parallel_corpus:
        if is_dirty(translation_tuple):
            parallel_corpus.remove(translation_tuple)
    for translation_tuple in parallel_corpus:
            out_ab.write(translation_tuple[0])
            if not translation_tuple[0].endswith("\n"):
                out_ab.write("\n")
            out_ru.write(translation_tuple[1])
            if not translation_tuple[1].endswith("\n"):
                out_ru.write("\n")

if __name__ == "__main__":
   # main(sys.argv[1:])
   open_parallel_file()
