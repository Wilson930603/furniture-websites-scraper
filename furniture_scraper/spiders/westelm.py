import scrapy
import json
from bs4 import BeautifulSoup
import re

class WestelmSpider(scrapy.Spider):
    name = 'westelm'
    allowed_domains = ['westelm.com']
    start_urls = ['https://shopee.sg/']


    HEADERS = {
        "authority": "www.westelm.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"''',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '''"Windows"''',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en;q=0.9"
    }

    def parse(self, response):
        categories = ['https://www.westelm.com/shop/furniture/']
        for category in categories:
            yield scrapy.Request(category, headers=self.HEADERS, callback=self.parse_nav, dont_filter=True)

    def parse_nav(self, response):
        sub_categories = response.xpath('//div[@data-component="Shop-GridItem"]/a/@href').getall()
        for sub_category in sub_categories:
            start = 0
            if 'all-' not in sub_category:
                c_id = sub_category.split('/')[-1]
                if c_id:
                    products_link = f'https://core.dxpapi.com/api/v1/core/?q={c_id}&start={start}&rows=20&request_type=search&search_type=category&request_id=713500820437&_br_uid_2=uid=7982508622742:v=12.0:ts=1638712609427:hc=10&account_id=4083&url=https://www.westelm.com/&domain_key=westelm_en_we_prd_d2&fq=inactive%3A%22false%22&fq=availability_logic%3A%22true%22&fl=pid%2Cprice%2Cprice_range%2Csale_price%2Csale_price_range%2Cthumb_image%2Ctitle%2CeligibleForQuickBuy%2CpipThumbnailMessages%2Cflags%2CisBopisOnly%2CimageOverride%2CaltImages%2Cstore_ids%2Ccategory_name_attr%2Ccategory_id_attr%2CpageLoadImages%2CimageRollOvers%2ChoverImages%2Cthumb_image_attr%2CleaderSkuImage%2CswatchesDisplay%2CmoreSwatchesCount%2CproductPriceType%2CmaxDiscountPercent'
                    yield scrapy.Request(products_link, headers=self.HEADERS, callback=self.parse_json, meta={'c_id': c_id, 'start': start}, dont_filter=True)
    
    def parse_json(self, response):
        json_data = json.loads(response.text)
        for product in json_data['response']['docs']:
            
            try:
                images = product['altImages'].split(',')
            except:
                images = []

            swatches = []
            index = 0
            try:
                for swatch in product['swatchesDisplay'].split('~'):
                    swatch = swatch.split(';')
                    swatch_index = index
                    swatch_images = swatch[1:-1]
                    swatch_name = swatch[-1]
                    swatches.append({'index': swatch_index,
                                    'images': swatch_images,
                                    'name': swatch_name})
                    index += 1
            except:
                pass

            product_link = 'https://www.westelm.com/products/' + product['pid']            
            p = {
                'SKU': product['pid'],
                'URL': product_link,
                'Main Category': '',
                'Sub Category 1': '',
                'Sub Category 2': '',
                'Sub Category 3': '',
                'Product Name': product['title'],
                'Rating': '',
                '# of reviews': '',
                'Price': product['price'],
                'Sale Price': product['sale_price'] if product['sale_price'] != product['price'] else '',
                'Details': '',
                'Dimension': '',
                'Swatches': swatches,
                'Main Image': images[0] if len(images) else '',
                'Image 1': images[1] if len(images) > 1 else '',
                'Image 2': images[2] if len(images) > 2 else '',
                'Image 3': images[3] if len(images) > 3 else '',
                'Image 4': images[4] if len(images) > 4 else '',
                'Image 5': images[5] if len(images) > 5 else '',
                'Image 6': images[6] if len(images) > 6 else '',
                'Image 7': images[7] if len(images) > 7 else '',
                'Image 8': images[8] if len(images) > 8 else ''
            }
            yield scrapy.Request(product_link, headers=self.HEADERS, callback=self.parse_product, meta={'p': p}, dont_filter=False)
        if json_data['response']['docs']:
            start = response.meta["start"] + 20
            products_link = f'https://core.dxpapi.com/api/v1/core/?q={response.meta["c_id"]}&start={start}&rows=20&request_type=search&search_type=category&request_id=713500820437&_br_uid_2=uid=7982508622742:v=12.0:ts=1638712609427:hc=10&account_id=4083&url=https://www.westelm.com/&domain_key=westelm_en_we_prd_d2&fq=inactive%3A%22false%22&fq=availability_logic%3A%22true%22&fl=pid%2Cprice%2Cprice_range%2Csale_price%2Csale_price_range%2Cthumb_image%2Ctitle%2CeligibleForQuickBuy%2CpipThumbnailMessages%2Cflags%2CisBopisOnly%2CimageOverride%2CaltImages%2Cstore_ids%2Ccategory_name_attr%2Ccategory_id_attr%2CpageLoadImages%2CimageRollOvers%2ChoverImages%2Cthumb_image_attr%2CleaderSkuImage%2CswatchesDisplay%2CmoreSwatchesCount%2CproductPriceType%2CmaxDiscountPercent'
            yield scrapy.Request(products_link, headers=self.HEADERS, callback=self.parse_json, meta={'c_id': response.meta["c_id"], 'start': start}, dont_filter=True)

    def parse_product(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        details = soup.find('div', class_='dream-pip-details').text.replace('Details', '').replace('\n', ' ').replace('show more', '').strip() if soup.find('div', class_='dream-pip-details') else ''
        dimensions = soup.find('div', class_='dream-pip-dimensions').text.replace('Dimensions', '').replace('\n', ' ').strip() if soup.find('div', class_='dream-pip-dimensions') else ''
        texts = soup.find_all('div', class_='accordion-contents')
        if len(details) < 10 and len(texts) > 0:
            details = texts[0].text.replace('\n', ' ').strip()
        if len(dimensions) < 10 and len(texts) > 1:
            dimensions = texts[1].text.replace('\n', ' ').strip()
        p = response.meta['p']
        p['Details'] = details
        p['Dimension'] = dimensions
        categories = response.xpath('//ul[@id="breadcrumb-list"]/li/a/span/text()').getall()
        p['Main Category'] = categories[0] if len(categories) else ''
        p['Sub Category 1'] = categories[1] if len(categories) > 1 else ''
        p['Sub Category 2'] = categories[2] if len(categories) > 2 else ''
        p['Sub Category 3'] = categories[3] if len(categories) > 3 else ''
        
        x = json.loads(response.xpath('//script[@type="application/ld+json"]/text()').get().replace('\n', ''))
        p['SKU'] = x['sku']
        
        if 'collection' in response.url:
            for sub_product in response.xpath('//section[contains(@class, "subset-section")]/div[@class="product-subset "]'):
                soup = BeautifulSoup(sub_product.get(), 'html.parser')
                prices = soup.find('div', class_='product-price').text.replace(',', '')
                prices = re.findall('[$][0-9]*', prices)
                prices2 = ''
                for item in prices:
                    item = item.replace('$', '')
                try:
                    prices2 = re.findall('[$][0-9]*', soup.find('span', class_='price-strike-special').text.replace(',', ''))
                    print(prices2)
                except:
                    pass
                sku_json = json.loads(sub_product.xpath('//div[@class="quantity-input__container"]/input/@data-addtocart').get())
                p['SKU'] = sku_json['sku']
                p['Product Name'] = sub_product.xpath('.//h3/text()').get()
                p['Sale Price'] = ''
                p['Price'] = ''
                if len(prices) == 1:
                    p['Price'] = prices[0]
                elif len(prices) == 2:
                    p['Price'] = ' - '.join(prices)
                elif len(prices) == 3:
                    p['Price'] = prices[0]
                    p['Sale Price'] = ' - '.join(prices[1:])
                elif len(prices) == 4:
                    p['Price'] = ' - '.join(prices[:2])
                    p['Sale Price'] = ' - '.join(prices[2:])

                if not p['Price'] and p['Sale Price']:
                    p['Price'] = p['Sale Price']
                    p['Sale Price'] = ''
                if prices2:
                    p['Price'] = ' - '.join(prices2)
                p['Main Image'] = sub_product.xpath('.//img/@src').get()
                yield(p)
        else:
            yield(p)
