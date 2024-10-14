import re
import io
import json

count = 0
# Format the date and sort by date for ab
with open('../data_ab.json', 'r') as f:
    data = json.load(f)
for item in data:
    date = re.split(r"[\.\s:]",item["date"])
    if len(date) == 5:
        item["date"] = date[2] + date[1] + date[0]
data = sorted(data, key=lambda k: k.get('date', 0))

# Format the date and sort by date for ru
with open('../data_ru.json', 'r') as f:
    data_ru = json.load(f)
for item in data_ru:
    date = re.split(r"[\.\s:]",item["date"])
    if len(date) == 5:
        item["date"] = date[2] + date[1] + date[0]
data_ru = sorted(data_ru, key=lambda k: k.get('date', 0))

for item in data:
    match = []
    for item_ru in data_ru:
        if item["date"] == item_ru["date"]:
            match.append(item_ru["name"])
    item["possible match"] = match
    if len(match) != 0:
        count = count + 1
        print('Matched: '+str(count))

with open('../data_out.json', 'w') as outfile:
    json.dump(data, outfile, indent = 1)
