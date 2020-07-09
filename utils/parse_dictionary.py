# -*- coding: utf_8 -*-
from pdfminer import high_level
from pdfminer.layout import LAParams
from lxml import etree, html
from io import StringIO, BytesIO
from pathlib import Path
import re
import unicodedata

'''
 to recreate the html layout, get the pdf files from:
wget http://apsnyteka.org/file/Kaslandziya_V_Dzhonua_B_Russko_abkhazsky_slovar-I_2016.pdf
wget http://apsnyteka.org/file/Kaslandzia_Dzhonua_Russko_abkhazsky_slovar_II_2016.pdf
wget http://apsnyteka.org/file/Kaslandziya_V_Dzhonua_Russko_abkhazsky_slovar_III_2019.pdf

and delete tom1.html tom2.html tom3.html
'''

# we are gonna convert the dictionary into parallel lists
ru_list = []
ab_list = []
cyrillic_encoding = 'utf-8' #"windows-1251"
with open('../draft/dictionary_prescript.ru', 'r+',encoding=cyrillic_encoding) as f:
    dictionary_prescript = f.read().splitlines()

ru_output = open('../draft/dictionary.ru', 'w+',encoding=cyrillic_encoding)
ab_output = open('../draft/dictionary.ab', 'w+',encoding=cyrillic_encoding)

comparable_output = open('comparable_dictionary_output.txt', 'w+',encoding=cyrillic_encoding)
searchable_output = open('searchable_unaccented_dictionary.txt', 'w+',encoding=cyrillic_encoding)
# the script will not match all translations
skipped_translations = open('skipped_translations.txt', 'w+',encoding=cyrillic_encoding)

messy_accents = {
'а́': 'a',
'ѝ': 'и',
'и́': 'и',
'о́': 'о',
'я́': 'я',
'у́':'y',
'ы́': 'ы',
'е́':'e',
'ю́':'ю'
}

numbers = ["1","2","3","4","5","6","7","8","9","- ", "."]


# ignore messy pairs, mostly missmatched synonyms or bad formation
messy_russian_words = ["звучание)","навaривать","обдавaть","обдавaться",
"дурeнь","минyтка","наварить","навёртываться","иркымпылны","льный","тный",
"гательный","– в –","– з –","на вкус","коль","коли",
"опорожнять","опорожнить","опорожняться","опорожниться",
"зыбко; зыбче","зыбко","зыбче",
"инжирный и инжировый","инжирный","инжировый",
"лю́тый и люто́й",
"лютый и лютой",
"лютый и лютoй","лютый","лютoй",
"навряд","навряд ли","вряд ли",
"стaртер","стартёр","стaртер и стартёр",
"стaртерный и стартёрный","стaртерный","стартёрный",
"чeрви и чeрвы","чeрви","чeрвы",
"игрeц","трaпеза",
"трёхлeток","у́ксусник","полюбовник",
"нумизмaтика ж","сам (","стерильность ж"
]

# convert the pdfs into html files
# Specify how much a horizontal and vertical position of a text matters when determining the order of text boxes.
# The value should be within the range of -1.0 (only horizontal position matters) to +1.0 (only vertical position matters).
vertical_flow = 0.8925
cyrillic_codec = None #"ISO-8859-5" #"'utf-8' "iso8859_5"
tom1html = "empty"
if Path("tom1.html").exists():
    tom1html = open("tom1.html").read()
else:
    tom1output = StringIO()
    with open('Kaslandziya_V_Dzhonua_B_Russko_abkhazsky_slovar-I_2016.pdf', 'rb') as fin:
      high_level.extract_text_to_fp(fin, tom1output, laparams=LAParams(boxes_flow=vertical_flow), output_type='html', codec=cyrillic_codec)

    with open('tom1.html', mode='w') as f:
        print(tom1output.getvalue(), file=f)

    tom1html = tom1output.getvalue()

tom2html = "empty"
if Path("tom2.html").exists():
    tom2html = open("tom2.html").read()
else:
    tom2output = StringIO()
    with open('Kaslandzia_Dzhonua_Russko_abkhazsky_slovar_II_2016.pdf', 'rb') as fin:
      high_level.extract_text_to_fp(fin, tom2output, laparams=LAParams(boxes_flow=vertical_flow), output_type='html', codec=cyrillic_codec)

    with open('tom2.html', mode='w') as f:
        print(tom2output.getvalue(), file=f)

    tom2html = tom2output.getvalue()

tom3html = "empty"
if Path("tom3.html").exists():
    tom3html = open("tom3.html").read()
else:
    tom3output = StringIO()
    with open('Kaslandziya_V_Dzhonua_Russko_abkhazsky_slovar_III_2019.pdf', 'rb') as fin:
      high_level.extract_text_to_fp(fin, tom3output, laparams=LAParams(boxes_flow=vertical_flow), output_type='html', codec=cyrillic_codec)

    with open('tom3.html', mode='w') as f:
        print(tom3output.getvalue(), file=f)

    tom3html = tom3output.getvalue()

parser = etree.HTMLParser()
parsedHTML1 = html.document_fromstring(tom1html)
parsedHTML2 = html.document_fromstring(tom2html)
parsedHTML3 = html.document_fromstring(tom3html)

def strip_accents(text):
    for accent in messy_accents.keys():
        text = text.replace(accent, messy_accents[accent])
    return text

def strip_clips(node_text):
    node_text = node_text.replace("<br>"," ").replace("\n"," ")
    node_text = re.sub('\([^\)]+\)', '', node_text)
    node_text = node_text.strip()
    return node_text

def get_following_text(node, boldspans):
    node_translation = ""
    siblings = list(node.itersiblings()) + node.getparent().getnext().getchildren() + node.getparent().getnext().getnext().getchildren()
    for sibling in siblings:
        if sibling.text and sibling.text.replace("\n","").strip().isdigit() and sibling in boldspans:
            #sibling is the page number
            continue
        if sibling in boldspans:
            #sibling is the next entry
            break

        # we filter the empty and cursiv texts
        # we leave the synonyms with "см." to filter them completly
        if sibling.text and (not "Italic" in sibling.attrib['style'] or "см." in sibling.text):
            node_translation += " "+sibling.text_content()

    return strip_clips(node_translation)

#alphabets
dirty_ab = re.compile('[^ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ]+')
dirty_ru = re.compile('[^ёйцукенгшщзхъфывапролджэячсмитьбю]+')
alphabet_ab = re.compile('[ҟцукенгшәзхҿфывапролджҽџчсмитьбҩҵқӷӡҳԥҷҭ]+',re.I)
alphabet_ru = re.compile('[ёйцукенгшщзхъфывапролджэячсмитьбю]+',re.I)

def is_abkhazian_alphabet(node_text):
    # There should be at last one letter of the alphabet
    if (len(dirty_ab.findall(node_text.lower())) > 0 and len(alphabet_ab.findall(node_text.lower())) == 0):
        print("\nno letter:")
        print(node_text)
        return False
    return True

def is_russian_alphabet(node_text):
    # There should be at last one letter of the alphabet
    if (len(dirty_ru.findall(node_text.lower())) > 0 and len(alphabet_ru.findall(node_text.lower())) == 0):
        print("\nno letter:")
        print(node_text)
        return False
    return True

def extract_parallel_text(boldspan, boldspans):
    ru_word = boldspan.text.replace("\n","").strip()
    ru_word_accent = ru_word
    ru_word = strip_accents(ru_word)
    if ru_word and len(ru_word)>3 and not ru_word.isdigit() and not "..." in ru_word and not "◊" in ru_word and not "," in ru_word and not "." in ru_word and not ru_word in dictionary_prescript and not (ru_word in messy_russian_words):
        word_translations = get_following_text(boldspan, boldspans)
        word_translations  = re.split(';|;|,|,|,|1|2|3|4|5|6|7|8|9|0',word_translations)
        #print(word_translations)
        for translation in word_translations:
            if translation.strip() and not "см." in translation and not "..." in translation and not "◊" in translation and not "?" in translation and not "…" in translation and not ")" in translation and not "(" in translation and not "-" in translation:
                ab_translation = translation.split(":")[0]
                for number in numbers:
                    ab_translation = ab_translation.replace(number, "")
                ab_translation = ab_translation.strip()
                # only save certain translations and no messy pairs
                '''
                if not len(ab_translation)>3:
                    print(ab_translation)
                '''
                if ab_translation and len(ab_translation)>3 and len(ab_translation.split(" "))<=2 and not (ru_word in messy_russian_words) and is_russian_alphabet(ru_word) and is_abkhazian_alphabet(ab_translation):# and not [ru_word, ab_translation] in messy_pairs:
                    # we leave the accents for comparison with the original
                    searchable_output.write(ru_word_accent + "\t:\t" + ab_translation+"\n")
                    # we try to convert the accents
                    ab_translation = strip_accents(ab_translation)

                    #write the extracted translation to the files

                    ru_list.append(ru_word)
                    ab_list.append(ab_translation)
                    ru_output.write(ru_word+"\n")
                    ab_output.write(ab_translation+"\n")
                    comparable_output.write(ru_word + "\t:\t" + ab_translation+"\n")
    else:
        if not ru_word.isdigit() and not ru_word in dictionary_prescript:
            skipped_translations.write(ru_word + "\n")


# find the bold start of the translations from Tom1
boldspansTom1 = parsedHTML1.xpath(".//span[contains(@style,'font-family: PTSerif-Bold') and not(contains(@style,'font-family: PTSerif-BoldItalic'))]")
# iterate only over the translations
for boldspan in boldspansTom1[133:]:
    extract_parallel_text(boldspan, boldspansTom1)

# find the bold start of the translations from Tom2
boldspansTom2 = parsedHTML2.xpath(".//span[contains(@style,'font-family: PTSans-Bold') and not(contains(@style,'font-family: PTSerif-BoldItalic'))]")
# iterate over the translations
for boldspan in boldspansTom2:
    extract_parallel_text(boldspan, boldspansTom2)

# find the bold start of the translations from Tom3
boldspansTom3 = parsedHTML3.xpath(".//span[contains(@style,'font-family: PTSerif-Bold') and not(contains(@style,'font-family: PTSerif-BoldItalic'))]")
# iterate over the translations
for boldspan in boldspansTom3:
    extract_parallel_text(boldspan, boldspansTom3)

ru_output.close()
ab_output.close()
comparable_output.close()
searchable_output.close()
skipped_translations.close()
print("extracted entries:")
print(len(ru_list))
print(len(ru_list) == len(ab_list))
