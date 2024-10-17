from os import listdir
from os import path
import io

ab_files = sorted(listdir('./ab'))
# These ids should correspond to the parallel pages of the other languages that should correspond to the ab pages.
save_jw_id = io.open('./jw_id_ab.txt','w+', encoding="utf-8")
for filename in ab_files:
    save_jw_id.write(filename[:-4]+'\n')
