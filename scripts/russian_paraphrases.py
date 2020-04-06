import json

cyrillic_encoding = "utf-8"
with open('dictionary.json', 'r+',encoding=cyrillic_encoding) as f:
    ru_dictionary = json.loads(f.read())
print(ru_dictionary)
