import scrapy
import requests
from bs4 import BeautifulSoup

class LazboySpider(scrapy.Spider):
    name = 'lazboy'
    allowed_domains = ['la-z-boy.com']
    start_urls = ['https://la-z-boy.com/']
    HEADERS = {
        "authority": "www.la-z-boy.com",
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
        "referer": "https://www.la-z-boy.com",
        "accept-language": "en-US,en;q=0.9"
    }

    def parse(self, response):
        sub_categories = response.xpath('//ul[@id="mega-nav"]/li/div/ul/li/a/@href').getall()
        for sub_category in sub_categories:
            if 'http' not in sub_category:
                sub_category = 'https://www.la-z-boy.com/' + sub_category
            if '-' in sub_category.split('/')[5]:
                yield scrapy.Request(sub_category, headers=self.HEADERS, callback=self.parse_sub_category, dont_filter=True)

    def parse_sub_category(self, response):
        products = response.xpath('//div[@class="product-tile"]')
        for product in products:
            link = 'https://www.la-z-boy.com/' + product.xpath('.//a/@href').get()
            yield scrapy.Request(link, headers=self.HEADERS, callback=self.parse_product, dont_filter=False)
        
        if products:
            new_link = response.url.split('?', 1)[0]
            No = '39'
            if 'No' in response.url:
                No = int(response.url.split('No=')[1].split('&')[0]) + 39
            new_link = new_link + f'?No={str(No)}&Nrpp=39&plpaction=loadmore'
            yield scrapy.Request(new_link, headers=self.HEADERS, callback=self.parse_sub_category, dont_filter=True)

    def parse_product(self, response):
        if 'http://schema.org/OutOfStock' in response.text:
            print('Out of stock', response.url)
            return
        price = response.xpath('//div[@class="regular-price"]/@aria-label').get()
        if price:
            price = price.split(':')[-1].replace('$', '')
        else:
            price = ''
        title = response.xpath('//h1[@class="product-name"]/text()').get()
        sku = response.xpath('//section[@class="product-page"]/@data-product-skuid').get()
        categories = response.xpath('//section[@class="breadcrumbs"]/ul/li/a/span/text()').getall()
        for category in categories:
            if len(category) < 2:
                categories.remove(category)

        ReviewsURL = f"https://cdn-ws.turnto.com/v5/sitedata/nlVU8iLFS6akCpgsite/{sku}/d/review/en_US/0/3/%7B%7D/H_RATED/false/true/"
        Reviews = requests.request("GET", ReviewsURL, headers=self.HEADERS).json()
        try:
            TotalPoints = 0
            for item in Reviews['filters'][0]['options']:
                TotalPoints += item['count'] * item['value']
            rating = round(((TotalPoints / (Reviews['total']*5))*5), 1)
            reviews = Reviews['total']
        except:
            rating = reviews = 0
        try:
            soup = BeautifulSoup(response.xpath('//div[@class="section-content product-details-info"]/div').get(), 'html.parser')
            details = soup.text.replace('\n', ' ').strip().replace('\t', ' ').replace('  ', ' ')
        except:
            details = ''
        try:
            soup = BeautifulSoup(response.xpath('//div[@id="product-dimensions-weight"]').get(), 'html.parser')
            dimensions = soup.text.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ').replace('Dimensions & Weight' , '').replace('  ', ' ').replace('  ', ' ').replace('Show More Less', '').strip()
        except:
            dimensions = ''
        images = response.xpath('//div[@class="product-image alt-img"]/img/@data-lazy').getall()
        image_urls = []
        for image in images:
            image_urls.append('https:' + image)

        swatches = []
        index = 0
        try:
            for swatch in response.xpath('//div[@id="base-cover-swatch-groups"]').xpath('.//div[contains(@class, "cover-selection-details")]'):
                swatch_images = 'https:' + swatch.xpath('.//a/@data-swatch').get()
                swatch_name = swatch.xpath('.//a/@data-color-name').get()
                swatch_price = swatch.xpath('.//a/@data-price-formatted').get().replace('$', '').replace(',', '')
                swatches.append({
                                'index': index,
                                 'images': swatch_images,
                                 'name': swatch_name.title()
                                })
                index += 1
                if index == 200:
                    break
        except Exception as err:
            print(err)
            pass

        yield {
            'SKU': sku,
            'URL': response.url,
            'Main Category': categories[0] if len(categories) else '',
            'Sub Category 1': categories[1] if len(categories) > 1 else '',
            'Sub Category 2': categories[2] if len(categories) > 2 else '',
            'Sub Category 3': categories[3] if len(categories) > 3 else '',
            'Product Name': title,
            'Rating': rating,
            '# of reviews': reviews,
            'Price': price,
            # 'Sale Price': '',
            'Details': details,
            'Dimension': dimensions,
            'Swatches': str(swatches).replace('\n', ''),
            'Main Image': image_urls[0] if image_urls else '',
            'Image 1': image_urls[1] if len(image_urls) > 1 else '',
            'Image 2': image_urls[2] if len(image_urls) > 2 else '',
            'Image 3': image_urls[3] if len(image_urls) > 3 else '',
            'Image 4': image_urls[4] if len(image_urls) > 4 else '',
            'Image 5': image_urls[5] if len(image_urls) > 5 else '',
        }