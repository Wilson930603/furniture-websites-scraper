import scrapy
import json
from bs4 import BeautifulSoup


class BludotSpider(scrapy.Spider):
    name = 'bludot'
    allowed_domains = ['bludot.com']
    start_urls = ['https://bludot.com/']
    HEADERS = {
            "authority": "www.bludot.com",
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
            "accept-language": "en-US,en;q=0.9"
        }
    
    def parse(self, response):
        main_categories = response.xpath('//nav[@class="navigation"]/ul/li')
        for category in main_categories:
            category1 = category.xpath('.//span/text()').get()
            sub_categories = category.xpath('.//ul/li/a')
            for sub_category in sub_categories:
                sub_category_name = sub_category.xpath('.//text()').get()
                sub_category = sub_category.xpath('.//@href').get()
                if 'View All' not in sub_category_name:
                    yield scrapy.Request(sub_category, headers=self.HEADERS, meta={'c1': category1, 'c2': sub_category_name}, callback=self.parse_category)
        # fix new categories:
        yield scrapy.Request('https://www.bludot.com/new.html', headers=self.HEADERS, meta={'c1': 'New', 'c2': ''}, callback=self.parse_category)

    def parse_category(self, response):
        for product in response.xpath('//li[@class="item product product-item"]'):
            link = product.xpath('.//a/@href').get()
            yield scrapy.Request(link, headers=self.HEADERS, meta={'c1': response.meta['c1'], 'c2': response.meta['c2']}, callback=self.parse_product)
        
    def parse_product(self, response):
        try:
            product = {}
            imagesX = {}
            for jsons in response.xpath('//script[@type="application/ld+json"]/text()').getall():
                if '"@type":"Product"' in jsons:
                    product = json.loads(jsons)
                    break
            for jsons in response.xpath('//script[@type="text/x-magento-init"]/text()').getall():
                if 'data-role=swatch-options' in jsons:
                    imagesX = json.loads(jsons)
                    break
            
            swatchesJson = ''
            for jsons in response.xpath('//script[@type="text/x-magento-init"]/text()').getall():
                if 'swatchesJson' in jsons:
                    swatchesJson = json.loads(jsons)
                    break

            if not product:
                print('** called parse_product() but no product found!')
                return

            swatches = []
            if swatchesJson:
                for i in range(200):
                    if str(i) not in swatchesJson['*']['Lyonscg_Swatch/js/swatch']['swatchesJson']:
                        break
                    swatch = swatchesJson['*']['Lyonscg_Swatch/js/swatch']['swatchesJson'][str(i)]
                    swatch_name = swatch['name']
                    swatch_image = swatch['image']
                    swatch_price = swatch['price']
                    swatches.append({'index': i,
                                    'images': swatch_image,
                                    'price': swatch_price,
                                    'name': swatch_name})

            details = BeautifulSoup(response.text, 'html.parser').find('div', id='product_details').text.strip().replace('\n', ' ').replace('Product Details', '').strip()
            dimensions = BeautifulSoup(response.text, 'html.parser').find('div', id='dimensions').text.replace('Product Dimensions', ' ').strip()
            if not dimensions:
                dimensions = BeautifulSoup(response.text, 'html.parser').find('div', id='dimensions').find('img')['src']
            if imagesX:
                imagesX = imagesX['[data-role=swatch-options]']['Magento_Swatches/js/swatch-renderer']['jsonConfig']['images']
            else:
                imagesX = []
            try:
                all_offers = product['offers']['offers'][:-1]
            except:
                all_offers = {'@type': 'http://schema.org/Offer', 'name': product['name'], 'price': response.xpath('//span[@class="price"]/text()').get().replace('$', ''), 'sku': product['sku'], 'url': response.url, 'availability': 'http://schema.org/InStock'}
            n = 0
            for offer in all_offers:
                n += 1
                images = []
                if imagesX:
                    try:
                        imagesX3 = imagesX[list(imagesX.keys())[n]]
                    except:
                        imagesX3 = imagesX[list(imagesX.keys())[-1]]
                    for image in imagesX3:
                        if image['img']:
                            images.append(image['img'])
                if len(all_offers) > 1:
                    try:
                        name_extension = offer['url'].split('.com/')[-1].replace('.html', '').replace('-', ' ').title()
                        name_extension = name_extension.split(product['offers']['offers'][2]['name'].split(' ')[-1], 1)[-1].strip()
                    except:
                        name_extension = ''
                    
                    if name_extension:
                        name = offer['name'] + ' - ' + name_extension
                    else:
                        name = offer['name']
                else:
                    name = offer['name']

                
                yield {
                    'SKU': offer['sku'],
                    'URL': offer['url'],
                    'Main Category': response.meta['c1'],
                    'Sub Category 1': response.meta['c2'],
                    # 'Sub Category 2': response.meta['c3'],
                    # 'Sub Category 3': '',
                    'Product Name': name,
                    # 'Rating': '',
                    # '# of reviews': '',
                    'Price': offer['price'],
                    'Details': details,
                    'Dimension': dimensions,
                    'Swatches': swatches,
                    'Main Image': images[0] if images else '',
                    'Image 1': images[1] if len(images) > 1 else '',
                    'Image 2': images[2] if len(images) > 2 else '',
                    'Image 3': images[3] if len(images) > 3 else '',
                    'Image 4': images[4] if len(images) > 4 else '',
                    'Image 5': images[5] if len(images) > 5 else '',
                }
        except:
            pass
