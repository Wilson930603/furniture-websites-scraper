import scrapy
import json
from bs4 import BeautifulSoup
import re
import simplejson
import requests

class ikeaspider(scrapy.Spider):
    name = 'ikea'
    allowed_domains = []
    start_urls = ['https://www.ikea.com/us/en/header-footer/menu-products.html']
    completeSku = []
    history = []

    # custom_settings ={
    #     'DOWNLOADER_MIDDLEWARES':{'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
    #     },
    # }

    HEADERS = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        #'cookie':'WSPFY=6d71627630500000b636dd611f0300005b040000; WSIDC=EAST; INTERNATIONAL=US-USD-1; bm_sz=B5011EEDB7A6912FCCE840EC8FCD41DC~YAAQbXFidpZ2lDF+AQAAD7odSA6G/4IqzFuNGWbR6EQRboZG6A7BpVEv2BUSDYQ58LvsXufdw6BBC8qsYiHJf/P2QGpc8ihNqwqvHZyT80XVhCJ+946C3nl+1iZpgSM1sO4kSLMyhmaNklojpTjTYSyLL3c0NaeNiXDNY2/ybbe65GIm2b558zMwayOSSTbUB5bwZUlIJmvagmXszYYtUVayoX+9Mv6uAM2BpNQ2HmwkKhljV+tppzJIBCtQPlTPsuoG9xMbf9ZqUksrut2z1xnC8OVlSqTpDLrR1xSUJv1GQIIuSkZl7Q==~3747895~3290694; check=true; TnTNew=true; AMCVS_D38758195432E1050A4C98A2%40AdobeOrg=1; _abck=BD787B9E7744A7B8393072043F6ED724~0~YAAQbXFidsN2lDF+AQAAOhEeSAdKmGODs/qsxloGOa4U4mnsTyCbR+S4AvuptulWqAcfQl4wF7PK0+eAc3kE6EG2a8xQOx2QT+rgtm/8SL9h5WZlvtond6mB591wHnZLB+I7PMPjgFSinrdZ6NZXY/ol+pUKo2uHX3EookYtE91XBaPX6WlJqKdgSdmp1rgKSvcOqiBUWV6RdgHZRMdViTSa1f6yObesRjUhjgsUKasyLDgqb8qRkYEsqiHOoHh1Mk2C3elqnR1bQTWDQC1G9La6r6lz9o2qf057Kk6pFaaXiTyg6sqA4S6bGiZik3al6z6AiaKHuN6PAh7jBbzCr+ylWp9toi62Ef41IqSZZLL77cEsuHN7ryueOFqjuBuaMkig8t7Vir5uCpgsh1g+RCouQoqRFS9fj0g=~-1~||-1||~-1; PB_PSID=ashburn.ow_CYxieykZJuGfvJ7aqLqZ8eUgfcrAmOEakFNiBQ8vV8kWYmtA-Ttg7VqVvCtR_jcbBXgLzSRbl1g0DImtwk56OQhPP5LhLQjj2yiZRJSXcClm1EvAepIFDgAqdcpo4j3Y2710%3D202201110750; svi_dec=90521412709910939267827820397336505532; s_cc=true; doubleclick_24h=true; jvxsync=sUc0pOzZOkcz; ad_sess_pb_email=true; CreState=Z42UJ7RMkdB0i08sYAjf2sY8FYt4RzSpCKDXAh9s9qk%3D.999.v1; filtersVisible=false; WSAB=420fc50b-613b-4669-8497-5f475a9f242a; PBRN=3wNPyEUA85i_51f-HPcKTO1PQAm8BdyBkMmjND_lCcvTdFSTbrv4GMw; akid=3wNPyEUA85i_51f-HPcKTO1PQAm8BdyBkMmjND_lCcvTdFSTbrv4GMw; wsiakid=1ZRDMSLU+CpCFgNp2mbXQMldap5Al2lmve/cFhQbrYu7eLFJTbEeNcu2JPm/sXS9njMoyS4NwGX/xj0twC0g6rJCyiLpT2aC86/tq5FklBc=; TT3bl=false; TURNTO_VISITOR_SESSION=1; searchFiltersVisible=false; TURNTO_TEASER_SHOWN=1641887987524; TURNTO_TEASER_COOKIE=a,1641888051646; WSGEO=ID|JK||-6.13|106.88; s_sq=%5B%5BB%5D%5D; rr_rcs=eF4FwbENgDAMBMCGil0e2f7EcTZgDYJBoqAD5udumu_vuXIxC6gXja7VydpRCOj07mtGcigNBzeiCAXe24BbPbtJk_D8AV8TEMs; utag_main=v_id:017e481e394e000603d5defa8a4605084001c07c00868$_sn:2$_ss:0$_st:1641893364911$vapi_domain:potterybarn.com$_prevpage:shop%3Afurniture%3Achairs-ottomans%3Bexp-1641895164432$_pn:2%3Bexp-session$ses_id:1641891453332%3Bexp-session$prev_page_primary_category:category%3Bexp-session; s_lv=1641891565007; s_nr44=1641891565010-Repeat; productnum=22; AMCV_D38758195432E1050A4C98A2%40AdobeOrg=1075005958%7CMCIDTS%7C19004%7CMCMID%7C90521412709910939267827820397336505532%7CMCAID%7CNONE%7CMCOPTOUT-1641898765s%7CNONE%7CvVersion%7C4.4.1; BIGipServerPool-PB-49446=!HsRm1o54l0JBMHvf3yH5clkbmr6XcL0HfU3cKVGqsLreNBhF2YcfvS4g6EgnaIksktwwXXBMPMf1FA==; s_tp=21087; s_ppv=shop%253Afurniture%253Achairs-ottomans%2C7%2C7%2C1540',
        #'referer':'https://www.potterybarn.com/pages/furniture/sofa-sectional-collections/',
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
    HEADERS_JSON = {
        'accept':'*/*',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        #'cookie':'WSPFY=6d71627630500000b636dd611f0300005b040000; WSIDC=EAST; INTERNATIONAL=US-USD-1; bm_sz=B5011EEDB7A6912FCCE840EC8FCD41DC~YAAQbXFidpZ2lDF+AQAAD7odSA6G/4IqzFuNGWbR6EQRboZG6A7BpVEv2BUSDYQ58LvsXufdw6BBC8qsYiHJf/P2QGpc8ihNqwqvHZyT80XVhCJ+946C3nl+1iZpgSM1sO4kSLMyhmaNklojpTjTYSyLL3c0NaeNiXDNY2/ybbe65GIm2b558zMwayOSSTbUB5bwZUlIJmvagmXszYYtUVayoX+9Mv6uAM2BpNQ2HmwkKhljV+tppzJIBCtQPlTPsuoG9xMbf9ZqUksrut2z1xnC8OVlSqTpDLrR1xSUJv1GQIIuSkZl7Q==~3747895~3290694; check=true; TnTNew=true; AMCVS_D38758195432E1050A4C98A2%40AdobeOrg=1; _abck=BD787B9E7744A7B8393072043F6ED724~0~YAAQbXFidsN2lDF+AQAAOhEeSAdKmGODs/qsxloGOa4U4mnsTyCbR+S4AvuptulWqAcfQl4wF7PK0+eAc3kE6EG2a8xQOx2QT+rgtm/8SL9h5WZlvtond6mB591wHnZLB+I7PMPjgFSinrdZ6NZXY/ol+pUKo2uHX3EookYtE91XBaPX6WlJqKdgSdmp1rgKSvcOqiBUWV6RdgHZRMdViTSa1f6yObesRjUhjgsUKasyLDgqb8qRkYEsqiHOoHh1Mk2C3elqnR1bQTWDQC1G9La6r6lz9o2qf057Kk6pFaaXiTyg6sqA4S6bGiZik3al6z6AiaKHuN6PAh7jBbzCr+ylWp9toi62Ef41IqSZZLL77cEsuHN7ryueOFqjuBuaMkig8t7Vir5uCpgsh1g+RCouQoqRFS9fj0g=~-1~||-1||~-1; PB_PSID=ashburn.ow_CYxieykZJuGfvJ7aqLqZ8eUgfcrAmOEakFNiBQ8vV8kWYmtA-Ttg7VqVvCtR_jcbBXgLzSRbl1g0DImtwk56OQhPP5LhLQjj2yiZRJSXcClm1EvAepIFDgAqdcpo4j3Y2710%3D202201110750; svi_dec=90521412709910939267827820397336505532; s_cc=true; doubleclick_24h=true; jvxsync=sUc0pOzZOkcz; ad_sess_pb_email=true; CreState=Z42UJ7RMkdB0i08sYAjf2sY8FYt4RzSpCKDXAh9s9qk%3D.999.v1; filtersVisible=false; WSAB=420fc50b-613b-4669-8497-5f475a9f242a; PBRN=3wNPyEUA85i_51f-HPcKTO1PQAm8BdyBkMmjND_lCcvTdFSTbrv4GMw; akid=3wNPyEUA85i_51f-HPcKTO1PQAm8BdyBkMmjND_lCcvTdFSTbrv4GMw; wsiakid=1ZRDMSLU+CpCFgNp2mbXQMldap5Al2lmve/cFhQbrYu7eLFJTbEeNcu2JPm/sXS9njMoyS4NwGX/xj0twC0g6rJCyiLpT2aC86/tq5FklBc=; TT3bl=false; TURNTO_VISITOR_SESSION=1; searchFiltersVisible=false; TURNTO_TEASER_SHOWN=1641887987524; TURNTO_TEASER_COOKIE=a,1641888051646; WSGEO=ID|JK||-6.13|106.88; s_sq=%5B%5BB%5D%5D; rr_rcs=eF4FwbENgDAMBMCGil0e2f7EcTZgDYJBoqAD5udumu_vuXIxC6gXja7VydpRCOj07mtGcigNBzeiCAXe24BbPbtJk_D8AV8TEMs; utag_main=v_id:017e481e394e000603d5defa8a4605084001c07c00868$_sn:2$_ss:0$_st:1641893364911$vapi_domain:potterybarn.com$_prevpage:shop%3Afurniture%3Achairs-ottomans%3Bexp-1641895164432$_pn:2%3Bexp-session$ses_id:1641891453332%3Bexp-session$prev_page_primary_category:category%3Bexp-session; s_lv=1641891565007; s_nr44=1641891565010-Repeat; productnum=22; AMCV_D38758195432E1050A4C98A2%40AdobeOrg=1075005958%7CMCIDTS%7C19004%7CMCMID%7C90521412709910939267827820397336505532%7CMCAID%7CNONE%7CMCOPTOUT-1641898765s%7CNONE%7CvVersion%7C4.4.1; BIGipServerPool-PB-49446=!HsRm1o54l0JBMHvf3yH5clkbmr6XcL0HfU3cKVGqsLreNBhF2YcfvS4g6EgnaIksktwwXXBMPMf1FA==; s_tp=21087; s_ppv=shop%253Afurniture%253Achairs-ottomans%2C7%2C7%2C1540',
        'origin':'https://www.ikea.com/',
        'referer':'https://www.ikea.com/',
        'sec-ch-ua':'"Chromium";v="96", "Opera GX";v="82", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'sec-fetch-dest':'empty',
        'sec-fetch-mode':'cors',
        'sec-fetch-site':'cross-site',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 OPR/82.0.4227.50',
    }
    HEADERS_INSIDE = {
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.9',
        #'cookie':'WSPFY=6d71627630500000b636dd611f0300005b040000; WSIDC=EAST; INTERNATIONAL=US-USD-1; bm_sz=B5011EEDB7A6912FCCE840EC8FCD41DC~YAAQbXFidpZ2lDF+AQAAD7odSA6G/4IqzFuNGWbR6EQRboZG6A7BpVEv2BUSDYQ58LvsXufdw6BBC8qsYiHJf/P2QGpc8ihNqwqvHZyT80XVhCJ+946C3nl+1iZpgSM1sO4kSLMyhmaNklojpTjTYSyLL3c0NaeNiXDNY2/ybbe65GIm2b558zMwayOSSTbUB5bwZUlIJmvagmXszYYtUVayoX+9Mv6uAM2BpNQ2HmwkKhljV+tppzJIBCtQPlTPsuoG9xMbf9ZqUksrut2z1xnC8OVlSqTpDLrR1xSUJv1GQIIuSkZl7Q==~3747895~3290694; check=true; TnTNew=true; AMCVS_D38758195432E1050A4C98A2%40AdobeOrg=1; _abck=BD787B9E7744A7B8393072043F6ED724~0~YAAQbXFidsN2lDF+AQAAOhEeSAdKmGODs/qsxloGOa4U4mnsTyCbR+S4AvuptulWqAcfQl4wF7PK0+eAc3kE6EG2a8xQOx2QT+rgtm/8SL9h5WZlvtond6mB591wHnZLB+I7PMPjgFSinrdZ6NZXY/ol+pUKo2uHX3EookYtE91XBaPX6WlJqKdgSdmp1rgKSvcOqiBUWV6RdgHZRMdViTSa1f6yObesRjUhjgsUKasyLDgqb8qRkYEsqiHOoHh1Mk2C3elqnR1bQTWDQC1G9La6r6lz9o2qf057Kk6pFaaXiTyg6sqA4S6bGiZik3al6z6AiaKHuN6PAh7jBbzCr+ylWp9toi62Ef41IqSZZLL77cEsuHN7ryueOFqjuBuaMkig8t7Vir5uCpgsh1g+RCouQoqRFS9fj0g=~-1~||-1||~-1; PB_PSID=ashburn.ow_CYxieykZJuGfvJ7aqLqZ8eUgfcrAmOEakFNiBQ8vV8kWYmtA-Ttg7VqVvCtR_jcbBXgLzSRbl1g0DImtwk56OQhPP5LhLQjj2yiZRJSXcClm1EvAepIFDgAqdcpo4j3Y2710%3D202201110750; svi_dec=90521412709910939267827820397336505532; s_cc=true; doubleclick_24h=true; jvxsync=sUc0pOzZOkcz; ad_sess_pb_email=true; CreState=Z42UJ7RMkdB0i08sYAjf2sY8FYt4RzSpCKDXAh9s9qk%3D.999.v1; filtersVisible=false; WSAB=420fc50b-613b-4669-8497-5f475a9f242a; PBRN=3wNPyEUA85i_51f-HPcKTO1PQAm8BdyBkMmjND_lCcvTdFSTbrv4GMw; akid=3wNPyEUA85i_51f-HPcKTO1PQAm8BdyBkMmjND_lCcvTdFSTbrv4GMw; wsiakid=1ZRDMSLU+CpCFgNp2mbXQMldap5Al2lmve/cFhQbrYu7eLFJTbEeNcu2JPm/sXS9njMoyS4NwGX/xj0twC0g6rJCyiLpT2aC86/tq5FklBc=; TT3bl=false; TURNTO_VISITOR_SESSION=1; searchFiltersVisible=false; TURNTO_TEASER_SHOWN=1641887987524; TURNTO_TEASER_COOKIE=a,1641888051646; WSGEO=ID|JK||-6.13|106.88; s_sq=%5B%5BB%5D%5D; rr_rcs=eF4FwbENgDAMBMCGil0e2f7EcTZgDYJBoqAD5udumu_vuXIxC6gXja7VydpRCOj07mtGcigNBzeiCAXe24BbPbtJk_D8AV8TEMs; utag_main=v_id:017e481e394e000603d5defa8a4605084001c07c00868$_sn:2$_ss:0$_st:1641893364911$vapi_domain:potterybarn.com$_prevpage:shop%3Afurniture%3Achairs-ottomans%3Bexp-1641895164432$_pn:2%3Bexp-session$ses_id:1641891453332%3Bexp-session$prev_page_primary_category:category%3Bexp-session; s_lv=1641891565007; s_nr44=1641891565010-Repeat; productnum=22; AMCV_D38758195432E1050A4C98A2%40AdobeOrg=1075005958%7CMCIDTS%7C19004%7CMCMID%7C90521412709910939267827820397336505532%7CMCAID%7CNONE%7CMCOPTOUT-1641898765s%7CNONE%7CvVersion%7C4.4.1; BIGipServerPool-PB-49446=!HsRm1o54l0JBMHvf3yH5clkbmr6XcL0HfU3cKVGqsLreNBhF2YcfvS4g6EgnaIksktwwXXBMPMf1FA==; s_tp=21087; s_ppv=shop%253Afurniture%253Achairs-ottomans%2C7%2C7%2C1540',
        #'referer':'https://www.potterybarn.com/pages/furniture/sofa-sectional-collections/',
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

    def parse(self, response):
        categories = response.xpath("//*[@data-tracking-label='products | fu001']/li/a")
        for category in categories:
            catName = category.xpath("./text()").get()
            catCode = category.xpath("./@data-tracking-label").get()
            if(catCode!='all'):
                urlCreate = 'https://sik.search.blue.cdtapps.com/us/en/product-list-page/more-products?category='+str(catCode)+'&start=0&end=24&c=lf&v=20211124&sort=RELEVANCE&sessionId=03a4f2be-edb8-4c19-bd60-679e34272d15'
                yield scrapy.Request(url=urlCreate,callback=self.parse_products, headers=self.HEADERS_JSON,meta={'catName':catName})
                #break #testing

    def parse_products(self,response):
        baseUrl = response.url
        catName = response.meta['catName']
        rawJson = json.loads(response.text)
        products = rawJson['moreProducts']['productWindow']
        for product in products:
            pipUrl = product['pipUrl']
            yield scrapy.Request(url=pipUrl,callback=self.parse_products_details, headers=self.HEADERS_INSIDE,meta={'catName':catName})
            #break #testing
            variants = product['gprDescription']['variants']
            for variant in variants:
                pipUrl = variant['pipUrl']
                yield scrapy.Request(url=pipUrl,callback=self.parse_products_details, headers=self.HEADERS_INSIDE,meta={'catName':catName})

        if(len(products)==24):
            pageNow = re.findall(r"start=(\d+)",baseUrl)[0]
            pageNext = int(pageNow)+24
            pageNext2 = pageNext+24
            urlNext = baseUrl.replace("start="+str(pageNow),"start="+str(pageNext)).replace("end="+str(pageNext),"end="+str(pageNext2))
            yield scrapy.Request(url=urlNext,callback=self.parse_products,headers=self.HEADERS_JSON,meta={'catName':catName})

    def parse_products_details(self,response):
        baseUrl = response.url
        catName = response.meta['catName'] #testing
        #### basic construct ####
        sku = ''
        images =[]
        rating1 = ''
        rating2 = ''
        #########################
        detailJson = json.loads(response.xpath("//*[@id='pip-range-json-ld']/text()").get())
        sku = detailJson['sku']
        images = detailJson['image']
        try:
            rating1=detailJson['aggregateRating']['ratingValue']
            rating2=detailJson['aggregateRating']['reviewCount']
        except:
            pass
        price = ''
        priceSale = ''
        try:
            priceSale = detailJson['offers']['lowPrice']
            price = detailJson['offers']['highPrice']
        except:
            try:
                price = detailJson['offers']['price']
            except:
                pass
        breadcrumb = []
        try:
            breadcrumb = response.xpath("//*[@class='bc-breadcrumb__list-item']/a//text()").getall()
            breadcrumb = breadcrumb[1:-1]
        except:
            breadcrumb = []
        dimension_text = ''
        try:
            dimension_text = self.parse_html(''.join(response.xpath("//*[@class='range-revamp-product-dimensions__title']/following-sibling::div/*").getall()))
        except Exception as e:
            pass
        detail_text = ''
        try:
            detail_text = self.parse_html(''.join(response.xpath("//*[@class='range-revamp-product-details__title']/following-sibling::div/*").getall()))
        except Exception as e:
            pass

        swatches = []
        index = 0
        try:
            for swatch in response.xpath('//div[@class="range-revamp-product-styles__items"]/a/div/span/img'):
                swatch_index = index
                swatch_name = swatch.xpath('.//@alt').get()
                swatch_image = swatch.xpath('.//@src').get()
                swatches.append({'index': swatch_index,
                                'images': swatch_image,
                                'name': swatch_name})
                index += 1
        except:
            pass

        p = {
            #'catName':catName,
            'SKU': sku,
            'URL': baseUrl,
            'Main Category': breadcrumb[0].strip() if len(breadcrumb) > 0 else '',
            'Sub Category 1': breadcrumb[1].strip() if len(breadcrumb) > 1 else '',
            'Sub Category 2': breadcrumb[2].strip() if len(breadcrumb) > 2 else '',
            'Sub Category 3': breadcrumb[3].strip() if len(breadcrumb) > 3 else '',
            'Product Name': response.xpath("//h1[@class='range-revamp-header-section']/*[contains(@class,'header-section__title')]/text()").get(),
            'Variant':', '.join(response.xpath("//h1[@class='range-revamp-header-section']/*[contains(@class,'header-section__description')]//text()").getall()),
            'Rating': rating1,
            '# of reviews': rating2,
            'Price': price,
            'Sale Price': priceSale,
            'Details': detail_text,
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
            if(p['Details'][0]=='\n'):
                p['Details'] = p['Details'][1:]
        except:
            pass
        try:
            if(p['Dimension'][0]=='\n'):
                p['Dimension'] = p['Dimension'][1:]
        except:
            pass
        #print(p)
        #yield(p)
        if(p['SKU'] not in self.history):
            self.history.append(p['SKU'])
            yield(p)
    def parse_html(self, html):
        elem = BeautifulSoup(html, features="html.parser")
        text = ''
        for e in elem.descendants:
            if isinstance(e, str):
                text += e
            elif e.name in ['br',  'p', 'h1', 'h2', 'h3', 'h4','tr', 'th']:
                text += '\n'
            elif e.name == 'td':
                text += ' - '
            elif e.name == 'li':
                text += ' '
            elif e.name == 'div':
                text += '\n'
        return text
