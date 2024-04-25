import scrapy
import json
from bs4 import BeautifulSoup
import re

class cb2spider(scrapy.Spider):
    name = 'cb2'
    allowed_domains = ['cb2.com']
    start_urls = ['https://cb2.com/']

    HEADERS = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-GB,en-US;q=0.9,en;q=0.8',
        #'cookie':'Internationalization=US|USD; OriginCountry=US; tid=ZuRMlV923MtYfMEhZ6Q7By71oXIJuVSpHlO6RbaExoL47h6BoGh6OjGOIXRmcWVacB4c_Nz6BT0vS8o4CG880M6L5BQV1xuDfN8T9iomX313RVOsJgU1dFiNnr6d5rPjJoB-YA2; id=zsvl2qulzxt42iifgzww1jfw; zip=60540; zipRemember=60540; uid=yyTWxeMyOEe2jz9FCUiytg; CBH_CB2US=EKA0j9cbm0-R5W9YWQQBaQ; AKA_A2=A; optimizelyEndUserId=oeu1638914945224r0.40420328638427017; mobileForOptIn=1; rl_anonymous_id=RudderEncrypt%3AU2FsdGVkX19vkTsawlxnYh7IRGr5iDda50LHScRQzUj%2BidmvRfnDyvhTP6%2B%2BH3dfea0tMntfX%2BJ2bWJXxPiIsA%3D%3D; rl_group_id=RudderEncrypt%3AU2FsdGVkX1%2ByW3XxWUY%2FXcnruPe7YzcRecJS0dRv3qE%3D; rl_group_trait=RudderEncrypt%3AU2FsdGVkX1%2BYNbMOMp6gvhF2dcp0MZCAeAqLnx8Ph6U%3D; rl_page_init_referrer=RudderEncrypt%3AU2FsdGVkX1%2FJL9wGVxPvbmXtqxaPnhri5wx%2Fkmup7eg%3D; rl_page_init_referring_domain=RudderEncrypt%3AU2FsdGVkX19v8yL8xJVjazB8nK%2BOZqGWO6l6SecB8lg%3D; rl_user_id=RudderEncrypt%3AU2FsdGVkX19vzqXlXci5me4GYAO2oiT8WiIn8ACyOsM%3D; rl_trait=RudderEncrypt%3AU2FsdGVkX1%2BeCri9MXF%2BOsDxqbJAaWV5dAu2XMnFP0S2c5YFiCZLu2qAMK4AE3sHCFfhosgtvO0eJGhkphGBv8Tec7ieePXQ%2FVhEzBvTHg%2BEN92XXV8D6cuhngPt4rZPlBphizIWkZl91g%2FgtUaUdZf%2FCKFCdIw6SFAdj8Xv%2FzsZQfB%2BQAnpX%2BcnrCvAiyddJqpdkEbgJyZ54ET%2BFMANgPlhH5D7tYUmSlidYEz6bRyZaLS1LW7Bm19suY4%2Bq6AYFGoWSHTu1vYxXS63gFbKUg%3D%3D; AMCVS_B9F81C8B5330A6F40A490D4D%40AdobeOrg=1; AMCV_B9F81C8B5330A6F40A490D4D%40AdobeOrg=-1124106680%7CMCIDTS%7C18969%7CMCMID%7C43953881869487543311350163513562037683%7CMCAAMLH-1639519757%7C3%7CMCAAMB-1639519757%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1638922157s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.2.0; gpv=spill%7Cnew%3Aview%20all%7Cview%20all%20new; s_cc=true; _ga_M3YLWN86TG=GS1.1.1638914957.1.0.1638914957.0; _ga=GA1.2.257141860.1638914960; _gid=GA1.2.1109742649.1638914961; _gat_gtag_UA_29752689_2=1; reese84=3:AePUJsBye/U7mlqpCmyzEw==:Jl5rhwHm7eExusledlpNxPMHoGhAdUhB2X4kJVR0DyQ3tYho/mzG1zQMhkvQruQgK3pTIe8VbPy+EJmTX2eOa89AxK0a7D/P1JrUOKsnaf2+wcoxSh59nGCAKagXiWsvZcQQ6JyN1OPlitWlPh3WmaJRhgDuVRk7wCcUnjtzBOqq/bOlCW3AEFocmtyZHt3WNXVokkRSpy8dKd9iBv8JN+h68zVdZlXfQP052FYXBVNzgo1215I5m6dWcFj1jsHAnnYFHXM0LH6y8jtVOMFjsdhGHbFM1cmn6Wx8Z3Bumk5rD6vWeFESAXJijJ5LgwPZzcfItPVBHYni1RBaslNOGEpuF+TdxlXptPKNqhtx7P+0sR6RQZRbF9gFWwBkerpUYaSdaykevnTDbGGG+Z58kQB2S+xj8NDIXQ3oWEA6QlM=:VUn6BjBks8rknsKhdw+pKnYUFUSOwimwTXO1LQs+7XI=; _uetsid=56a1e78057aa11ecadb41d9e8ad527b5; _uetvid=56a287b057aa11eca4db099a90dfc65c; _rdt_uuid=1638914965553.ea3d6177-ccf7-4ea6-8df0-10abd00e8d3d; __pdst=27ae08f8d6e442c7aa17e652583655b8; _gcl_au=1.1.601838983.1638914966; s_nr365=1638914966357-New; s_sq=candbcb2com%3D%2526c.%2526a.%2526activitymap.%2526page%253Dspill%25257Cnew%25253Aview%252520all%25257Cview%252520all%252520new%2526link%253DHOLIDAY%2526region%253Dnav-list_New%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dspill%25257Cnew%25253Aview%252520all%25257Cview%252520all%252520new%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Fwww.cb2.com%25252Fnew%25252Fnew-holiday%25252F1%2526ot%253DA; RT="z=1&dm=cb2.com&si=34946bdf-144c-43f0-9053-01a81dc0432a&ss=kwwnmskn&sl=1&tt=p95&bcn=%2F%2F684d0d4a.akstat.io%2F&ld=paq&nu=34fhann9&cl=suz&ul=swb"',
        'dnt':'1',
        'referer':'https://www.cb2.com/',
        'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'same-origin',
        'sec-fetch-user':'?1',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36',
    }

    def parse(self, response):
        categories = ['https://www.cb2.com/']
        for category in categories:
            yield scrapy.Request(category, headers=self.HEADERS, callback=self.parse_nav, dont_filter=True)

    def parse_nav(self, response):
        sub_categories = response.xpath('//div[@id="main-menu"]//*[contains(@id,"View-All")]/@href').getall()
        for sub_category in sub_categories:
            products_link = 'https://www.cb2.com'+sub_category
            yield scrapy.Request(products_link, headers=self.HEADERS, callback=self.parse_json, dont_filter=False)

    def parse_json(self, response):
        rawJson = response.xpath("//script[contains(.,'pageInfo')]/text()").get()
        reJson = re.findall(r"assign\(\{\}, (.+?)\)\;",rawJson)
        json_data = json.loads(reJson[0])['product']

        for product in json_data:
            product_link = 'https://www.cb2.com'+product['productInfo']['productURL']
            yield scrapy.Request(product_link, headers=self.HEADERS, callback=self.parse_product, dont_filter=False)

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

    def clean_imageurl(self, link):
        imageurl = re.findall(r"([^>]*)\/\$web_pdp",link)
        if(imageurl==[]):
            return link
        else:
            return imageurl[0]

    def parse_product(self, response):
        swatches = []
        index = 0

        target_script = ''
        for item in response.xpath('//script').getall():
            if 'currentPrice' in str(item) and 'console.log("[.NET]"' in str(item):
                target_script = item
                break
        try:
            target = json.loads(target_script.split('colorBar":')[-1].split(',"choiceImageMacro"')[0].split('{"colorBarChoices":')[-1])
            for swatch in target:
                swatch_index = index
                swatches.append({'index': swatch_index,
                                'images': swatch['imagePath'],
                                'name': swatch['choiceName']})
                index += 1
        except:
            pass
            
        try:
            checkVariants = response.xpath("//*[@class='attribute-text']/@href").getall()
        except:
            checkVariants = []

        if(len(checkVariants)>0):
            for checkVariant in checkVariants:
                variant_link = 'https://cb2.com'+checkVariant
                yield scrapy.Request(variant_link, headers=self.HEADERS, callback=self.parse_product_variants, meta={'swatches': swatches}, dont_filter=False)
        else:
            rawJson2 = response.xpath("//script[contains(.,'pageInfo')]/text()").get()
            reJson2 = re.findall(r"assign\(\{\}, (.+?)\)\;",rawJson2)
            json_data2 = json.loads(reJson2[0])
            rawJson1 = response.xpath("//script[contains(.,'ImageGallery')]/text()").get()
            json_data1 = json.loads(rawJson1)
            rawJson3 = response.xpath("//script[contains(.,'SingleProductPageContainer')]/text()").get()
            reJson3 = re.findall(r"PageContainer, (.+?)\), document\.getElementBy",rawJson3)
            json_data3 = json.loads(reJson3[0])

            price = json_data2['product'][0]['attributes']['price']['regularPrice']
            salePrice = json_data2['product'][0]['attributes']['price']['currentPrice']
            if(salePrice==price):
                salePrice = ''
            categoryLists = json_data2['product'][0]['attributes']['category']['categoryLevels']

            images = json_data1['associatedMedia']

            descText = ''
            details =response.xpath("//*[@class='details-content']/*").getall()
            descText = self.parse_html(''.join(details))
            
            dimText = ''
            try:
                dimensions = json_data3['model']['browseDto']['dimensionComponent'][0]['productDimensions'][0]
                dwidth = dimensions['width']
                ddepth = dimensions['depth']
                dheight = dimensions['height']
                ddiameter = dimensions['diameter']
                dweight = dimensions['weight']
                if(dwidth!=0):
                    dimText+='Width = ' + str(dwidth) + '; '
                if(ddepth!=0):
                    dimText+='Depth = ' + str(ddepth) + '; '
                if(dheight!=0):
                    dimText+='Height = ' + str(dheight) + '; '
                if(ddiameter!=0):
                    dimText+='Diameter = ' + str(ddiameter) + '; '
                if(dweight!=0):
                    dimText+='Weight = ' + str(dweight)
            except:
                dimensions = ''
                dimText = ''

            rating = json_data2['page']['attributes']['review']['averageReview']
            numRating = json_data2['page']['attributes']['review']['reviewCount']
            if(numRating==0):
                rating = 0

            p = {
                'SKU': json_data2['product'][0]['productInfo']['productId'],
                'URL': response.url,
                'Main Category': categoryLists[0] if len(categoryLists) > 0 else '',
                'Sub Category 1': categoryLists[1] if len(categoryLists) > 1 else '',
                'Sub Category 2': categoryLists[2] if len(categoryLists) > 2 else '',
                'Sub Category 3': categoryLists[3] if len(categoryLists) > 3 else '',
                'Product Name': json_data2['product'][0]['productInfo']['productName'],
                'Rating': rating,
                '# of reviews': numRating,
                'Price': price,
                'Sale Price': salePrice,
                'Details': descText,
                'Dimension': dimText,
                'Swatches': swatches,
                'Main Image': 'https://cb2.scene7.com/is/image/CB2/'+json_data2['product'][0]['productInfo']['productImage'],
                'Image 1': self.clean_imageurl(images[1]['contentUrl']) if len(images) > 1 else '',
                'Image 2': self.clean_imageurl(images[2]['contentUrl']) if len(images) > 2 else '',
                'Image 3': self.clean_imageurl(images[3]['contentUrl']) if len(images) > 3 else '',
                'Image 4': self.clean_imageurl(images[4]['contentUrl']) if len(images) > 4 else '',
                'Image 5': self.clean_imageurl(images[5]['contentUrl']) if len(images) > 5 else '',
                'Image 6': self.clean_imageurl(images[6]['contentUrl']) if len(images) > 6 else '',
                'Image 7': self.clean_imageurl(images[7]['contentUrl']) if len(images) > 7 else '',
                'Image 8': self.clean_imageurl(images[8]['contentUrl']) if len(images) > 8 else ''
            }

            yield(p)

    def parse_product_variants(self,response):
        rawJson2 = response.xpath("//script[contains(.,'pageInfo')]/text()").get()
        reJson2 = re.findall(r"assign\(\{\}, (.+?)\)\;",rawJson2)
        json_data2 = json.loads(reJson2[0])
        rawJson1 = response.xpath("//script[contains(.,'ImageGallery')]/text()").get()
        json_data1 = json.loads(rawJson1)
        rawJson3 = response.xpath("//script[contains(.,'SingleProductPageContainer')]/text()").get()
        reJson3 = re.findall(r"PageContainer, (.+?)\), document\.getElementBy",rawJson3)
        json_data3 = json.loads(reJson3[0])

        price = json_data2['product'][0]['attributes']['price']['regularPrice']
        salePrice = json_data2['product'][0]['attributes']['price']['currentPrice']
        if(salePrice==price):
            salePrice = ''
        categoryLists = json_data2['product'][0]['attributes']['category']['categoryLevels']

        images = json_data1['associatedMedia']

        descText = ''
        details =response.xpath("//*[@class='details-content']/*").getall()
        descText = self.parse_html(''.join(details))
        
        dimText = ''
        try:
            dimensions = json_data3['model']['browseDto']['dimensionComponent'][0]['productDimensions'][0]
            dwidth = dimensions['width']
            ddepth = dimensions['depth']
            dheight = dimensions['height']
            ddiameter = dimensions['diameter']
            dweight = dimensions['weight']
            if(dwidth!=0):
                dimText+='Width = ' + str(dwidth) + '; '
            if(ddepth!=0):
                dimText+='Depth = ' + str(ddepth) + '; '
            if(dheight!=0):
                dimText+='Height = ' + str(dheight) + '; '
            if(ddiameter!=0):
                dimText+='Diameter = ' + str(ddiameter) + '; '
            if(dweight!=0):
                dimText+='Weight = ' + str(dweight)
        except:
            dimensions = ''
            dimText = ''

        rating = json_data2['page']['attributes']['review']['averageReview']
        numRating = json_data2['page']['attributes']['review']['reviewCount']
        if(numRating==0):
            rating = 0
            
        p = {
            'SKU': json_data2['product'][0]['productInfo']['productId'],
            'URL': response.url,
            'Main Category': categoryLists[0] if len(categoryLists) > 0 else '',
            'Sub Category 1': categoryLists[1] if len(categoryLists) > 1 else '',
            'Sub Category 2': categoryLists[2] if len(categoryLists) > 2 else '',
            'Sub Category 3': categoryLists[3] if len(categoryLists) > 3 else '',
            'Product Name': json_data2['product'][0]['productInfo']['productName'],
            'Rating': rating,
            '# of reviews': numRating,
            'Price': price,
            'Sale Price': salePrice,
            'Details': descText,
            'Dimension': dimText,
            'Swatches': response.meta['swatches'],
            'Main Image': 'https://cb2.scene7.com/is/image/CB2/'+json_data2['product'][0]['productInfo']['productImage'],
            'Image 1': self.clean_imageurl(images[1]['contentUrl']) if len(images) > 1 else '',
            'Image 2': self.clean_imageurl(images[2]['contentUrl']) if len(images) > 2 else '',
            'Image 3': self.clean_imageurl(images[3]['contentUrl']) if len(images) > 3 else '',
            'Image 4': self.clean_imageurl(images[4]['contentUrl']) if len(images) > 4 else '',
            'Image 5': self.clean_imageurl(images[5]['contentUrl']) if len(images) > 5 else '',
            'Image 6': self.clean_imageurl(images[6]['contentUrl']) if len(images) > 6 else '',
            'Image 7': self.clean_imageurl(images[7]['contentUrl']) if len(images) > 7 else '',
            'Image 8': self.clean_imageurl(images[8]['contentUrl']) if len(images) > 8 else ''
        }

        yield(p)
