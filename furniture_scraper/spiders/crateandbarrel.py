from bs4 import BeautifulSoup
import scrapy
import json
import requests
import re

class CrateandbarrelSpider(scrapy.Spider):
    name = 'crateandbarrel'
    allowed_domains = ['crateandbarrel.com']
    start_urls = ['https://shopee.sg/']

    HEADERS = {
        "authority": "www.crateandbarrel.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"''',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '''"Windows"''',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://www.crateandbarrel.com/furniture/",
        "accept-language": "en-US,en;q=0.9"
    }

    def parse(self, response):
        yield scrapy.Request('http://crateandbarrel.com/', headers=self.HEADERS, callback=self.parse_nav, dont_filter=True)

    def parse_nav(self, response):
        navigation = response.xpath('//nav[@class="header-nav nav-primary"]')
        categories = ['Furniture']
        for category in navigation.xpath('.//li[@class="primary-nav-item"]'):
            if category.xpath('.//a/text()').get() in categories:
                category_name = category.xpath('.//a/text()').get()
                for sub_category in category.xpath('.//li[@class="nav-category-item"]'):
                    link = 'http://crateandbarrel.com/' + sub_category.xpath('.//a/@href').get()
                    sub_category_name = sub_category.xpath('.//a/text()').get()
                    if '/1' in link:
                        yield scrapy.Request(link, headers=self.HEADERS, callback=self.parse_products, meta={'CN': category_name, 'SCN': sub_category_name, 'SSCN': ''}, dont_filter=False)
                    else:
                        yield scrapy.Request(link, headers=self.HEADERS, callback=self.parse_category, meta={'CN': category_name, 'SCN': sub_category_name, 'SSCN': ''}, dont_filter=True)
    
    def parse_category(self, response):
        sub_categories = response.xpath('//div[@class="showcase-item"]')
        for sub_category in sub_categories:
            link = 'http://crateandbarrel.com/' + sub_category.xpath('.//div/a/@href').get()
            sub_category_name = sub_category.xpath('.//div/a/div/h3/text()').get()
            if sub_category_name and 'Shop All' in sub_category_name:
                sub_category_name = sub_category.xpath('.//div/a/@href').get().split('/')[-2].replace('-', ' ').title()
            if not sub_category_name:
                sub_category_name = ''
            if '/1' in link:
                yield scrapy.Request(link, headers=self.HEADERS, callback=self.parse_products, meta={'CN': response.meta['CN'], 'SCN': response.meta['SCN'], 'SSCN': sub_category_name}, dont_filter=False)
            else:
                yield scrapy.Request(link, headers=self.HEADERS, callback=self.parse_sub_category, meta={'CN': response.meta['CN'], 'SCN': response.meta['SCN'], 'SSCN': sub_category_name}, dont_filter=True)

    def parse_sub_category(self, response):
        sub_sub_categories = response.xpath('//div[@class="cms-content cms-category-banner-top"]/div[@class="upholsteryCollection "]')
        for sub_sub_category in sub_sub_categories:
            link = 'http://crateandbarrel.com/' + sub_sub_category.xpath('.//a/@href').get()
            yield scrapy.Request(link, headers=self.HEADERS, callback=self.parse_products, meta={'CN': response.meta['CN'], 'SCN': response.meta['SCN'], 'SSCN': response.meta['SSCN']}, dont_filter=False)

    def parse_products(self, response):
        jsondata = json.loads(response.xpath('//script[@defer="true"]/text()').get().split('({}, ')[1].split(');')[0])
        categoryId = jsondata['page']['pageInfo']['pageId'].replace('c', '')
        head = {
            "authority": "www.crateandbarrel.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"''',
            "content-type": "application/json",
            "x-requested-with": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "sec-ch-ua-platform": '''"Windows"''',
            "accept": "*/*",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.crateandbarrel.com/whats-new/new-furniture/1",
            "accept-language": "en-US,en;q=0.9"
        }

        skip = 0
        while True:
            querystring = {"categoryId":categoryId,"facets":"","sortBy":"","hasAvailabilityCheck":"false","isModelOnly":"true","skip":skip,"take":"100"}
            try:
                products = requests.request("GET", response.url, headers=head, params=querystring).json()['minisets']
            except:
                break

            if len(products) == 0:
                break
            for product in products:
                try:
                    images = []
                    videos = []
                    try:
                        for item in product['showcaseData']['images']:
                            if not item['isVideo']:
                                if not item['is360']:
                                    images.append(item['portraitSrc'])
                            else:
                                if not item['is360']:
                                    video_link = f'https://images.crateandbarrel.com/s7viewers/html5/VideoViewer.html?config=Crate/Universal_HTML5_Video_FJ_Main_Carousel&asset=Crate/{item["videoSource"]}&autoplay=false&loop=false'
                                    videos.append(video_link)
                    except:
                        pass
                    p = {
                        'SKU': product['sku'],
                        'URL': 'https://www.crateandbarrel.com/' + product['navigateUrl'],
                        'Main Category': '',
                        'Sub Category 1': '',
                        'Sub Category 2': '',
                        'Sub Category 3': '',
                        'Product Name': product['name'],
                        'Rating': '',
                        '# of reviews': '',
                        'Price': product['currentPrice'],
                        'Details': '',
                        'Dimension': '',
                        'Swatches': [],
                        'Main Image': images[0] if len(images) else '',
                        'Image 1': images[1] if len(images) > 1 else '',
                        'Image 2': images[2] if len(images) > 2 else '',
                        'Image 3': images[3] if len(images) > 3 else '',
                        'Image 4': images[4] if len(images) > 4 else '',
                        'Image 5': images[5] if len(images) > 5 else '',
                        'Video 1': videos[0] if len(videos) else '',
                        'Video 2': videos[1] if len(videos) > 1 else '',
                        'Video 3': videos[2] if len(videos) > 2 else ''
                    }
                    link = 'https://www.crateandbarrel.com/' + product['navigateUrl']
                    yield scrapy.Request(link, headers=self.HEADERS, callback=self.parse_p, meta={'p': p}, dont_filter=False)
                except:
                    pass
            skip += 100

    def parse_p(self, response):
        product = response.meta['p']
        soup = BeautifulSoup(response.body, 'lxml')
        dimensions = soup.find('div', class_='details-dimensions').text.split('\n')[-1].strip() if soup.find('div', class_='details-dimensions') else ''
        if dimensions:
            dimensions = dimensions.split(' ')[-1]
            width = re.findall('[0-9]*"W', dimensions)[0].replace('W', '') if re.findall('[0-9]*"W', dimensions) else ''
            depth = re.findall('[0-9]*"D', dimensions)[0].replace('D', '') if re.findall('[0-9]*"D', dimensions) else ''
            height = re.findall('[0-9]*"H', dimensions)[0].replace('H', '') if re.findall('[0-9]*"H', dimensions) else ''
            dimensions = f'Width: {width}, Depth: {depth}, Height: {height}'
        rating = soup.find('span', class_='review-stars-bar')['title'].split(' ')[0] if soup.find('span', class_='review-stars-bar') else '0'
        if float(rating) < 1:
            rating = ''
        reviews = soup.find('div', class_='review-total text-md-reg').text.split(' ')[0] if soup.find('div', class_='review-total text-md-reg') else ''
        categories = []
        for item in soup.find_all('li', class_='breadcrumb-list-item'):
            categories.append(item.find('a').text)
        if soup.find('li', class_='breadcrumb-list-item-no-arrow').text not in categories:
            categories.append(soup.find('li', class_='breadcrumb-list-item-no-arrow').text)

        product['Main Category'] = categories[0]
        product['Sub Category 1'] = categories[1] if len(categories) > 1 else ''
        product['Sub Category 2'] = categories[2] if len(categories) > 2 else ''
        try:
            product['Sub Category 3'] = categories[-1] if categories[-1] != categories[2] and categories[-1] != categories[1] else ''
        except:
            pass
        product['Rating'] = rating
        product['# of reviews'] = reviews
        product['Details'] = BeautifulSoup(response.body, 'html.parser').find('div', class_='details-content').get_text(separator=' ')
        product['Dimension'] = dimensions
        
        x = ''
        for item in response.xpath('//script'):
            if '{"model":' in str(item.get()):
                x = item
        if x:
            x = json.loads(x.xpath('.//text()').get().split('Container, ')[1].split('), document')[0])
            
        swatches = []
        index = 0
        try:
            for i in range(5):
                if 'swatch' in str(x['model']['browseDto']['superSpecialOrder']['options'][i]):
                    for item in x['model']['browseDto']['superSpecialOrder']['options'][i]['choiceGroups']:
                        for y in item['choices']:
                            swatches.append({'index': index,
                                            'images': [y['images']['desktop']],
                                            'name': y['title']})
                        index += 1
                    break
        except:
            pass
        product['Swatches'] = swatches

        yield(product)
