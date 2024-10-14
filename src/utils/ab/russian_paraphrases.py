import json
from os import listdir

cyrillic_encoding = "utf-8"
with open('dictionary.json', 'r+',encoding=cyrillic_encoding) as f:
    ru_dictionary = json.loads(f.read())

outputfile = 'russian_paraphrase.txt'
output = open(outputfile,"w+")

word_list = ru_dictionary["wordlist"]
# we extract the synonyms from the dictionary
synonyms = {}
for word in word_list:
    if "synonyms" in word.keys():
        if word["name"] in synonyms.keys():
            synonyms[word["name"]].update(word["synonyms"])
        else:
            synonyms[word["name"]] = set(word["synonyms"])

print("amount of russian synonyms:")
print(len(synonyms))

russian_paraphrases = {}
# Let's generate paraphrases
# and store them like
# russian_paraphrases = {"original sentence":["paraphrase1","paraphrase2"]}

def generate_paraphrases(sentence):
    for synonym_key in synonyms.keys():
        paraphrases = []
        # search and exchange the synonym
        # the search space could be advanced to the start and end of the sentence
        # how can we make this case sensitive?
        if " "+synonym_key+" " in sentence:
            # we have found a match
            output.write("\n"+sentence+"\n")
            for i,synonym in enumerate(synonyms[synonym_key]):
                if len(paraphrases) == i:
                    paraphrases.append(sentence[:])
                if " "+synonym_key+" " in paraphrases[i]:
                    paraphrases[i] = paraphrases[i].replace(" "+synonym_key+" ", " "+synonym+" ")
                    #write the exchanhe to the output_type
                    output.write("\t"+synonym_key+" --> "+synonym+"\n")
        if len(paraphrases) > 0:
            russian_paraphrases[sentence] = paraphrases

for file_name in listdir('../ru'):
    with open('../ru/'+file_name, 'r+',encoding="utf-8") as f:
        russian_sentences = f.read().splitlines()
        for sentence in russian_sentences:
            generate_paraphrases(sentence)

print("amount of russian paraphrases:")
print(sum([len(russian_paraphrases[sentence]) for sentence in russian_paraphrases.keys()]))
