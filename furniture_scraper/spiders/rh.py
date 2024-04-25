import scrapy
import requests
import urllib.parse as urlparse
from json import dumps
from urllib.parse import (urlencode, unquote, urlparse, parse_qsl, ParseResult)
import re

class RhSpider(scrapy.Spider):
    name = 'rh'
    allowed_domains = ['rh.com']
    start_urls = ['https://rh.com/sitemap.jsp']

    HEADERS = {
        "authority": "rh.com",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"''',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '''"Windows"''',
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en;q=0.9"
    }

    def parse(self, response):
        API_URL = "https://rh.com/rh-experience-layer-v1/graphql"
        HEADERS = {
            "cookie": '''fusion_search=true; fusion_gcp=true; PF_EXP=DESKTOP; cleanedCookie=true; engagement=4;''',
            "authority": "rh.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua": '''" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"''',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '''"Windows"''',
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-language": "en-US,en;q=0.9"
        }

        categories = response.xpath('//div[@class="sitemap-category grid"]')[1:]
        skus = []
        for category in categories:
            categoryName = category.xpath('.//h2/a/text()').get()
            for subCategory in category.xpath('.//div[@class="grid__item one-quarter menu"]'):
                subCategoryName = subCategory.xpath('.//h3/a/text()').get()
                for subSubCategory in subCategory.xpath('.//ul[@class="sitemap__links"]/li/a'):
                    subSubCategoryName = subSubCategory.xpath('.//text()').get()

                    categoriesList = [categoryName, subCategoryName, subSubCategoryName]
                    start = 0
                    query = subSubCategoryName.lower()
                    while True:
                        new = False
                        querystring = {"query":"query InfiniteScroll($ntt: String!, $contentType: String, $n: String, $nrpp: Int, $ns: String, $no: Int, $country: String, $currencyCode: String, $userType: String) { infiniteScroll( ntt: $ntt contentType: $contentType n: $n nrpp: $nrpp ns: $ns no: $no country: $country currencyCode: $currencyCode userType: $userType ) { stocked resultList { lastRecNum firstRecNum recsPerPage totalNumRecs records { recordType product { altImageUrl imageUrl displayName repositoryId colorizable removeFromBrowse skuPriceInfo { fullSkuId currencyLabel currencySymbol listPrice salePrice memberPrice tradePrice onSale onClearance showMemberPrice skuOptions { id optionType label __typename } __typename } priceInfo { currencyLabel currencySymbol isCustomProduct isRetail isUnavailable priceFilter isSale priceMessage priceRange { allOnSale assetId currencyApplied highestFullSkuId highestPaidFullSkuId lowestFullSkuId lowestPaidFullSkuId noPriceRange onClearance onSale onSaleAndOnClearance previewMode salePriceListId tradeBest __typename } rangeType showMemberPrice strikePriceLabel priceMessagePrice listPrices listPriceLabel salePrices salePriceLabel memberPrices memberPriceLabel __typename } swatchInfo { swatchesToDisplay { displayName imageRef imageUrl swatchId displayName __typename } numAdditionalSwatchesAvailable numAdditionalSaleSwatchesAvailable __typename } __typename } sku { fullSkuId __typename } __typename } sortOptions { navigationState label selected __typename } __typename } instructionResultList { firstRecNum lastRecNum recsPerPage totalNumRecs name records { productDisplayName link label __typename } __typename } __typename } } ","operationName":"InfiniteScroll","variables":"{\"ntt\":\"" + query + "\",\"no\":"+ str(start) +",\"currencyCode\":\"USA\",\"nrpp\":10}"}
                        r = requests.request("GET", API_URL, headers=HEADERS, params=querystring).json()
                        try:
                            start = r['data']['infiniteScroll']['resultList']['lastRecNum']
                        except:
                            break
                        total_products = r['data']['infiniteScroll']['resultList']['totalNumRecs']
                        products = r['data']['infiniteScroll']['resultList']['records']
                        for product in products:
                            product = product['product']
                            prodID = product['repositoryId']

                            swatches = []
                            index = 0
                            try:
                                for swatch in product['swatchInfo']['swatchesToDisplay']:
                                    swatch_index = index
                                    swatch_images = swatch["imageUrl"]
                                    swatch_name = swatch['displayName']
                                    swatches.append({'index': swatch_index,
                                                    'images': swatch_images,
                                                    'name': swatch_name})
                                    index += 1
                            except:
                                pass

                            if prodID not in skus:
                                new = True
                                skus.append(prodID)
                            querystring = {"query":"query BaseProduct($productId: String!, $categoryId: String, $filter: String, $userType: String) { product( productId: $productId categoryId: $categoryId filter: $filter userType: $userType ) { __typename ...BaseProductFields } } fragment BaseProductFields on Product { isActive endDate subName longDescription merchMessage targetUrl emptyProduct onSale giftCert featureList dimensions deliveryDimensions careInstructions fixedDisplaySku layout productListTitle id type displayName imageUrl galleryDescription newProduct template suppressSwatchCopy alternateImages { imageUrl caption video __typename } colorizeInfo { colorizable __typename } layout priceRangeDisplay { ...PriceRangeDisplay __typename } index rangeId parentCategoryId fileLinkUrls { link label __typename } instock { hasInStock showInStockButton showInStockMessage __typename } sale { hasSale showSaleButton showSaleMessage __typename } uxAttributes { productType triggerSwatchImage giftCert __typename } swatchesToBuy { atgSkuId swatchId productId fullSkuId __typename } customProduct __typename } fragment PriceRangeDisplay on ProductPriceRangeDisplay { __typename rangeType isUnavailable isSale showMemberPrice listPrices salePrices memberPrices salePriceLabel priceMessage priceMessagePrice listPriceLabel memberPriceLabel strikePriceLabel currencySymbol currencyLabel overridePriceLabel overrideLowestSkuListPrice overrideLowestSkuSalePrice overrideLowestSkuMemberPrice priceFilter hasOnlyOneSku } ","operationName":"BaseProduct","variables":"{\"productId\":\""+prodID+"\",\"filter\":null,\"userType\":\"\"}"}
                            yield scrapy.Request(add_url_params(API_URL, querystring), method="GET", headers=HEADERS, meta={'category': categoriesList, 'sku': prodID, 'swatches': swatches}, callback=self.parse_product, dont_filter=False)
                        if not new:
                            break


    def parse_product(self, response):
        product = response.json()['data']['product']
        if not product['isActive']:
            return
        images = []
        for image in product['alternateImages']:
            if 'imageUrl' in image and image['imageUrl']:
                images.append('https:' + image['imageUrl'])

        categories = response.meta['category']
        yield {
            'SKU': response.meta['sku'].replace('prod', ''),
            'URL': 'https://rh.com' + product['targetUrl'],
            'Main Category': categories[0] if len(categories) else '',
            'Sub Category 1': categories[1] if len(categories) > 1 else '',
            'Sub Category 2': categories[2] if len(categories) > 2 else '',
            # 'Sub Category 3': categories[3] if len(categories) > 3 else '',
            'Product Name': product['displayName'],
            # 'Rating': Totalrating,
            # '# of reviews': json_response['reviewAggregate']['reviewCount'] if 'reviewCount' in json_response['reviewAggregate'] else 0,
            'Price': product['priceRangeDisplay']['listPrices'][0] if product['priceRangeDisplay']['listPrices'] else '',
            'Sale Price': product['priceRangeDisplay']['salePrices'][0] if product['priceRangeDisplay']['salePrices'] != product['priceRangeDisplay']['listPrices'] else '',
            'Member Prices': product['priceRangeDisplay']['memberPrices'][0] if product['priceRangeDisplay']['memberPrices'] else '',
            'Details': cleanhtml(', '.join(product['featureList'])).replace('\n', ' '),
            'Dimension': cleanhtml(', '.join(product['dimensions'])).replace('\n', ' ').replace('&#39;', "'").replace('&#34;', '"').replace('#189;', '½').replace('&#190;', '¾').replace('Detailed Specifications', '').replace('#188;', '¼'),
            'Swatches': response.meta['swatches'],
            'Main Image': 'https:' + product['imageUrl'],
            'Image 1': images[1] if len(images) > 1 else '',
            'Image 2': images[2] if len(images) > 2 else '',
            'Image 3': images[3] if len(images) > 3 else '',
            'Image 4': images[4] if len(images) > 4 else '',
            'Image 5': images[5] if len(images) > 5 else '',
        }

def add_url_params(url, params):
    """ Add GET params to provided URL being aware of existing.
    'http://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    url = unquote(url)
    parsed_url = urlparse(url)
    get_args = parsed_url.query
    parsed_get_args = dict(parse_qsl(get_args))
    parsed_get_args.update(params)

    parsed_get_args.update(
        {k: dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url

def cleanhtml(raw_html):
    if raw_html:
        raw_html=str(raw_html).replace('</',' ^</')
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        cleantext=(' '.join(cleantext.split())).strip()
        cleantext=str(cleantext).replace(' ^','^').replace('^ ','^')
        while '^^' in cleantext:
            cleantext=str(cleantext).replace('^^','^')
        cleantext=str(cleantext).replace('^','\n')
        return cleantext.strip()
    else:
        return ''
