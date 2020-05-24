import io
import random

inputfile = ''
outputfile = 'output.txt'
language = ''

def main(argv):
   global inputfile
   global outputfile
   global language
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print('shuffle_ab_ru.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('shuffle_ab_ru.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg

def open_parallel_file():
    out_ab = io.open('output_shuffled ab.txt','w+', encoding="utf-8")
    out_ru = io.open('output_shuffled ru.txt','w+', encoding="utf-8")
    abkhaz_list = []
    in_ab = io.open('output ab.txt','r', encoding="utf-8")
    abkhaz_list.extend(in_ab.readlines())

    russian_list = []
    in_ru = io.open('output ru.txt','r', encoding="utf-8")
    russian_list.extend(in_ru.readlines())

    parallel_corpus = list(zip(abkhaz_list, russian_list))
    random.shuffle(parallel_corpus)
    for translation_tuple in parallel_corpus:
        out_ab.write(translation_tuple[0])
        if not translation_tuple[0].endswith("\n"):
            out_ab.write("\n")
        out_ru.write(translation_tuple[1])
        if not translation_tuple[1].endswith("\n"):
            out_ru.write("\n")

open_parallel_file()
