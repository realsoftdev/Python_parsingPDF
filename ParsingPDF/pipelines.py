# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.files import FilesPipeline
from tabula import read_pdf, convert_into
from scrapy.http import Request

class ParsingpdfPipeline(FilesPipeline):

    current = 0

    def get_media_requests(self, item, info):
        meta = {
            'filename': item['company_name']
        }
        for image_url in item['file_urls']:
            yield Request(image_url, meta=meta)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        self.parse_pdf('./Downloadfiles/' + image_paths[0])
        return item

    def file_path(self, request, response=None, info=None):
        filename = request.meta.get('filename', '')
        return '%s.%s' % (filename, 'pdf')

    def parse_pdf(self, path):
        self.current += 1
        try:
            df = convert_into(path, str(self.current) + '.csv', output_format='csv')
            print 'parsing'
        except:
            print 'parsing error'
        pass