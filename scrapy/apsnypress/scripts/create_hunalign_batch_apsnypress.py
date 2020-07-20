from os import listdir
from os import path
import io
import json

save_apsnypress = io.open('../hunalign_batch_apsnypress.txt','w+', encoding="utf-8")
with open('../data_out.json', 'r') as f:
    data_j = json.load(f)
for item in data_j:
    if len(item["possible match"]) != 0:
        for possible_item in item["possible match"]:
            save_apsnypress.write('./ab/'+item["name"]+'.txt'+'\t'+'./ru/'+possible_item+'.txt'+'\t'+'./aligned/'+item["name"]+'_'+possible_item+'.txt'+'\n')
