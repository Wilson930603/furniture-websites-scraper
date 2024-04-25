import scrapy
from bs4 import BeautifulSoup

class WilliamsSonomaSpider(scrapy.Spider):
    name = 'williamsonoma'
    start_urls = ['https://www.williams-sonoma.com/']

    HEADERS = {
        "authority": "www.williams-sonoma.com",
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

    productsAPI = f'https://core.dxpapi.com/api/v1/core/?q=XQUERYX&start=XSTARTX&rows=20&request_type=search&search_type=category&request_id=418868019508&_br_uid_2=uid=5375918860225:v=12.0:ts=1642137036363:hc=2&account_id=4060&url=https://www.williams-sonoma.com/&domain_key=williamssonoma_en_ws_prd_d1&fq=inactive%3A%22false%22&fq=availability_logic%3A%22true%22&fl=pid%2Cprice%2Cprice_range%2Csale_price%2Csale_price_range%2Cthumb_image%2Ctitle%2CeligibleForQuickBuy%2CpipThumbnailMessages%2Cflags%2CisBopisOnly%2CimageOverride%2CaltImages%2Cstore_ids%2Ccategory_name_attr%2Ccategory_id_attr%2CpageLoadImages%2CimageRollOvers%2ChoverImages%2Cthumb_image_attr%2CleaderSkuImage%2CswatchesDisplay%2CmoreSwatchesCount%2CproductPriceType%2CmaxDiscountPercent&efq=store_ids:(%22ST%3A0218%22%20OR%20%22ST%3A0011%22%20OR%20%22ST%3A0618%22%20OR%20%22ST%3A0848%22%20OR%20%22ST%3A6134%22%20OR%20%22ST%3A6073%22%20OR%20%22ST%3A0814%22%20OR%20%22ST%3A0856%22%20OR%20%22ST%3A0726%22%20OR%20%22ST%3A0413%22%20OR%20%22ST%3A0795%22%20OR%20%22ST%3A0625%22%20OR%20%22ST%3A6049%22%20OR%20%22ST%3A0021%22%20OR%20%22ST%3A0945%22%20OR%20%22ST%3A0308%22%20OR%20%22ST%3A6213%22)%20OR%20fulfillment_locations:(%22COI%22%20OR%20%22COI_CMO%22%20OR%20%22COI_SS%22%20OR%20%22DEFAULT%22)'
    def parse(self, response):
        categories = ['https://www.williams-sonoma.com/shop/home-furniture/?cm_type=gnav']
        for category in categories:
            yield scrapy.Request(category, callback=self.parse_category, headers=self.HEADERS, dont_filter=True)

    def parse_category(self, response):
        for sub_category in response.xpath('//a[@class="category-link"]/@href').getall():
            URL = 'https://www.williams-sonoma.com' + sub_category
            if '.html' in URL:
                continue
            elif '/shop/' in URL:
                if '/m/' not in URL:
                    query = URL.split('/')[6] if len(URL.split('/')) > 6 else URL.split('/')[-1]
                    query = query.split('--')[-1].strip('-').strip()
                    URL = self.productsAPI.replace('XQUERYX', query).replace('XSTARTX', '0')
                    yield scrapy.Request(URL, callback=self.parse_products, headers=self.HEADERS, meta={'q': query, 's': '0'}, dont_filter=True)

    def parse_products(self, response):
        json_response = response.json()
        for product in json_response['response']['docs']:
            URL = 'https://www.williams-sonoma.com/products/' + product['pid']
            yield scrapy.Request(URL, callback=self.parse_product, headers=self.HEADERS, meta={'product': product})
        
        if int(response.json()['response']['numFound']) > (int(response.meta['s']) + 200):
            URL = self.productsAPI.replace('XQUERYX', response.meta['q']).replace('XSTARTX', str(int(response.meta['s']) + 200))
            yield scrapy.Request(URL, callback=self.parse_products, headers=self.HEADERS, meta={'q': response.meta['q'], 's': int(response.meta['s']) + 200}, dont_filter=True)
    
    def parse_product(self, response):
        product = response.meta['product']
        categories = response.xpath('//li[@itemprop="itemListElement"]/a/span/text()').getall()
        images = []
        for i in range(5):
            image = response.xpath(f'//img[@alt="Alternate view {i}"]/@data-src').get()
            if image:
                image = image.replace('-r.jpg', '-z.jpg')
                images.append(image)     

        if not images:
            images = [response.xpath('//img[@id="hero"]/@src').get()]   
            
        dimensions = ''
        for dimension in response.xpath('//div[@class="dream-pip-dimensions-list"]/div/ul').xpath('.//li/text()').getall():
            dimensions = dimensions + dimension.strip() + ' '
        if not dimensions:
            for element in  response.xpath('//div[@class="accordion-tab-copy"]'):
                if 'DIMENSIONS' in element.get():
                    for li in element.xpath('.//ul/li'):
                        dimensions = dimensions + li.xpath('.//text()').get().strip() + ' '
                    break
        if not dimensions:
            accordions = response.xpath('//dl[@class="accordion-component "]')
            for i in range(len(accordions.xpath('.//dt'))):
                if 'Dimensions' in accordions.xpath('.//dt/text()')[i].get():
                    for item in accordions.xpath('.//dd')[i].xpath('.//div/div/ul/li/text()').getall():
                        dimensions = dimensions + item.strip() + ' '
                    break

        soup = BeautifulSoup(response.text, 'lxml')
        details = soup.find('div', class_='dream-pip-details').text.replace('Details', '').replace('\n', ' ').replace('show more', '').strip() if soup.find('div', class_='dream-pip-details') else ''
        if not details:
            details = soup.find('div', class_='accordion-tab-copy').text.replace('Details', '').replace('\n', ' ') if soup.find('div', class_='accordion-tab-copy') else ''

        
        for i in range(5):
            if '\n' in dimensions or '\n' in details:
                dimensions = dimensions.replace('\n', ' ')
                details = details.replace('\n', ' ')
            else:
                break
        try:
            rating = float(response.xpath('//span[@class="stars"]/img/@title').get().split('Rated')[1].split('out')[0])
        except:
            rating = ''

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

        yield {
            'SKU': product['pid'],
            'URL': 'https://www.williams-sonoma.com/products/' + product['pid'],
            'Main Category': categories[0] if len(categories) else '',
            'Sub Category 1': categories[1] if len(categories) > 1 else '',
            'Sub Category 2': categories[2] if len(categories) > 2 else '',
            'Sub Category 3': categories[3] if len(categories) > 3 else '',
            'Product Name': product['title'],
            'Rating': rating,
            # '# of reviews': ',
            'Price': ' - '.join([str(x) for x in product['price_range']]),
            'Sale Price': ' - '.join([str(x) for x in product['sale_price_range']]) if product['sale_price_range'] != product['price_range'] else '',
            # 'Member Prices': '',
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