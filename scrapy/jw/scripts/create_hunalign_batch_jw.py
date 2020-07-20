from os import listdir
from os import path
import io

ab_files = sorted(listdir('./ab'))
# These ids should correspond to the parallel pages of the other languages that should correspond to the ab pages.
save_jw_id = io.open('./hunalign_batch_jw.txt','w+', encoding="utf-8")
jw_id = io.open('./jw_id_ab.txt','r', encoding="utf-8")
f = jw_id.readlines()
for line in f:
    save_jw_id.write('./ab/'+line[:-1]+'.txt'+'\t'+'./ru/'+line[:-1]+'.txt'+'\t'+'./aligned/'+line[:-1]+'.txt'+'\n')
