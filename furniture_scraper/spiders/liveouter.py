import scrapy
import json
import requests

class LiveouterSpider(scrapy.Spider):
    name = 'liveouter'
    allowed_domains = ['liveouter.com']
    start_urls = ['https://shopee.sg/']

    def parse(self, response):
        sub_categories = ['https://liveouter.com/sofas-and-sectionals',
                          'https://liveouter.com/chairs',
                          'https://liveouter.com/tables',
                          'https://liveouter.com/fire-pit-table']
        for sub_category in sub_categories:
            yield scrapy.Request(sub_category, callback=self.parse_sub_categories, dont_filter=True)
    
    def parse_sub_categories(self, response):
        products_links = response.xpath('//div[@class="col-xs-12 col-sm-4"]/a/@href').getall()
        for product_link in products_links:
            product_link = 'https://liveouter.com' + product_link
            yield scrapy.Request(product_link, callback=self.parse_product, dont_filter=True)

    def parse_product(self, response):
        script_data = response.xpath('//script[@type="application/ld+json"]/text()').get().replace('&quot;', '"')
        product = json.loads(script_data)
        desc_text = response.xpath('//div[contains(@class, "ProductDescription-module--productDescription")]').xpath('.//p/text()').get()
        dimension = response.xpath('//div[contains(@class, "ProductDimensions-module--productDimensions")]')
        dim_text = dimension.xpath('.//p/text()').getall()
        while ':' in dim_text:
            dim_text.remove(':')
        dimension_text = ''
        i = 0
        for text in dim_text:
            if not i%2:
                dimension_text = dimension_text + ' ' + text.replace(':', '') + ':'
            else:
                dimension_text = dimension_text + ' ' + text + ','
            i += 1
        dimension_text = dimension_text[1:-1]
        images = response.xpath('//div[contains(@class, "ProductGallery-module--thumbnails")]/div[contains(@class, "ProductGallery-module--imageContainer")]').xpath('.//img/@src').getall()
        for image in images:
            if 'e_blur' in image:
                images.pop(images.index(image))
        aggregateId = response.xpath('//div[contains(@class, "ProductDetails-module--titleRatingWrapper")]/div/@data-oke-reviews-collection-id').get()
        API_URL = f'https://api.okendo.io/v1/stores/c66de292-8b75-49c9-8801-e15b2b80e695/collections/{aggregateId}/review_aggregate'
        json_response = requests.get(API_URL).json()
        try:
            Totalrating = round(((json_response['reviewAggregate']['reviewRatingValuesTotal'] / (json_response['reviewAggregate']['reviewCount']*5))*5), 1)
        except:
            Totalrating = 0

        swatches = []
        index = 0
        try:
            for swatch in response.xpath('//ul[contains(@class, "module--colors")]/li/p/text()').getall():
                swatch_index = index
                swatches.append({'index': swatch_index,
                                'images': [],
                                'name': swatch})
                index += 1
        except:
            pass

        yield {
            'SKU': product['sku'],
            'URL': response.url,
            'Main Category': 'Furniture',
            'Sub Category 1': response.xpath('//a[contains(@class, "Breadcrumb-module--breadcrumbLink")]/text()').get(),
            # 'Sub Category 2': '',
            # 'Sub Category 3': '',
            'Product Name': product['name'],
            'Rating': Totalrating,
            '# of reviews': json_response['reviewAggregate']['reviewCount'] if 'reviewCount' in json_response['reviewAggregate'] else 0,
            'Price': product['offers']['price'],
            # 'Sale Price': ,
            'Details': desc_text,
            'Dimension': dimension_text,
            'Swatches': swatches,
            'Main Image': images[0],
            'Image 1': images[1] if len(images) > 1 else '',
            'Image 2': images[2] if len(images) > 2 else '',
            'Image 3': images[3] if len(images) > 3 else '',
            'Image 4': images[4] if len(images) > 4 else '',
            'Image 5': images[5] if len(images) > 5 else '',
        }
