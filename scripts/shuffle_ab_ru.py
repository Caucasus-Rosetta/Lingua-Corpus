import io
import random
import re
import sys, getopt
from zipfile import ZipFile
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
    dirty_sym = re.compile('[0-9-\.№○●:\[\*a-z"▪\?+“\(\)\n\x0A]+')
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
    f1_text = ""
    f2_text = ""
    f3_text = ""
    f4_text = ""
    f5_text = ""
    f6_text = ""   
    for translation_tuple in parallel_corpus[0:-2000]:
            f1_text = f1_text + translation_tuple[0]
            if not translation_tuple[0].endswith("\n"):
                f1_text = f1_text + "\n"
            f4_text = f4_text + translation_tuple[1]
            if not translation_tuple[1].endswith("\n"):
                f4_text = f4_text + "\n"
    for translation_tuple in parallel_corpus[-2000:-500]:
            f2_text = f2_text + translation_tuple[0]
            if not translation_tuple[0].endswith("\n"):
                f2_text = f2_text + "\n"
            f5_text = f5_text + translation_tuple[1]
            if not translation_tuple[1].endswith("\n"):
                f5_text = f5_text + "\n"
    for translation_tuple in parallel_corpus[-500:-1]:
            f3_text = f3_text + translation_tuple[0]
            if not translation_tuple[0].endswith("\n"):
                f3_text = f3_text + "\n"
            f6_text = f6_text + translation_tuple[1]
            if not translation_tuple[1].endswith("\n"):
                f6_text = f6_text + "\n"
    archive = ZipFile('ab_ru_'+str(int(len(parallel_corpus)/1000))+'k.zip', 'w')
    f1 = io.StringIO(f1_text)
    f2 = io.StringIO(f2_text)
    f3 = io.StringIO(f3_text)
    f4 = io.StringIO(f4_text)
    f5 = io.StringIO(f5_text)
    f6 = io.StringIO(f6_text)
    archive.writestr("src-train.txt", f1.getvalue())
    archive.writestr("src-val.txt", f2.getvalue())
    archive.writestr("src-test.txt", f3.getvalue())
    archive.writestr("tgt-train.txt", f4.getvalue())
    archive.writestr("tgt-val.txt", f5.getvalue())
    archive.writestr("tgt-test.txt", f6.getvalue())
    archive.close()

if __name__ == "__main__":
   # main(sys.argv[1:])
   open_parallel_file()
