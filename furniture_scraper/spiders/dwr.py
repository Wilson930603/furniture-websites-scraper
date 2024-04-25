import scrapy
import requests
import json
import re

class DwrSpider(scrapy.Spider):
    name = 'dwr'
    allowed_domains = ['dwr.com']
    start_urls = ['https://www.dwr.com/']
    HEADERS = {
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"''',
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "sec-ch-ua-platform": '''"Windows"''',
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Dest": "script",
        "Referer": "https://www.dwr.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def parse(self, response):
        allowed_categories = ['furniture']
        possible_categories = response.xpath('//ul[@class="nav navbar-nav"]/li/a/@href').getall()
        for category in possible_categories:
            if any(x in category for x in allowed_categories):
                yield scrapy.Request(category, headers=self.HEADERS, callback=self.parse_sub_categories, dont_filter=True)
    
    def parse_sub_categories(self, response):
        sub_categories = response.xpath('//figcaption/h3/a/@href').getall()
        for sub_category in sub_categories:
            yield scrapy.Request(sub_category, headers=self.HEADERS, callback=self.parse_products, dont_filter=True)
    
    def parse_products(self, response):
        products = response.xpath('//div[@class="product-tile "]')
        for product in products:
            link = 'https://www.dwr.com/' + product.xpath('.//a[@class="stretched-link"]/@href').get()
            yield scrapy.Request(link, headers=self.HEADERS, callback=self.parse_product, dont_filter=True)
        if len(products) > 95:
            start = 96
            if 'start=' in response.url:
                start = int(response.url.split('&start=')[-1].split('&')[0]) + 96
                
            new_page_link = response.url.split('lang=en_US')[0]
            new_page_link = new_page_link + f'lang=en_US&start={start}'
            yield scrapy.Request(new_page_link, headers=self.HEADERS, callback=self.parse_products, dont_filter=True)
        
    def parse_product(self, response):
        categories = response.xpath('//ol/li/a/text()').getall()
        if response.xpath('//span[@class="sr-only"]/text()'):
            rating = response.xpath('//span[@class="sr-only"]/text()').get().split(' ')[0]
        else:
            rating = ''
        for item in response.xpath('//script'):
            if 'generatedData' in str(item.get()):
                json_script = item.get().split('generatedData = ')[1].split(';')[0]
                break
        x = json.loads(json_script)
        product_id = x[0]['ecommerce']['detail']['products'][0]['id']
        API_URL = "https://staticw2.yotpo.com/batch/app_key/3i9iZTLvUzBswpHrsCouNOJo71DNAvgCKsr9Cl12/domain_key/5667/widget/rich_snippet"
        payload = 'methods=[{"method":"rich_snippet","params":{"pid":"' + str(product_id) + '"}}]&app_key=3i9iZTLvUzBswpHrsCouNOJo71DNAvgCKsr9Cl12&is_mobile=false&widget_version=2021-05-26_15-37-45'
        headers = {
            "authority": "staticw2.yotpo.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"''',
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua-mobile": "?0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "sec-ch-ua-platform": '''"Windows"''',
            "origin": "https://www.dwr.com",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.dwr.com/",
            "accept-language": "en-US,en;q=0.9"
        }
        reviews_request = requests.request("POST", API_URL, data=payload, headers=headers).json()[0]['result'].strip()
        if reviews_request:
            rating = reviews_request.split('ratingValue')[1].split('\n')[0].replace('"', '').replace(':', '').replace(',', '').strip()
            reviews = reviews_request.split('reviewCount')[1].split('\n')[0].replace('"', '').replace(':', '').replace(',', '').strip()
        else:
            rating = reviews = ''
        images = response.xpath('//div[contains(@class, "preview thumbnail")]/div/img/@src').getall()
        del_price = response.xpath('//div[@class="col-12 ml-sm-auto product-info-section"]').xpath('.//div[@class="price"]/span/del').xpath('.//span[@class="value"]/@content').get()
        if del_price:
            price = del_price
            sale_price = response.xpath('//div[@class="price"]/span').xpath('.//span[@class="sales"]/span/@content').get()
        else:
            price = x[0]['ecommerce']['detail']['products'][0]['price']
            sale_price = ''

        swatches = []
        index = 0
        try:
            for swatch in response.xpath('//button[contains(@class, "color-attribute")]/@data-text').getall():
                swatch_index = index
                swatches.append({'index': swatch_index,
                                'images': [],
                                'name': swatch})
                index += 1
        except:
            pass

        yield {
            'SKU': response.xpath('//span[@class="product-id"]/text()').get().strip(),
            'URL': response.url,
            'Main Category': categories[0].strip() if categories else '',
            'Sub Category 1': categories[1].strip() if len(categories) > 1 else '',
            'Sub Category 2': categories[2].strip() if len(categories) > 2 else '',
            'Sub Category 3': categories[-1].strip() if len(categories) > 3 else '',
            'Product Name': response.xpath('//h1[@class="h3 product-name"]/text()').get().strip(),
            'Rating': rating,
            '# of reviews': reviews,
            'Price': price,
            'Sale Price': sale_price,
            'Details': ' '.join(response.xpath('//ul[@class="bulleted specifications-pdp-feature-list"]/li/text()').getall()),
            'Dimension': ' '.join(response.xpath('//ul[@class="unstyled mb-3 specifications-pdp-dimensions-list"]/li/text()').getall()),
            'Swatches': swatches,
            'Main Image': response.xpath('//span[@class="ratio ratio-16x9"]/img/@data-srcset').get().split(',')[-2].split(' ')[0],
            'Image 1': images[1].split('auto=format')[0] + 'auto=format&w=1200&q=68&h=1000' if len(images) > 1 else '',
            'Image 2': images[2].split('auto=format')[0] + 'auto=format&w=1200&q=68&h=1000' if len(images) > 2 else '',
            'Image 3': images[3].split('auto=format')[0] + 'auto=format&w=1200&q=68&h=1000' if len(images) > 3 else '',
            'Image 4': images[4].split('auto=format')[0] + 'auto=format&w=1200&q=68&h=1000' if len(images) > 4 else '',
            'Image 5': images[5].split('auto=format')[0] + 'auto=format&w=1200&q=68&h=1000' if len(images) > 5 else '',
        }
