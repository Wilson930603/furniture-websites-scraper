import scrapy
import json
import urllib.parse

class WayfairSpider(scrapy.Spider):
    name = 'wayfair'
    allowed_domains = ['wayfair.com']
    start_urls = ['https://example.com']
    HEADERS = {
    "authority": "www.wayfair.com",
    "pragma": "no-cache",
    "cache-control": "no-cache",
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "_px3=9241591f43c7967d8f079ece47387e2a1b30f7d11c0090d058d91ac52cf5b9e5:QCHkEbAdgUDmLFKLSm2I73ZyGc0d+mRp1nmiLM8NuBxnILmHWGQvVF1JCIKuPkwGAYoC7LcQVZaZqkoywl33Sw==:1000:qhmbcPmzI88aijjOKeSUDGnUAOrTMizP66EPmUBYRtUvVAUR4mnBNRFLQCvJdXgi+pypyiWSZWcKvHe6wyaGMgktzRTOS95GyIbnrveO3Y+CyLk5YEGagvkyGHgYn2c1tM1E3UR6/CJdXyZXe+oAy+C0e/13KemFGfEHEok0u7mTtO6lr8LBm5mVPqXKmIvsDhISmj1AvBX6VeQT0XxW3A==;",
    }
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
            'scrapy_crawlera.CrawleraMiddleware': 610,
        },
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': 'c79ed6d3bb814597b4b26b17dfa299d5',
        'CONCURRENT_REQUESTS': 100,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 100,
        'AUTOTHROTTLE_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 30
    }

    def parse(self, response):
        if 'starter' not in response.meta:
            categories = [('Furniture', 'https://www.wayfair.com/furniture/cat/furniture-c45974.html')]
            for category in categories:
                yield scrapy.Request(category[1], headers=self.HEADERS, callback=self.parse, meta={'starter': True}, dont_filter=True)
            return
        sub_categories = response.xpath('//div[contains(@class, "CategoryLandingPageNavigation-linkWrap")]')
        for sub_category in sub_categories:
            sub_category = sub_category.xpath('.//a/@href').get()
            if 'http' not in sub_category:
                sub_category = 'https://www.wayfair.com' + sub_category
            if 'sale' not in sub_category:
                yield scrapy.Request(sub_category + '?itemsperpage=12', headers=self.HEADERS, callback=self.parse_sub_category, dont_filter=True)
        
        if not sub_categories:
            yield scrapy.Request(response.url, headers=self.HEADERS, callback=self.parse, meta={'starter': True}, dont_filter=True)

    def parse_sub_category(self, response):
        sub_categories = response.xpath('//div[contains(@class, "CategoryLandingPageNavigation-linkWrap")]')
        products = response.xpath('//a[@class="pl-ProductCard-productCardElement"]/@href').getall()
        if sub_categories != []:
            for sub_category in sub_categories:
                sub_category = sub_category.xpath('.//a/@href').get()
                if 'sale' in sub_category:
                    continue
                elif 'http' not in sub_category:
                    sub_category = 'https://www.wayfair.com' + sub_category
                yield scrapy.Request(sub_category, headers=self.HEADERS, callback=self.parse_sub_category, meta={'new': True}, dont_filter=True)
        elif products != []:
            for product in products:
                if 'http' not in product:
                    product = 'https://www.wayfair.com' + product
                product_headers = {
                    "authority": "www.wayfair.com",
                    "pragma": "no-cache",
                    "cache-control": "no-cache",
                    "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"''',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '''"Windows"''',
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "sec-fetch-site": "same-origin",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-user": "?1",
                    "sec-fetch-dest": "document",
                    "referer": product,
                    "accept-language": "en-US,en;q=0.9",
                    "cookie": "_px3=9241591f43c7967d8f079ece47387e2a1b30f7d11c0090d058d91ac52cf5b9e5:QCHkEbAdgUDmLFKLSm2I73ZyGc0d+mRp1nmiLM8NuBxnILmHWGQvVF1JCIKuPkwGAYoC7LcQVZaZqkoywl33Sw==:1000:qhmbcPmzI88aijjOKeSUDGnUAOrTMizP66EPmUBYRtUvVAUR4mnBNRFLQCvJdXgi+pypyiWSZWcKvHe6wyaGMgktzRTOS95GyIbnrveO3Y+CyLk5YEGagvkyGHgYn2c1tM1E3UR6/CJdXyZXe+oAy+C0e/13KemFGfEHEok0u7mTtO6lr8LBm5mVPqXKmIvsDhISmj1AvBX6VeQT0XxW3A==;",
                }
                yield scrapy.Request(product, headers=product_headers, callback=self.parse_product, dont_filter=True)

            new_url = response.url.split('?')[0]
            if 'curpage' not in response.url:
                new_page = '2'
            else:
                new_page = int(response.url.split('curpage=')[-1])+1
            new_url = new_url + f'?itemsperpage=12&curpage={str(new_page)}'
            if not ('curpage' not in response.url and not response.meta['new']):
                yield scrapy.Request(new_url, headers=self.HEADERS, callback=self.parse_sub_category, meta={'new': False}, dont_filter=True)

    def parse_product(self, response):
        product = []
        for jsons in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            if '"@type":"Product"' in jsons:
                product = json.loads(jsons)
                break
        if not product:
            return

        images = response.xpath('//div[@class="ImageComponent"]/img/@srcset').getall()
        image_urls = []
        for image in images:
            image_url = image.split(',')[-1].split(' ')[0]
            if 'h56' in image_url and 'w56' in image_url:
                image_url = image_url.replace('h56', 'h800').replace('w56', 'w800').replace('r50', 'r85')
                image_urls.append(image_url)
        details = '. '.join(response.xpath('//ul[@class="ProductOverviewInformation-list"]/li/text()').getall()).replace('..', '.')
        
        price = response.xpath('//div[@class="SFPrice"]/div/span/text()').get()
        salePrice = response.xpath('//div[@class="SFPrice"]/div/s/text()').get()
        if salePrice:
            saleprice_tmp = salePrice
            salePrice = price
            price = saleprice_tmp
        
        API_URL = "https://www.wayfair.com/graphql"
        querystring = {"hash": '85f8ba545fe309999686c353eecba095'}
        payload = {"variables": {"sku": product['sku']}}
        headers = {
            "authority": "www.wayfair.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"''',
            "sec-ch-ua-mobile": "?0",
            "x-parent-txid": "I+F9OmG0CAKY/aL9O6WmAg==",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
            "content-type": "application/json",
            "use-web-hash": "true",
            "accept": "application/json",
            "sec-ch-ua-platform": '''"Windows"''',
            "origin": "https://www.wayfair.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "accept-language": "en-US,en;q=0.9"
        }

        try:
            rating = response.xpath('//span[@class="ProductRatingNumberWithCount-rating"]/text()').get()
            reviewCount = response.xpath('//span[@class="ProductRatingNumberWithCount-count ProductRatingNumberWithCount-count--link"]/text()').get().split(' ')[0]
        except:
            rating = reviewCount = '0'
        categories = response.xpath('//li[@class="Breadcrumbs-listItem"]/a/text()').getall()

        p = {
            'SKU': product['sku'],
            'URL': product['url'],
            'Main Category': categories[0] if len(categories) else '',
            'Sub Category 1': categories[1] if len(categories) > 1 else '',
            'Sub Category 2': categories[2] if len(categories) > 2 else '',
            'Sub Category 3': categories[3] if len(categories) > 3 else '',
            'Product Name': product['name'],
            'Rating': rating,
            '# of reviews': reviewCount,
            'Price': price,
            'Sale Price': salePrice,
            'Details': details,
            'Dimension': '',
            'Swatches': '',
            'Main Image': image_urls[0] if image_urls else '',
            'Image 1': image_urls[1] if len(image_urls) > 1 else '',
            'Image 2': image_urls[2] if len(image_urls) > 2 else '',
            'Image 3': image_urls[3] if len(image_urls) > 3 else '',
            'Image 4': image_urls[4] if len(image_urls) > 4 else '',
            'Image 5': image_urls[5] if len(image_urls) > 5 else '',
        }

        images = response.xpath('//img[@class="pl-FluidImage-image"]/@src').getall()

        yield scrapy.Request(API_URL+'?'+urllib.parse.urlencode(querystring), method='POST', body=json.dumps(payload), headers=headers, meta={'p': p, 'im': images}, callback=self.parse_product2)
    
    def parse_product2(self, response):
        product = response.meta['p']
        dimensions = response.json()
        dimensions_text = ''
        try:
            for dimension in dimensions['data']['product']['displayInfo']['measurements'][0]['tags']:
                text = dimension['title'] + ':' + dimension['value'] + '. '
                dimensions_text = dimensions_text + text
            product['Dimension'] = dimensions_text.replace('\n', ' ').strip()
        except:
            pass

        API_URL = "https://www.wayfair.com/graphql"
        querystring = {"hash":"24e17b1e9c2cffd32c2cab2189a5e917#16dd774cea9d3bd2c887f99be034a1de"}
        payload = {"variables": {
                "sku": response.meta['p']['SKU'],
                "withLegacySpecificationsData": False
            }}
        headers = {
            "authority": "www.wayfair.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "apollographql-client-name": "@wayfair/sf-ui-product-details",
            "sec-ch-ua-mobile": "?0",
            "x-parent-txid": "I+F9OmHzvVmozBMumrthAg==",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "content-type": "application/json",
            "use-web-hash": "true",
            "accept": "application/json",
            "apollographql-client-version": "b3b521a93ebef488a9385a842eb8e830da80c083",
            "origin": "https://www.wayfair.com",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.wayfair.com/furniture/pdp/latitude-run-thompson-776-wide-reversible-modular-sofa-chaise-w006913213.html",
            "accept-language": "en-US,en;q=0.9"
        }

        yield scrapy.Request(API_URL+'?'+urllib.parse.urlencode(querystring), method='POST', body=json.dumps(payload), headers=headers, meta={'p': product, 'im': response.meta['im']}, callback=self.parse_product3)
    
    def parse_product3(self, response):
        product = response.meta['p']
        swatches = []
        index = 0
        for item in response.json()['data']['product']['manufacturerPartNumber']['partNumberOptions']:
            swatch_name = item[4]
            swatch_image = ''
            for item in response.meta['im']:
                if swatch_name.replace(' ', '+') in item:
                    swatch_image = item
                    break
            if not swatch_image:
                for item in response.meta['im']:
                    if swatch_name.split(' ')[0] in item:
                        swatch_image = item
                        break
            swatches.append({'index': index,
                            'images': swatch_image,
                            'name': swatch_name})
            index += 1
        product['Swatches'] = swatches
        
        yield(product)