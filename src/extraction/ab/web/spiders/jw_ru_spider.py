import scrapy
import re
import io


class JwRuSpider(scrapy.Spider):
    name = "jwru"
    start_urls = []
    jw_ids = io.open('./jw_id_ab.txt','r', encoding="utf-8")
    for id in jw_ids:
        start_urls.append('https://wol.jw.org/ru/wol/d/r2/lp-u/'+id[:-1])

    def parse(self, response):
        page = response.url.split("/")[-1]
        content = []
        content.extend(response.xpath('//body//article//h1//text()').extract())
        content.extend(response.xpath('//body//article//h2//text()').extract())
        content.extend(response.xpath('//body//article//div[@class="boxTtl emphasized"]//text()').extract())
        paragraphs = response.xpath('//body//article//p')
        for paragraph in paragraphs:
            content.append("".join(paragraph.xpath('.//text()').getall()))
        filename = './ru/%s.txt' % page
        # Jesus, The way, The Truth, The life book questions
        if re.match('./ru/11020146|./ru/11020147',filename):
            content = []
            content.extend(response.xpath('//body//article//header//h1//text()').extract())
            content.extend(response.xpath('//body//article//header//p//text()').extract())
            content.extend(response.xpath('//body//article//div[@class="blockTeach"]//p//text()').extract())
        with open(filename, 'w') as f:
            for line in content:
                line = line.replace(u'\xa0', u' ')
                f.write(line+"\n")
