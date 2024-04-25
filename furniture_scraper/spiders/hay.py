import scrapy
import re

class hayspider(scrapy.Spider):
    name = 'hay'
    allowed_domains = ['us.hay.com']
    start_urls = ['https://us.hay.com/']
    completeSku = []
    history = []

    custom_settings ={
        'DOWNLOADER_MIDDLEWARES':{'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
        },
    }

    HEADERS = {
        'accept':'text/html, */*; q=0.01',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        #'cookie':'dwsid=we7yC223htueuiMTaqnKryGx15w_cO0BiDP03FqIZlIGBmoeo4Apf4Z9NL4HTQa8Vn4ocvJHeA3KsE5kQG2iFQ==; dwac_c6c2513d8be477902182f9aae2=MnOysb5A1wHmO2y8EGudttIslybsh7zb8LI%3D|dw-only|||USD|false|US%2FPacific|true; cqcid=bcncuHzJQUDa5lVFkrQ0aMDqB1; cquid=||; dwanonymous_bf0ce6c0471303687455a60485b8be61=bcncuHzJQUDa5lVFkrQ0aMDqB1; sid=MnOysb5A1wHmO2y8EGudttIslybsh7zb8LI; __cq_dnt=0; dw_dnt=0; dw=1; dw_cookies_accepted=1; liveagent_oref=https://hay.dk/; MrSoftwareSettings=%7B%22useIframeView%22%3A%22false%22%7D; liveagent_sid=a7df48c1-b231-4fcd-98ab-454da07356d4; liveagent_vc=2; liveagent_ptid=a7df48c1-b231-4fcd-98ab-454da07356d4',
        #'referer':'https://us.hay.com/accessories?lang=en_US',
        'sec-ch-ua':'"Chromium";v="96", "Opera GX";v="82", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'empty',
        'sec-fetch-mode':'cors',
        'sec-fetch-site':'same-origin',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50',
        'x-requested-with':'XMLHttpRequest',
    }

    def parse(self, response):
        categories = ['accessories','furniture','lighting']
        for category in categories:
            yield scrapy.Request(url='https://us.hay.com/'+category+'?lang=en_US&start=0&sz=45&format=page-element',callback=self.parse_products,headers=self.HEADERS)
            #break #testing

    def parse_products(self, response):
        baseUrl = response.url
        products = response.xpath("//a[@class='name-link']/@href").getall()
        for product in products:
            #product = '/on/demandware.store/Sites-hay-Site/en_US/Product-Variation?pid=2516310&dwvar_2516310_arm=reclining&dwvar_2516310_upholstery=metaphor&dwvar_2516310_size=three_seater'
            yield scrapy.Request(url='https://us.hay.com'+product,callback=self.parse_products_details, headers=self.HEADERS)
            #break #testing

        if(products is not None):
            if(len(products)==45):
                pageNow = re.findall(r"start=(\d+)",baseUrl)[0]
                pageNext = int(pageNow)+45
                urlNext = baseUrl.replace("start="+str(pageNow),"start="+str(pageNext))
                yield scrapy.Request(url = urlNext, callback=self.parse_products, headers=self.HEADERS)

    def parse_products_details(self,response):
        baseUrl = response.url
        
        theSku = response.xpath("//*[@class='item-number']/*[@class='value']/text()").get()
        if(theSku not in self.history):
            self.history.append(theSku)
            breadcrumb = response.xpath("//*[@class='breadcrumb']/a/text()").getall()
            price1 = response.xpath("//*[@id='product-content']//*[@class='product-standard-price']/text()").get()
            price2 = response.xpath("//*[@id='product-content']//*[@class='product-sales-price']/text()").get()
            price = price1
            salePrice = price2
            if(price1 is None):
                price = price2
                salePrice = ''
            imagesList = response.xpath("//*[@class='pdp-thumbnails']//*[@class='thumbnail-link']/@href").getall()
            images = []
            for img in imagesList:
                if('demandware.static' in img):
                    images.append('https://us.hay.com'+img)
                else:
                    if('null' not in img):
                        images.append(img.replace("//",""))
            dimensionText = ''.join(response.xpath("//*[@class='b3']//text()").getall())
            try:
                dimensionText = dimensionText.strip()
            except:
                pass
            selected = response.xpath("//*[@class='radio-selected-checked']/parent::*/text()").getall()
            variant_text=''
            variant_add = response.xpath("//*[@class='selected-swatch']/span/text()").get()
            try:
                variant_text=''.join(selected)
                variant_text=variant_text.strip()
            except:
                pass
            if(variant_text!=''):
                try:
                    variant_text+=';'+variant_add
                    variant_text=variant_text.replace("\n","")
                except:
                    pass
            else:
                try:
                    variant_text=variant_add.replace("\n","")
                except:
                    pass

            swatches = []
            index = 0
            try:
                for swatch in response.xpath('//ul[@class="swatches color img-attr"]').xpath('.//li[contains(@class, "selectable")]/a'):
                    swatch_images = swatch.xpath('.//img/@src').get()
                    swatch_name = swatch.xpath('.//@title').get()
                    swatches.append({'index': index,
                                    'images': swatch_images,
                                    'name': swatch_name})
                    index += 1
            except:
                pass

            p = {
                'SKU': theSku,
                'URL': baseUrl,
                'Main Category': breadcrumb[0].strip() if len(breadcrumb) > 0 else '',
                'Sub Category 1': breadcrumb[1].strip() if len(breadcrumb) > 1 else '',
                'Sub Category 2': breadcrumb[2].strip() if len(breadcrumb) > 2 else '',
                'Sub Category 3': breadcrumb[3].strip() if len(breadcrumb) > 3 else '',
                'Product Name': response.xpath("//*[@itemprop='name']/text()").get(),
                'Rating': '',
                '# of reviews': '',
                'Price': price,
                'Sale Price': salePrice,
                'Details': response.xpath("//*[@id='product-content']//*[@class='description-short-block']/text()").get(),
                'Variant': variant_text,
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
            try:
                p['Product Name'] = p['Product Name'].strip()
            except:
                pass
            try:
                p['Details'] = p['Details'].strip()
            except:
                pass
            try:
                p['Variant'] = p['Variant'].strip()
            except:
                pass
            try:
                p['Dimension'] = p['Dimension'].strip()
            except:
                pass

            yield(p)
            variants = response.xpath("//*[contains(@class,'swatchanchor ')]/@href").getall()
            for variant in variants:
                yield scrapy.Request(url=variant,callback=self.parse_products_details,headers=self.HEADERS)
                #break