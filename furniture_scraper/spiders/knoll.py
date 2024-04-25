import scrapy
import json
from bs4 import BeautifulSoup
import re
from lxml import etree,html
import requests

class knollspider(scrapy.Spider):
    name = 'knoll'
    allowed_domains = ['knoll.com']
    start_urls = ['https://knoll.com/']
    completeSku = []

    custom_settings ={
        'DOWNLOADER_MIDDLEWARES':{'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
        },
    }

    HEADERS = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language':'en-US,en;q=0.9',
        'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'same-origin',
        'sec-fetch-user':'?1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    }

    def parse_html(self, html):
        elem = BeautifulSoup(html, features="html.parser")
        text = ''
        for e in elem.descendants:
            if isinstance(e, str):
                text += e
            elif e.name in ['h5']:
                text += '\n'
            elif e.name in ['br',  'p', 'h1','h2','h3', 'h4','tr', 'th','ul']:
                text += ''
            elif e.name == 'td':
                text += ' | '
            elif e.name == 'li':
                text += '• '
            elif e.name == 'div':
                text += '\n'
        return text

    def parse(self, response):
        url1 = "https://www.knoll.com/shop"
        yield scrapy.Request(url1, headers=self.HEADERS, callback=self.parse_nav, dont_filter=True)

    def parse_nav(self, response):
        domainUrl = "https://www.knoll.com"
        mainCategories = response.xpath("//div[@class='second-level-menu']/ul[1]/li")
        for main in mainCategories:
            mainCat = main.xpath("./a/text()").get()
            if(mainCat != 'Inspiration' and mainCat != 'Gifts'):
                subCategories = main.xpath(".//div[@class='third-level-menu']//li/a")
                for subCategory in subCategories:
                    subUrl = subCategory.xpath("./@href").get()
                    subCat = subCategory.xpath("./text()").get()
                    yield scrapy.Request(url=domainUrl+subUrl,headers=self.HEADERS, callback = self.parse_variant, meta={'mainCategory':mainCat,'subCategory':subCat},dont_filter=True)

    def parse_variant(self, response):
        domainUrl = "https://www.knoll.com"
        products = response.xpath("//*[contains(@class,'product_catalog ')]/ul[contains(@class,'box-grid')]/li")

        for product in products:
            prodUrl = product.xpath("./a/@href").get().strip()
            prodImg = product.xpath("./a/span/img/@src").get()
            prodPrice = product.xpath(".//*[@class='price-label']/text()").get()
            yield scrapy.Request(url=domainUrl+prodUrl,headers=self.HEADERS, callback = self.parse_product, meta={'mainCategory':response.meta['mainCategory'],'subCategory':response.meta['subCategory'],'mainImg':prodImg,'prodPrice':prodPrice},dont_filter=False)


    def parse_product(self, response):
        images = []
        images.append("https://www.knoll.com"+response.meta['mainImg'])
        otherimages = response.xpath("//*[@id='hiddenimages']//li/a/@data-zoom").getall()
        for otherimage in otherimages:
            images.append("https://www.knoll.com"+otherimage)
        try:
            skuRaw = response.xpath("//script[contains(.,'loadBasic')]").get()
            sku = re.findall(r"/configurator/parts/(.+?)\'",skuRaw)[0]
        except:
            sku = ''

        details = response.xpath("//section[@class='bodyContentBlock']/*").getall()
        detailsText = self.parse_html(''.join(details))

        dimensionsText = ''
        dimensions = response.xpath("//*[@class='section_head' and contains(.,'Dimensions')]/following-sibling::*//table")
        tableHead = dimensions.xpath(".//tr[1]/th")
        headers = []
        for tableH in tableHead:
            temp = tableH.xpath(".//text()").getall()
            tempText = ''.join(temp)
            tempText = tempText.replace("\n","")
            headers.append(tempText)
        tableContents = dimensions.xpath(".//tr")[1:]
        for tableC in tableContents:
            temp = tableC.xpath(".//td")
            tc = 0
            for te in temp:
                teText = te.xpath(".//text()").getall()
                teText = ''.join(teText).replace("\n","")
            
                dimensionsText+=headers[tc]+":"+teText+"\n"
                tc+=1
            dimensionsText+="\n"
        data = {'images':images,'sku':sku,'mainCategory':response.meta['mainCategory'],'subCategory':response.meta['subCategory'],'url':response.url,'details':detailsText,'dimensions':dimensionsText}
        if(sku!=''):
            yield scrapy.Request(url="https://www.knoll.com/configurator/parts/"+sku,headers=self.HEADERS, callback = self.parse_product_details, meta={'data':data},dont_filter=True)
        else:
            title = response.xpath("//*[@class='product_info']/h1//text()").getall()
            title = ''.join(title).replace("\n","")
            sku = response.xpath("//*[@class='product_info']/small/text()").get()
            sku = sku.replace("Item #","")
            try:
                price = response.xpath("//*[@class='unavailable']/h4/text()").get()
                price = price.replace("$","")
            except:
                try:
                    price = response.xpath("//*[@class='unavailable']/p/strong/text()").get()
                except:
                    price = ''

            if(sku not in self.completeSku):
                url = "https://www.knoll.com/configurator/parts/" + data['sku']

                headers = {
                    "authority": "www.knoll.com",
                    "pragma": "no-cache",
                    "cache-control": "no-cache",
                    "tracestate": "1504694@nr=0-1-1504694-1133779761-c920837b411349dd----1642675659842",
                    "traceparent": "00-8da417a125a045c3c711d2592a0d23a0-c920837b411349dd-01",
                    "sec-ch-ua-mobile": "?0",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
                    "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjE1MDQ2OTQiLCJhcCI6IjExMzM3Nzk3NjEiLCJpZCI6ImM5MjA4MzdiNDExMzQ5ZGQiLCJ0ciI6IjhkYTQxN2ExMjVhMDQ1YzNjNzExZDI1OTJhMGQyM2EwIiwidGkiOjE2NDI2NzU2NTk4NDJ9fQ==",
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "x-requested-with": "XMLHttpRequest",
                    "sec-fetch-site": "same-origin",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-dest": "empty",
                    "referer": "https://www.knoll.com/product/florence-knoll-settee",
                    "accept-language": "en-US,en;q=0.9",
                }

                i = 1
                swatches = []
                try:
                    dd = requests.request("GET", url, headers=headers).json()
                    partNumber = dd['partNumber']
                    if dd['groups'][-1]['choices']:
                        for swatch in dd['groups'][-1]['choices']:
                            swatches.append({'index': i,
                                            'images': f'https://www.knoll.com/static_resources/images/products/catalog/eco/parts/{partNumber}/{swatch["optionGroupCode"]}/{swatch["number"]}/thumb.jpg',
                                            'price': swatch['price'],
                                            'name': swatch['description']})
                            i += 1
                except:
                    pass
                self.completeSku.append(sku)
                p = {
                'SKU': sku,
                'URL': data['url'],
                'Main Category': data['mainCategory'],
                'Sub Category 1': data['subCategory'],
                'Sub Category 2': '',
                'Sub Category 3': '',
                'Product Name': title,
                'Rating': '',
                '# of reviews': '',
                'Price': price,
                'Sale Price': '',
                'Details': data['details'],
                'Dimension': data['dimensions'],
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
            
    def parse_product_details(self, response):
        tree = etree.fromstring(response.text)
        data = response.meta['data']


        url = "https://www.knoll.com/configurator/parts/" + data['sku']

        headers = {
            "authority": "www.knoll.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "tracestate": "1504694@nr=0-1-1504694-1133779761-c920837b411349dd----1642675659842",
            "traceparent": "00-8da417a125a045c3c711d2592a0d23a0-c920837b411349dd-01",
            "sec-ch-ua-mobile": "?0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            "newrelic": "eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjE1MDQ2OTQiLCJhcCI6IjExMzM3Nzk3NjEiLCJpZCI6ImM5MjA4MzdiNDExMzQ5ZGQiLCJ0ciI6IjhkYTQxN2ExMjVhMDQ1YzNjNzExZDI1OTJhMGQyM2EwIiwidGkiOjE2NDI2NzU2NTk4NDJ9fQ==",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "x-requested-with": "XMLHttpRequest",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.knoll.com/product/florence-knoll-settee",
            "accept-language": "en-US,en;q=0.9",
        }

        dd = requests.request("GET", url, headers=headers).json()
        i = 1
        swatches = []
        try:
            partNumber = dd['partNumber']
            if dd['groups'][-1]['choices']:
                for swatch in dd['groups'][-1]['choices']:
                    swatches.append({'index': i,
                                    'images': f'https://www.knoll.com/static_resources/images/products/catalog/eco/parts/{partNumber}/{swatch["optionGroupCode"]}/{swatch["number"]}/thumb.jpg',
                                    'price': swatch['price'],
                                    'name': swatch['description']})
                    i += 1
        except:
            pass
        
        
        if(data['sku'] == 'TP' or data['sku'] == 'TP!OUTDOOR'):
            try:
                title = tree.xpath("//name/text()")[0]
                basePrice = tree.xpath("//price/text()")[0]
                code = data['url'].replace("https://www.knoll.com/product/pillows-by-knolltextiles-indoor-outdoor-shop?p=","").replace("https://www.knoll.com/product/pillows-by-knolltextiles-shop?p=","")
                rawCode = code.split("-")[1]
                model = rawCode.split("_")[0]
                ### Use model to determine variant 
                totalPrice = float(basePrice)
                title1 = tree.xpath("//number[contains(.,'"+model+"')]/following-sibling::description/text()")
                price1 = tree.xpath("//number[contains(.,'"+model+"')]/following-sibling::price/text()")
                totalPrice += float(price1[0])
                price2 = tree.xpath("//parentChoice[contains(.,'"+model+"')]")
                for price2x in price2:
                    test = price2x.xpath("./following-sibling::defaultSelected/text()")
                    try:
                        if(test[0]=='Y'):
                            price2y = price2x.xpath("./preceding-sibling::price/text()")
                            totalPrice += float(price2y)
                            break
                    except:
                        pass

                title += " - " + title1[0]

                images = data['images']
                newSku = data['sku']+"-"+rawCode
                if(newSku not in self.completeSku):
                    self.completeSku.append(newSku)
                    p = {
                        'SKU': newSku,
                        'URL': data['url'],
                        'Main Category': data['mainCategory'],
                        'Sub Category 1': data['subCategory'],
                        'Sub Category 2': '',
                        'Sub Category 3': '',
                        'Product Name': title,
                        'Rating': '',
                        '# of reviews': '',
                        'Price': totalPrice,
                        'Sale Price': '',
                        'Details': data['details'],
                        'Dimension': data['dimensions'],
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
            except:
                pass
            
        else:
            title = tree.xpath("//name/text()")[0]
            price = tree.xpath("//price/text()")[0]
            
            images = data['images']
            newSku = data['sku']
            if(newSku not in self.completeSku):
                self.completeSku.append(newSku)
                p = {
                    'SKU': newSku,
                    'URL': data['url'],
                    'Main Category': data['mainCategory'],
                    'Sub Category 1': data['subCategory'],
                    'Sub Category 2': '',
                    'Sub Category 3': '',
                    'Product Name': title,
                    'Rating': '',
                    '# of reviews': '',
                    'Price': price,
                    'Sale Price': '',
                    'Details': data['details'],
                    'Dimension': data['dimensions'],
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