import nltk.tokenize.punkt
from os import listdir
from os import path
import re
import io
import shutil
import os
import sys, getopt

# load the sentence tokenizer
ab_tokenizer = nltk.data.load("abkhaz_tokenizer.pickle")
ru_tokenizer = nltk.data.load("russian.pickle")

speech_tokenset = (
"иҳәеит", "рҳәеит", "сҳәеит", "шәҳәеит", "ҳҳәеит", "бҳәеит", "лҳәеит",
"иҳәоит", "рҳәоит", "сҳәоит", "шәҳәоит", "ҳҳәоит", "бҳәоит", "лҳәоит",
"иҳәон", "рҳәон", "сҳәон", "шәҳәон", "ҳҳәон", "бҳәон", "лҳәон",
"ҳәа", "лҳәаит","иҳәит","иӡбит","Дыхәнет","рҳәит", "дҵааит")

acronyms = [
"А.","Ҟ.","Ц.","Ҵ.","У.","К.","Қ.","Е.","Н.","Г.","Ӷ.","Ш.","З.","Ӡ.","Х.","Ҳ.",
"Ҿ.","Ф.","В.","П.","Ԥ.","Р.","Л.","Д.","Ж.","Ҽ.","Џ.","Ч.","Ҷ.","С.","М.","Т.",
"Ҭ.","Ҩ.","Ҟә.","Цә.","Ҵә.","Кә.","Қә.","Гә.","Ӷә.","Шә.","Ӡә.","Хә.","Ҳә.",
"Дә.","Жә.","Тә.","Ҭә.","Ҟь.","Кь.","Қь.","Гь.","Ӷь.","Хь.","Жь.","Џь.","Шь."
]

inputfile = ''
outputfile = 'output.txt'
language = ''

def main(argv):
   global inputfile
   global outputfile
   global language
   try:
      opts, args = getopt.getopt(argv,"hi:o:l:",["ifile=","ofile=","lang="])
   except getopt.GetoptError:
      print('tokenize_ab_ru.py -i <inputfile> -o <outputfile> -l <languagecode>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('tokenize_ab_ru.py -i <inputfile> -o <outputfile> -l <languagecode>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
      elif opt in ("-l", "--lang"):
         language = arg
def ends_with_acronym(sentence):
    for acronym in acronyms:
        if sentence.endswith(acronym):
            return True
    return False

def change_hypen(text):
    '''
    We change all the new lines with hyphens
    '''
    text = text.replace("-\n","")

    return text

remHyphen = re.compile("^ – |^– |^- |^ - ")
upper_lower = re.compile('([ҞЦУКЕНГШӘЗХҾФЫВАПРОЛДЖҼЏЧСМИТЬБҨҴҚӶӠҲԤҶҬ]{2,})([^ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭҞЦУКЕНГШӘЗХҾФЫВАПРОЛДЖҼЏЧСМИТЬБҨҴҚӶӠҲԤҶҬ]+)([ҞЦУКЕНГШӘЗХҾФЫВАПРОЛДЖҼЏЧСМИТЬБҨҴҚӶӠҲԤҶҬ]{2,})')

def correct_sentences(sentences):
    for i,sentence in enumerate(sentences[:]):
    	if sentence.startswith("!»"):
    		#the newline should start after "!»"
    		#so we delete the start from the sentence
    		sentences[i] = sentence[2:]
    		sentence = sentence[2:]
    		# and put it to the sentence before
    		sentences[i-1] += "!»"
    	# the sentence should not end with an acronym
    	if i+1<len(sentences) and ends_with_acronym(sentence):
    		# let us combine those sentences
    		sentences[i] = sentence + sentences[i+1]
    		# and empty the following sentence in the list
    		sentences[i+1] = ""
    	if sentence.startswith(speech_tokenset):
    		# we combine the speech with the post word of the speech
    		sentences[i-1] += sentence
    		# and empty the post word
    		sentences[i] = ""

    for i,sentence in enumerate(sentences[:]):
        sentences[i] = remHyphen.sub('', sentence)
        sentences[i] = sentence.capitalize()

    return sentences


if __name__ == "__main__":
   main(sys.argv[1:])
   infile = io.open(inputfile,'r', encoding="utf-8")
   content = infile.read()
   if language == "ab":
      content = correct_sentences(ab_tokenizer.tokenize(content))
   elif language == "ru":
      content = correct_sentences(ru_tokenizer.tokenize(content))
   outfile = io.open(outputfile,'w', encoding="utf-8")
   for line in content:
      outfile.write(line+"\n")
