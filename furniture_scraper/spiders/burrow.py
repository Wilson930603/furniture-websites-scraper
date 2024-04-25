import scrapy
import json
from bs4 import BeautifulSoup
import re
import simplejson

class burrowspider(scrapy.Spider):
    name = 'burrow'
    allowed_domains = ['burrow.com']
    start_urls = ['https://burrow.com/']
    custom_settings ={
        'DOWNLOADER_MIDDLEWARES':{'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
        },
    }

    HEADERS = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    }

    def parse(self, response):
        categories = ['https://www.burrow.com/']
        for category in categories:
            yield scrapy.Request(category, headers=self.HEADERS, callback=self.parse_nav, dont_filter=True)

    def parse_nav(self, response):
        sub_categories = response.xpath('//div[@class="links-section"]//a[contains(.,"Shop All")]')
        
        
        for sub_category in sub_categories:
            theUrl = sub_category.xpath('./@href').get()
            mainCategory = sub_category.xpath('./text()').get()
            mainCategory = mainCategory.replace("Shop All ","")
            products_link = 'https://www.burrow.com'+theUrl
            yield scrapy.Request(products_link, headers=self.HEADERS, callback=self.parse_json,dont_filter=False)
            

        ## For Rugs
        products_link = 'https://www.burrow.com'+'/rugs'
        yield scrapy.Request(products_link, headers=self.HEADERS, callback=self.parse_json,dont_filter=False)        

    def parse_json(self, response):
        rawJson = response.xpath("//script[contains(.,'PRELOADED_STATE')]/text()").get()
        reJson = rawJson.replace("window.__PRELOADED_STATE__ = ","").replace("\\","\\\\")
        json_data = json.loads(reJson)['page']['data']['content']['components']
        
        totalItem = 0
        for components in json_data:
            if(components['type']=='ProductCollection'):
                collections = components['collections'][0]['productCollectionItems']
                crumbs2 = components['collections'][0]['header']
                for item in collections:
                    try:
                        itemUrl = "https://www.burrow.com"+item['item']['url']
                        totalItem+=1
                        
                        yield scrapy.Request(itemUrl, headers=self.HEADERS, callback=self.parse_product, dont_filter=False)
                    except:
                        pass
                    
        if(totalItem==0):
            json_data = json.loads(reJson)['page']['data']['content']['productCollections']
            for components in json_data:
                
                collections = components['productCollectionItems']
                if(len(collections)>0):
                    for item in collections:
                        try:
                            itemUrl = "https://www.burrow.com"+item['item']['url']+"?sku="+item['item']['sku']
                            yield scrapy.Request(itemUrl, headers=self.HEADERS, callback=self.parse_product,dont_filter=False)
                        except:
                            pass

    def parse_html(self, html):
        elem = BeautifulSoup(html, features="html.parser")
        text = ''
        for e in elem.descendants:
            if isinstance(e, str):
                text += e
            elif e.name in ['br',  'p', 'h1', 'h2', 'h3', 'h4','tr', 'th']:
                text += '\n'
            elif e.name == 'td':
                text += ' | '
            elif e.name == 'li':
                text += '\n- '
        return text

    def parse_product(self, response):
        rawJson = response.xpath("//script[contains(.,'PRELOADED_STATE')]/text()").get()
        reJson = rawJson.replace("window.__PRELOADED_STATE__ = ","").replace("\<","\\\\<")
        json_data = json.loads(reJson)['product']['data']['details']
        try:
            baseSku = json_data['skuSplit']['sku']
            skuOpt = json_data['skuSplit']['size']

            countVariants = 0
            checkVariants=json_data['productModifiers']
            for checkVariant in checkVariants:
                if(checkVariant['slug']=='size'):
                    variants = checkVariant['options']
                    countVariants+=1

                    for variant in variants:
                        value = variant['value']
                        newSku = baseSku.replace(skuOpt,value)
                        newUrl = response.url+"?sku="+newSku
                        yield scrapy.Request(newUrl, headers=self.HEADERS, callback=self.parse_product_variants,dont_filter=False)
        except:
            countVariants = 0
        
        if(countVariants==0):
            price = json_data['pricing']['price']['raw']
            try:
                salePrice = json_data['pricing']['salePrice']['raw']
                if(salePrice == None):
                    salePrice = ''
            except:
                salePrice = ''
            
            dimText = ''
            dimensions = json_data['dimensions']
            for dimension in dimensions:
                dimText += dimension['header'] + " " + dimension['dimension'] + ";\n"
            
            images = []
            images_lists = json_data['gallery']
            for images_list in images_lists:
                images.append(images_list['images'][0]['url'])
            try:
                breadcrumbs = response.xpath("//*[@class='pdp-breadcrumbs']/a/text()").get()
            except:
                breadcrumbs = ''

            swatches = []
            index = 0
            try:
                for swatch in response.xpath('//div[@class="pdp-options-ul fabric"]/div/@title').getall():
                    swatch_index = index
                    swatches.append({'index': swatch_index,
                                    'images': [],
                                    'name': swatch})
                    index += 1
            except:
                pass

            p = {
                'SKU': json_data['sku'],
                'URL': response.url,
                'Main Category': breadcrumbs,
                'Sub Category 1': '',
                'Sub Category 2': '',
                'Sub Category 3': '',
                'Product Name': json_data['name'],
                'Rating': json_data['bottomline']['averageScore'],
                '# of reviews': json_data['bottomline']['totalReview'],
                'Price': price,
                'Sale Price': salePrice,
                'Details': json_data['description'],
                'Dimension': dimText,
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

    def parse_product_variants(self, response):
        rawJson = response.xpath("//script[contains(.,'PRELOADED_STATE')]/text()").get()
        reJson = rawJson.replace("window.__PRELOADED_STATE__ = ","").replace("\<","\\\\<")
        json_data = json.loads(reJson)['product']['data']['details']
        
        price = json_data['pricing']['price']['raw']
        try:
            salePrice = json_data['pricing']['salePrice']['raw']
            if(salePrice == None):
                salePrice = ''
        except:
            salePrice = ''
        
        dimText = ''
        dimensions = json_data['dimensions']
        for dimension in dimensions:
            dimText += dimension['header'] + " " + dimension['dimension'] + ";\n"
        
        images = []
        images_lists = json_data['gallery']
        for images_list in images_lists:
            images.append(images_list['images'][0]['url'])
        try:
            breadcrumbs = response.xpath("//*[@class='pdp-breadcrumbs']/a/text()").get()
        except:
            breadcrumbs = ''

        p = {
            'SKU': json_data['sku'],
            'URL': response.url,
            'Main Category': breadcrumbs,
            'Sub Category 1': '',
            'Sub Category 2': '',
            'Sub Category 3': '',
            'Product Name': json_data['name'],
            'Rating': json_data['bottomline']['averageScore'],
            '# of reviews': json_data['bottomline']['totalReview'],
            'Price': price,
            'Sale Price': salePrice,
            'Details': json_data['description'],
            'Dimension': dimText,
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
