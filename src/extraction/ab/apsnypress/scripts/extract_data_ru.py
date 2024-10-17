import json
import re
import io
import os
from lxml import html

data = []
count = 0
dir_ru = os.listdir('../news/')
m_j = {
"Января":"01",
"Февраля":"02",
"Марта":"03",
"Апреля":"04",
"Мая":"05",
"Июня":"06",
"Июля":"07",
"Августа":"08",
"Сентября":"09",
"Октября":"10",
"Ноября":"11",
"Декабря":"12"
}

def parse_data(htmltree, name):
    global data
    content = []
    page = name
    date  = htmltree.xpath('//div[@class="newslist_date"]//text()')
    if len(date) != 0:
        date = re.split(r"[\.\s:]",date[0])
        if len(date[2]) == 1:
            date[2] = "0"+date[2]
        date = date[2]+'.'+m_j[date[3]]+'.'+date[4]+' '+date[0]+':'+date[1][0:-1]
    else:
        date = 'None'
    photo_url = htmltree.xpath('//img[@class="detail_picture"]//@src')
    if len(photo_url) != 0:
        photo = 'http://apsnypress.info' + photo_url[0]
    else:
        photo = 'None'
    data.append(json.loads('{"name": "'+page+'","date":"'+date+'","photo": "'+photo+'"}'))
    content.extend(htmltree.xpath('//div[@class="r_block"]//h1//text()'))
    content.extend(htmltree.xpath('//div[@class="detail_text"]//text()'))
    filename = '../ru/%s.txt' % page
    with open(filename, 'w') as f:
        for line in content:
            if not re.match(r'^\s*$', line):
                line = line.strip('\r\n')
                line = line.strip()
                f.write(line+"\n")
    with open('../data_ru.json', 'w') as outfile:
         json.dump(data, outfile, indent = 1)
for item in dir_ru:
    tree = html.parse('../news/'+item+'/index.html')
    parse_data(tree,item)
    count = count + 1
    print("parsed: "+ str(count))
