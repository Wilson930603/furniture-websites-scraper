import scrapy
import json
from bs4 import BeautifulSoup

class arhausspider(scrapy.Spider):
    name = 'arhaus'
    allowed_domains = ['arhaus.com']
    start_urls = ['https://arhaus.com/']
    completeSku = []

    custom_settings ={
        'DOWNLOADER_MIDDLEWARES':{'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
        },
    }

    HEADERS = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    }

    def parse(self, response):
        categories = ['https://www.arhaus.com/']
        for category in categories:
            yield scrapy.Request(category, headers=self.HEADERS, callback=self.parse_nav, dont_filter=True)

    def parse_nav(self, response):
        domainName = 'https://www.arhaus.com'
        mainCategories = response.xpath('//li[@class="navigation-item js-hoverSub"]')
        for main in mainCategories:
            mainHeader = main.xpath('./a/text()').get()
            if('Holiday' not in mainHeader):
                subCategories = main.xpath('.//li[contains(@class,"navigation-item navigation-item--child")]')
                
                for subCategory in subCategories:
                    checkSubSubCategories = subCategory.xpath(".//*[@class='navigation-link navigation-link--grandchild']")
                    
                    if(len(checkSubSubCategories)==0):
                        subUrl = subCategory.xpath("./a/@href").get()
                    else:
                        for subSubCategories in checkSubSubCategories:
                            header = subSubCategories.xpath("./text()").get()
                            if('All ' not in header):
                                subsubUrl = subSubCategories.xpath("./@href").get()
                                categoryLink = domainName + subsubUrl + '?s=M&p=1000'
                                if(categoryLink=='https://www.arhaus.com/furniture/bedding/?s=M&p=1000'):
                                    categoryLink = 'https://www.arhaus.com/furniture/bedding/all-bedding/?s=M&p=1000'
                                
                                yield scrapy.Request(categoryLink, headers=self.HEADERS, callback=self.parse_category,dont_filter=False)


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

    def unique(self,list1):
        list_set = set(list1)
        unique_list = (list(list_set))
        return unique_list

    def parse_category(self, response):
        print('parse_category '+response.url)
        domainName = 'https://www.arhaus.com'
        products = response.xpath("//*[@class='product_grid-name']/a/@href").getall()
        if(len(products)>0):
            for product in products: 
                productLink = domainName+product
                yield scrapy.Request(productLink, headers=self.HEADERS, callback=self.parse_product,dont_filter=False)

    def parse_product(self, response):
        print(response.url)
        title = response.xpath('//h1[@property="id"]/text()').get()
        title = title.replace("\n","").replace("\r","").replace("\t","").replace("        ","")
        details = response.xpath('//*[@class="flavor-content" and @data-tab="details"]/div/*').getall()
        
        detailsText = self.parse_html(''.join(details))
        try:
            detailsText=detailsText.replace("\r\n                ","").replace("\r\n","").replace("\n\n","").replace("=-","-")
        except:
            detailsText = ''
        try:
            detailsText = detailsText[1:]
        except:
            detailsText = detailsText

        if(detailsText==''):
            details = response.xpath('//*[@class="flavor-content" and @data-tab="details"]/*').getall()
            detailsText = self.parse_html(''.join(details))

            try:
                detailsText=detailsText.replace("\r\n                ","").replace("\r\n","").replace("\n\n","").replace("=-","-")
            except:
                detailsText = ''
            try:
                detailsText = detailsText[1:]
            except:
                detailsText = detailsText

        imagesList = response.xpath('//div[@class="swiper-wrapper"]/img/@src').getall()
        images = self.unique(imagesList)
        
        breadcrumbs = response.xpath("//script[contains(.,'BreadcrumbList')]/text()").get()
        breadcrumbsJson = json.loads(breadcrumbs)['itemListElement']
        breadcrumb = []
        for bread in breadcrumbsJson:
            breadcrumb.append(bread['item']['name'].replace(" &amp;"," & "))
        try:
            breadcrumb = breadcrumb[:-1]
        except:
            pass

        try:
            sku = response.xpath('//*[@property="productId"]/text()').get()
        except:
            sku = ''
        
        try:
            dimensions = response.xpath("//*[@property='dimensions']/text()").get()
        except:
            dimensions = ''
        
        price = response.xpath('//*[@property="regularPrice"]/*[contains(@class,"js-price")]/text()').get()
        salePrice = response.xpath('//*[@property="salePrice"]/*[contains(@class,"js-price")]/text()').get()
        if(price==salePrice):
            salePrice = ''

        if(sku not in self.completeSku):
            self.completeSku.append(sku)

            swatches = []
            index = 0
            for swatch in response.xpath('//div[contains(@class, "color-swatch")]/div/@data-name').getall():
                swatch_index = index
                swatches.append({'index': swatch_index,
                                'images': [],
                                'name': swatch.title()})
                index += 1

            p = {
                'SKU': sku,
                'URL': response.url,
                'Main Category': breadcrumb[0] if len(breadcrumb) > 0 else '',
                'Sub Category 1': breadcrumb[1] if len(breadcrumb) > 1 else '',
                'Sub Category 2': breadcrumb[2] if len(breadcrumb) > 2 else '',
                'Sub Category 3': breadcrumb[3] if len(breadcrumb) > 3 else '',
                'Product Name': title,
                'Rating': '',
                '# of reviews': '',
                'Price': price,
                'Sale Price': salePrice,
                'Details': detailsText,
                'Dimension': dimensions,
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
