from os import listdir
from os import path
import re
import io

# These ids should correspond to the parallel pages of the other languages that should correspond to the ab pages.
lost = []
rulist = []
alignedlist = []
ru = io.open('./jw_id_ru.txt','r', encoding="utf-8")
aligned = io.open('./jw_id_aligned.txt','r', encoding="utf-8")
jw_id_ru = ru.readlines()
jw_id_aligned = aligned.readlines()
for line in jw_id_ru:
    rulist.append(line[:-1])
for line in jw_id_aligned:
    alignedlist.append(line[:-1])
