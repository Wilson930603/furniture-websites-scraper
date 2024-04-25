# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.exporters import CsvItemExporter

class CSVPipeline:
    def open_spider(self, spider):
        file_path_products = f'{spider.settings.get("DATA_FILE_PATH")}/Data_{spider.name}.csv'
        self.file_products = open(file_path_products, 'wb')
        self.exporter_products = CsvItemExporter(self.file_products, include_headers_line=True, encoding='utf-8-sig')
        self.exporter_products.start_exporting()

    def close_spider(self, spider):
        self.exporter_products.finish_exporting()
        self.file_products.close()

    def process_item(self, item, spider):
        self.exporter_products.export_item(item)
        return item
