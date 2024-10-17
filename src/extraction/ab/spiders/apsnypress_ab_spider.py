import scrapy
import json
import re
import io

data = []

class ApsnyPressSpider(scrapy.Spider):
    name = "apsnypress_ab"
    start_urls = ['http://apsnypress.info/abk/news/?PAGEN_1=310']

    def parse(self, response):
        global data
        page = response.url.split("/")[-1]
        if page[1:6] != 'PAGEN':
            content = []
            page = response.url.split("/")[-2]
            date  = response.xpath('//div[@class="newslist_date"]//text()').get()
            photo_url = response.xpath('//img[@class="detail_picture"]//@src').get()
            if photo_url != None:
                photo = 'http://apsnypress.info' + photo_url
            else:
                photo = 'None'
            data.append(json.loads('{"name": "'+page+'","date":"'+date+'","photo": "'+photo+'"}'))
            content.extend(response.xpath('//div[@class="r_block"]//h1//text()').getall())
            content.extend(response.xpath('//div[@class="detail_text"]//text()').getall())
            filename = './ab/%s.txt' % page
            with open(filename, 'w') as f:
                for line in content:
                    line = line.replace('Ҧ', 'Ԥ')
                    line = line.replace('Ҕ', 'Ӷ')
                    line = line.replace('ҧ', 'ԥ')
                    line = line.replace('ҕ', 'ӷ')
                    if not re.match(r'^\s*$', line):
                        line = line.strip('\r\n')
                        line = line.strip()
                        f.write(line+"\n")
            with open('./data.json', 'w') as outfile:
                 json.dump(data, outfile, indent = 1)
        NEXT_PAGE_SELECTOR = '.newslist_block a ::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).getall()
        if len(next_page) != 0:
            for page in next_page:
                yield scrapy.Request(
                    response.urljoin(page),
                    callback=self.parse
                )
        NEXT_PAGE_SELECTOR2 = '.modern-page-next ::attr(href)'
        next_page2 = response.css(NEXT_PAGE_SELECTOR2).get()
        if next_page2 is not None:
            yield scrapy.Request(
                response.urljoin(next_page2),
                callback=self.parse
            )
