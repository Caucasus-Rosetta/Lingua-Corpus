import scrapy
import json
import re
import io

data = []
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

class ApsnyPressSpider(scrapy.Spider):
    name = "apsnypress_ru"
    start_urls = ['http://apsnypress.info/news/?PAGEN_3=832']

    def parse(self, response):
        global data
        page = response.url.split("/")[-1]
        # import pdb; pdb.set_trace()
        if page[1:6] != 'PAGEN':
            content = []
            page = response.url.split("/")[-2]
            date  = response.xpath('//div[@class="newslist_date"]//text()').get()
            if len(date) != 0:
                date = re.split(r"[\.\s:]",date)
                if len(date[2]) == 1:
                    date[2] = "0"+date[2]
                date = date[2]+'.'+m_j[date[3]]+'.'+date[4]+' '+date[0]+':'+date[1][0:-1]
            else:
                date = 'None'
            photo_url = response.xpath('//img[@class="detail_picture"]//@src').get()
            if photo_url != None:
                photo = 'http://apsnypress.info' + photo_url
            else:
                photo = 'None'
            data.append(json.loads('{"name": "'+page+'","date":"'+date+'","photo": "'+photo+'"}'))
            content.extend(response.xpath('//div[@class="r_block"]//h1//text()').getall())
            content.extend(response.xpath('//div[@class="detail_text"]//text()').getall())
            filename = './ru/%s.txt' % page
            with open(filename, 'w') as f:
                for line in content:
                    if not re.match(r'^\s*$', line):
                        line = line.strip('\r\n')
                        line = line.strip()
                        f.write(line+"\n")
            with open('./data_ru.json', 'w') as outfile:
                 json.dump(data, outfile, indent = 1)
        NEXT_PAGE_SELECTOR = '.newslist_block a ::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).getall()
        if len(next_page) != 0:
            for page in next_page:
                yield scrapy.Request(
                    response.urljoin(page),
                    callback=self.parse
                )
        NEXT_PAGE_SELECTOR2 = '.modern-page-previous ::attr(href)'
        next_page2 = response.css(NEXT_PAGE_SELECTOR2).get()
        if next_page2 is not None:
            yield scrapy.Request(
                response.urljoin(next_page2),
                callback=self.parse
            )
