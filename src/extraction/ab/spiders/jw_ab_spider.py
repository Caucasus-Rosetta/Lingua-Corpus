import scrapy
import re
import io


class JwAbSpider(scrapy.Spider):
    name = "jwab"
    start_urls = [
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/402018244',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/2019242',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/2020242',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/302016035',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/302017029',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102002189',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1101995010',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102008271',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102008082',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1101996039',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102018600',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102016801',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102005169',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102005150',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102015169',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102007442',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102013270',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/202016001',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/202017001',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/202018000',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/202019000',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/202020000',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/202013201',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/202014001',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/202015001',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102015820',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102012181',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102000081',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1101991223',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102020016',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1101992011',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102012172',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1101994008',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102011101',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102011058',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102018437',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102013537',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102006290',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102000090',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102013500',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102001160',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102013410',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102014810',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102013390',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102008391',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102008390',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1101998090',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1101998100',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102013400',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102013380',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102012770',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1102014910',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1101990020',
                  'https://wol.jw.org/ab/wol/d/r358/lp-abk/1201038'
                 ]

    def parse(self, response):
        page = response.url.split("/")[-1]
        content = []
        content.extend(response.xpath('//body//article//h1//text()').extract())
        content.extend(response.xpath('//body//article//h2//text()').extract())
        content.extend(response.xpath('//body//article//div[@class="boxTtl emphasized"]//text()').extract())
        paragraphs = response.xpath('//body//article//p')
        for paragraph in paragraphs:
            content.append("".join(paragraph.xpath('.//text()').getall()))
        filename = './ab/%s.txt' % page
        # Watch Tower Magazine 2018
        filename = filename.replace('./ab/402018','./ab/2018')
        # Jesus, The way, The Truth, The life book questions
        filename = filename.replace('./ab/11020186','./ab/11020146')
        filename = filename.replace('./ab/11020187','./ab/11020147')
        with open(filename, 'w') as f:
            for line in content:
                line = line.replace(u'\xa0', u' ')
                line = line.replace('Ҧ', 'Ԥ')
                line = line.replace('Ҕ', 'Ӷ')
                line = line.replace('ҧ', 'ԥ')
                line = line.replace('ҕ', 'ӷ')
                f.write(line+"\n")

        NEXT_PAGE_SELECTOR = '.resultNavRight a ::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )
