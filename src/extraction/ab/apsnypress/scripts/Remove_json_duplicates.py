import re
import io
import json

# Format the date and sort by date for ru
with open('../data_ru.json', 'r') as f:
    data_ru = json.load(f)

unique = { each['name'] : each for each in data_ru }

with open('../data_ru_see.json', 'w') as outfile:
    json.dump(unique, outfile, indent = 1)
