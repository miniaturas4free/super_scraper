import scrapy
import re

class CotoSpider(scrapy.Spider):
    name = "CotoSpider"
    base_url = "https://www.cotodigital3.com.ar"

    def start_requests(self):

        #urls = ["https://www.cotodigital3.com.ar/sitios/cdigi/browse"] #contains all categories together
        urls = ["https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-bebidas/_/N-1c1jy9y",
                "https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-almacén/_/N-8pub5z",
                "https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-frescos/_/N-1ewuqo6",
                "https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-congelados/_/N-1xgbihs",
                "https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-limpieza/_/N-nityfw",
                "https://www.cotodigital3.com.ar/sitios/cdigi/browse/catalogo-perfumer%C3%ADa/_/N-cblpjz"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        def clean_text(text: str) -> str:
            text_ = text.replace('\n', '').replace('\t', '').strip()
            text_ = " ".join(text_.split())
            return text_
        
        products = response.css('ul#products.grid').css('div.leftList')
        for product in products:
            result = {'name': None,
                      'sku': None,
                      'price': None,
                      'unit': None,
                      'url': None,
                      'img_url': None}
            try:
                result['name'] = clean_text(product.css('div.descrip_full::text').get())
                result['sku'] = product.css('div.descrip_full').attrib['id'].replace('descrip_full_sku','')
                result['price'] = clean_text(product.css('span.atg_store_productPrice')
                                           .css('span.atg_store_newPrice::text')
                                           .get()
                                           ),
                result['unit'] = clean_text(product.css('span.unit::text').get())
                result['url'] = self.base_url + product.css('div.product_info_container').css('a::attr(href)').get()
                result['img_url'] = product.css('span.atg_store_productImage').css('img::attr(src)').get()

                yield scrapy.Request(url=result['url'], callback=self.parse_product, cb_kwargs={"result": result})

            except:
                pass


        #Recursively returns next pages results to scrawler
        pagination_items = response.css('ul#atg_store_pagination').css('li')
        next_page = None
        for index, item in enumerate(pagination_items):
            # print ('\n' * 10 + item.get())
            if 'class' in item.attrib and 'active' in item.attrib['class']:
                route = pagination_items[index + 1].css('a::attr(href)').get()
                if route is not None:
                    next_page = self.base_url + route
                    break

        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)


    def parse_product(self, response, result):
        for div in response.css('div'):
            id = div.attrib.get('id')
            if (id == 'brandText'):
                text = div.xpath('string()').get().replace(' ', '')
                text = re.search (r'EAN:(\d+)', text)
                if text:
                    result['ean'] = text.group(1)
                    break

        yield result
