import re
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request

import logging
logging.getLogger('scrapy').propagate = False


class propzySpi(scrapy.Spider):
    name = 'propzy'
    allowed_domains = "https://propzy.vn"
    start_urls = ['https://propzy.vn/mua/ban-nha-rieng-tphcm']
    data = []
    row = {}
    page = 1
    max_page = 10

    def parse_data(self, response):
        self.row.clear()

        self.row['link'] = response.url

        self.row['title'] = ''.join(
            response.css('.div-title-rose > h1::text').get()).replace(
                u'\xa0', u' ').replace('  ', ' ')

        a = response.xpath(
            '//div[@class="bl-inline div-price"]/span/text()').extract()
        self.row['Giá(tỷ)'] = a[0].replace(' tỷ', '').replace(',', '.')
        self.row['Diện tích(m²)'] = a[1].replace('m²', '').replace(',', '.')

        a = response.xpath(
            '//div[@class="bl-inline div-price"]/p/a/span/text()').extract()
        self.row['Quận/Huyện'] = a[0]
        self.row['Phường/Xã'] = a[1]

        for inf in response.xpath(
                '//div[@class="block-info block-info-2 11"]/div/span/text()'
        ).extract():
            inf = re.split(":", inf)
            name = ' '.join(inf[0].split())
            info = inf[1].strip()
            if name in ['Chiều dài', 'Chiều rộng', 'Mặt tiền', 'Hẻm']:
                name += "(m)"
                info = info.replace('m', '').replace('.0', '')
            self.row[name] = info

        a = response.xpath(
            '//div[@class="block-info block-info-5 11"]/div/span/text()'
        ).extract()
        b = ' '.join([txt.strip() for txt in response.xpath(
            '//div[@class="block-info block-info-6"]/div//text()').extract()
                      ]).replace('.-', '.').replace('-', '')
        self.row['Truy vấn'] = b.strip() + ' ' + '. '.join(a)

        # print(self.row)
        self.data.append(self.row.copy())

    def parse(self, response):
        for url in response.css('.redirectProductDetail'):
            yield scrapy.Request(self.allowed_domains +
                                 url.css('a::attr(href)')[0].extract(),
                                 callback=self.parse_data,
                                 dont_filter=True)

        if self.page < self.max_page:
            self.page += 1
            print(self.page)
            yield Request(url="https://propzy.vn/mua/ban-nha-rieng-tphcm/p%d" %
                          self.page,
                          callback=self.parse,
                          dont_filter=True)


process = CrawlerProcess()
process.crawl(propzySpi)
process.start()
df = pd.DataFrame(propzySpi.data,
                  columns=[
                      'link', 'title', 'Giá(tỷ)', 'Diện tích(m²)',
                      'Quận/Huyện', 'Phường/Xã', 'Chiều dài(m)',
                      'Chiều rộng(m)', 'Hướng', 'Mặt tiền(m)', 'Hẻm(m)',
                      'Tầng', 'Giấy tờ', 'Phòng ngủ', 'Phòng tắm', 'Truy vấn'
                  ])
df.to_csv('data.csv')
# print(df)
print('end')