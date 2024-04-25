import scrapy
import json
from bs4 import BeautifulSoup

class featherspider(scrapy.Spider):
    name = 'feather'
    allowed_domains = ['livefeather.com']
    start_urls = ['https://livefeather.com/']
    completeSku = []

    custom_settings ={
        'DOWNLOADER_MIDDLEWARES':{'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
        },
    }

    HEADERS = {
        'accept':'*/*',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type':'application/json; charset=utf-8',
        'dnt':'1',
        'origin':'https://livefeather.com',
        'referer':'https://livefeather.com/',
        'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'empty',
        'sec-fetch-mode':'cors',
        'sec-fetch-site':'same-site',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    }

    def parse(self, response):
        categories = ['https://www.livefeather.com/']
        for category in categories:
            yield scrapy.Request(category, headers=self.HEADERS, callback=self.parse_nav, meta={'offset':0}, dont_filter=True)

    def parse_nav(self, response):
        offset = response.meta['offset']
        print(offset)
        url = 'https://api.livefeather.com/external-api/products'
        data = '''{"offset":'''+str(offset)+''',"numItems":40,"sort":null,"order":null,"categories":[],"classes":[],"subclasses":[],"filter":{"deliveryArea":null,"brands":[],"classes":[],"subclasses":[],"availability":[]}}'''

        yield scrapy.Request(url, headers=self.HEADERS, callback=self.parse_product,method='POST',meta={'offset':offset},body=data)

    def parse_html(self, html):
        elem = BeautifulSoup(html, features="html.parser")
        text = ''
        for e in elem.descendants:
            if isinstance(e, str):
                text += e
            elif e.name in ['br',  'p', 'h1', 'h2', 'h3', 'h4','tr', 'th','ul']:
                text += ''
            elif e.name == 'td':
                text += ' | '
            elif e.name == 'li':
                text += '• '
            elif e.name == 'div':
                text += '\n'
        return text

    def parse_product(self, response):
        offset = response.meta['offset']
        offset_next = offset+40

        rawJson = json.loads(response.text)['pageData']
        for product in rawJson:
            urlVariant = 'https://api.livefeather.com/external-api/products/'+product['identifier']
            yield scrapy.Request(urlVariant, headers=self.HEADERS, callback=self.parse_variant,dont_filter=True)
            
        if(len(rawJson)==40):
            yield scrapy.Request('https://www.livefeather.com/', headers=self.HEADERS, callback=self.parse_nav, meta={'offset':offset_next}, dont_filter=True)

    def parse_variant(self, response):
        product = json.loads(response.text)
        title = product['title']
        sku = product['identifier']
        
        breadcrumb = []
        breadcrumb.append("Furniture")
        categories = product['categories']
        for category in categories:
            breadcrumb.append(category['name'])
            break

        description = product['description']

        variants = product['variants']
        for variant in variants:
            forsku = variant['identifier']
            price = variant['retailPrice']
            salePrice = variant['buyPrice']
            if(price==salePrice):
                salePrice = ''
            
            dimensionText = ''
            try:
                dimensionsW = variant['dimensions']['width']
                dimensionText+="Width: "+dimensionsW+"\n"
            except:
                dimensionsW = ''
            try:
                dimensionsH = variant['dimensions']['height']
                dimensionText+="Height: "+dimensionsH+"\n"
            except:
                dimensionsH = ''
            try:
                dimensionsL = variant['dimensions']['length']
                dimensionText+="Length: "+dimensionsL+"\n"
            except:
                dimensionsL = ''
            try:
                dimensionsWe = variant['dimensions']['weight']
                dimensionText+="Weight: "+dimensionsWe+"\n"
            except:
                dimensionsWe = ''
            
            images = []
            try:
                images.append(variant['mainImage']['desktop']+'?auto=compress,format&cs=srgb&dpr=1&fit=max&h=500&q=80&w=747')
            except:
                pass
            imgDetails = variant['detailImages']
            for imgDetail in imgDetails:
                images.append(imgDetail['desktop']+'?auto=compress,format&cs=srgb&dpr=1&fit=max&h=500&q=80&w=747')
            imgOthers = variant['otherImages']
            for imgOther in imgOthers:
                images.append(imgOther['desktop']+'?auto=compress,format&cs=srgb&dpr=1&fit=max&h=500&q=80&w=747')

            swatches = []
            index = 0
            try:
                for swatch in product['options']:
                    if 'color' in swatch['name'].lower():
                        swatch_index = index
                        swatch_images = []
                        swatch_name = swatch['name']
                        swatches.append({'index': swatch_index,
                                        'images': swatch_images,
                                        'name': swatch_name})
                        index += 1
            except:
                pass

            p = {
                'SKU': sku+'-'+forsku,
                'URL': 'https://www.livefeather.com/products/'+sku,
                'Main Category': breadcrumb[0] if len(breadcrumb) > 0 else '',
                'Sub Category 1': breadcrumb[1] if len(breadcrumb) > 1 else '',
                'Sub Category 2': breadcrumb[2] if len(breadcrumb) > 2 else '',
                'Sub Category 3': breadcrumb[3] if len(breadcrumb) > 3 else '',
                'Product Name': title,
                'Rating': '',
                '# of reviews': '',
                'Price': price,
                'Sale Price': salePrice,
                'Details': description,
                'Dimension': dimensionText,
                'Swatches': swatches,
                'Main Image': images[0] if len(images) > 0 else '',
                'Image 1': images[1] if len(images) > 1 else '',
                'Image 2': images[2] if len(images) > 2 else '',
                'Image 3': images[3] if len(images) > 3 else '',
                'Image 4': images[4] if len(images) > 4 else '',
                'Image 5': images[5] if len(images) > 5 else '',
                'Image 6': images[6] if len(images) > 6 else '',
                'Image 7': images[7] if len(images) > 7 else '',
                'Image 8': images[8] if len(images) > 8 else ''
            }

            yield(p)
