import scrapy
import json
from bs4 import BeautifulSoup
import re
import simplejson

class modernspider(scrapy.Spider):
    name = '2modern'
    allowed_domains = []
    start_urls = ['https://2modern.com/']
    completeSku = []
    history = []
    ### Need to use proxy ###
    # custom_settings ={
    #     'DOWNLOADER_MIDDLEWARES':{'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
    #     },
    # }

    HEADERS = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        #'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        'cache-control':'no-cache',
        #'cookie':'secure_customer_sig=; localization=; cart_currency=USD; _orig_referrer=; _landing_page=%2F; _y=df9d7b31-c649-466c-86de-1d2a4172eda6; _shopify_y=df9d7b31-c649-466c-86de-1d2a4172eda6; _tracking_consent=%7B%22lim%22%3A%5B%22GDPR%22%5D%2C%22reg%22%3A%22%22%2C%22v%22%3A%222.0%22%2C%22con%22%3A%7B%22GDPR%22%3A%22%22%7D%7D; _shopify_tw=; _shopify_m=persistent; nostojs=autoload; ssUserId=86f1e748-a4c4-478d-b50e-6d0042101954; _ga=GA1.2.18110235.1641838003; _gid=GA1.2.578048620.1641838003; 2c.cId=61dc75b541c734708ce3abcc; 2c.dc=%7B%2261d485b96c7afe4679ef8e01%22%3A%7B%22state%22%3A%22closed%22%7D%7D; swym-pid="KQGYIAa9bGzWmLTc64ytmzgH/CDmzzy78iGCwcQdY3Q="; swym-swymRegid="P4JhOJeW9s1XsMBeeeNbuVeJyy9u7KAG1SfdBGuCP-lvgbfAl-Mun2Gz61BGQlcFTZgD2n4FlI01c9vddfkxSxIiL5jltpk4BDwocZUSl1Q6TrTMY2kloslF2KqU5a3KtDhVFZEf19MW7quAjbTkla6wSN5YZ5hKXpIlfjJtfm8"; swym-email=null; swym-cu_ct=undefined; _isuid=V3-5E010DA3-0901-4A5B-87D9-91676768B30F; swym-instrumentMap={}; _s=b1d2328a-dbd9-4239-8bb5-4ccfaaefd9ea; _shopify_s=b1d2328a-dbd9-4239-8bb5-4ccfaaefd9ea; _shopify_tm=; _shopify_sa_p=; shopify_pay_redirect=pending; swym-session-id="yw3jyt47s5ck8q3cwb66hg34lxk5hx0f7lkpngwd6d8fs9kw3dhr470ep44yc738"; ssViewedProducts=16044%2C20230%2CKSSBRIAL-DAWMOO-ASHLEG%2C9976002-020300ZZ%2CECSFEMBA-sadbro%2CECCHCARD-motwhi-ba%2C51490%2CEC-172TR-2%2FF2%2CSN1-102SFA-BK; ssSessionIdNamespace=fc9b032c-ac5a-4a9b-afee-20810fccfd53; OptanonConsent=isGpcEnabled=0&datestamp=Tue+Jan+11+2022+03%3A17%3A06+GMT%2B0700+(Western+Indonesia+Time)&version=6.26.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false; _shopify_sa_t=2022-01-10T20%3A17%3A06.147Z; swym-o_s=true',
        'pragma':'no-cache',
        #'referer':'https://www.2modern.com/collections/living-room-furniture',
        'sec-ch-ua':'"Chromium";v="96", "Opera GX";v="82", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'same-origin',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50',
    }
    HEADERS_JSON = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        #'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        'cache-control':'max-age=0',
        'sec-ch-ua':'"Chromium";v="96", "Opera GX";v="82", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'none',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50',
    }
    def parse(self, response):
        categories = response.xpath("//*[@data-handle='furniture']//*[@class='mega-menu__title']/a/@href").getall()
        for category in categories:
            if('collections' in category):
                yield scrapy.Request(url = 'https://www.2modern.com'+category,callback=self.parse_cat,headers=self.HEADERS)
                # break #testing

    def parse_cat(self, response):
        baseUrl = response.url
        print(baseUrl)
        getId = response.xpath("//*[@class='id']/text()").get()
        urlCreate = 'https://dja4ih.a.searchspring.io/api/search/search.json?ajaxCatalog=v3&resultsFormat=native&siteId=dja4ih&domain='+str(baseUrl)+'&bgfilter.collection_id='+str(getId)+'&q=&userId=V3-5E010DA3-0901-4A5B-87D9-91676768B30F&page=1'
        yield scrapy.Request(url=urlCreate,callback=self.parse_products,headers=self.HEADERS_JSON)

    def parse_products(self,response):
        baseUrl = response.url
        products = json.loads(response.text)['results']
        for product in products:
            prodName = product['name']
            prodUrl = product['url'].replace("//","https://")
            variants = json.loads(product['variants'].replace("&quot;",'"'))
            for variant in variants:
                extraName = variant['title']
                finalName = prodName
                variantid = variant['id']

                temp_dict = {
                    'SKU':variant['sku'],
                    'URL':prodUrl,
                    'Product Name':finalName,
                    'Variant':extraName,
                    'Rating':'',
                    '# of reviews': '',
                    'Price': variant['price'],
                    'Sale Price': '',
                }

                yield scrapy.Request(url=prodUrl+"?variant="+str(variantid),callback=self.parse_products_details,headers=self.HEADERS,meta={'temp':temp_dict})
            #     break #testing
            # break #testing

            if(len(products)==96):
                pageNow = re.findall(r"page=(\d+)",baseUrl)[0]
                pageNext = int(pageNow)+1
                urlNext = baseUrl.replace("page="+str(pageNow),"page="+str(pageNext))
                yield scrapy.Request(url=urlNext,callback=self.parse_products,headers=self.HEADERS_JSON)

    def parse_products_details(self,response):
        baseUrl = response.url
        tempDict = response.meta['temp']
        breadcrumb = response.xpath("//*[@class='breadcrumbs']//li/a/text()").getall()
        dimension = response.xpath("//*[@class='details-content' and contains(.,'Packaged Dimensions:')]//text()").getall()

        if(dimension == []):
            dimension = response.xpath("//*[@class='details-content' and contains(.,'Overall Dimensions:')]//text()").getall()

        dimension_text = ''
        for dimen in dimension:
            if('Packaged Dimensions:' in dimen or 'Overall Dimensions:' in dimen):
                dimension_text = dimen.strip().replace("Packaged Dimensions: ","").replace("Overall Dimensions: ","")
        imagelist = response.xpath("//*[@class='pdp-product__thumbnail-link']/img/@src").getall()
        images=[]
        for img in imagelist:
            images.append('https:'+img.replace("20x.jpg","1024x1024.jpg"))
        
        price1 = response.xpath("//*[@data-product-price]/text()").get()
        price2 = response.xpath("//*[@data-compare-price]/text()").get()
        priceSale = ''
        if(price2 is None or price2 == ''):
            price = price1
            price2 = ''
        else:
            price = price2
            priceSale = price1

        swatches = []
        i = 1
        for swatch in response.xpath('//div[@class="pdp-option-selectors pdp-option-with-image"]').xpath('.//label[contains(@for, "Option")]'):
            try:
                swatch_image = swatch.xpath('.//@data-src').get()
                swatch_name = swatch.xpath('.//span/text()').get()
                if not swatch_image:
                    continue
                swatches.append({'index': i,
                                'images': swatch_image,
                                'name': swatch_name})
                i += 1
            except:
                pass


        p = {
            'SKU': tempDict['SKU'],
            'URL': baseUrl,
            'Main Category': breadcrumb[0].strip() if len(breadcrumb) > 0 else '',
            'Sub Category 1': breadcrumb[1].strip() if len(breadcrumb) > 1 else '',
            'Sub Category 2': breadcrumb[2].strip() if len(breadcrumb) > 2 else '',
            'Sub Category 3': breadcrumb[3].strip() if len(breadcrumb) > 3 else '',
            'Product Name': tempDict['Product Name'],
            'Variant': tempDict['Variant'],
            'Rating': '',
            '# of reviews': '',
            'Price': price,
            'Sale Price': priceSale,
            'Details': response.xpath("//*[@class='details-content']/p/text()").get(),
            'Dimension': dimension_text,
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
            p['Price'] = p['Price'].strip().replace("\n","").replace(" ","")
        except:
            pass
        try:
            p['Sale Price'] = p['Sale Price'].strip().replace("\n","").replace(" ","")
        except:
            pass
        try:
            if(p['SKU'] not in self.history and p['Main Category'] == "Furniture"):
                self.history.append(p['SKU'])
                yield(p)
        except:
            pass