import scrapy
import time
import urlparse
import json
from tabula import read_pdf

class DocumentScraper(scrapy.Spider):
    name = "document_app"
    allowed_domains = ['http://documents.dps.ny.gov/']
    start_urls = ['http://documents.dps.ny.gov/public/MatterManagement/CaseMaster.aspx?MatterSeq=41907']

    company_names = {
        0 :'Niagara Mohawk Power Corporation',
        1 :'New York State Electric',
        2 :'Central Hudson Gas',
        3 :'Orange and Rockland Utilities, Inc',
        4 :'Consolidated Edison Company of New York, Inc.',
    }

    titles = [
        'SIR Inventory Report',
        'SIR Inventory Spreadsheet Thru',
        'SIR Inventory Report',
        'Filed {month} SIR',
        'PSC SIR Monthly Report {month} {year}',
    ]

    months = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
    ]

    def getTitleXpath(self, key, current_year):
        if key < 3:
            title_xpath = 'contains(td/a/text(), "{0}")'
            title = title_xpath.format(self.titles[key])
            return title
        if key == 3:
            title_xpath = []
            for month in self.months:
                title_xpath.append('contains(td/a/text(), "' + self.titles[key].format(month=month) + '")')
            return ' or '.join(title_xpath)
        if key == 4:
            title_xpath = []
            for year in range(int(current_year)-1, int(current_year)+1):
                for month in self.months:
                    title_xpath.append('contains(td/a/text(), "' + self.titles[key].format(month=month, year=year) + '")')
            return ' or '.join(title_xpath)

    def parse(self, response):
        current_year = time.strftime("%Y")
        for key in self.company_names:
            c_name = self.company_names[key]
            title = self.getTitleXpath(key, current_year)
            xpath_str = '//tr[({title}) and contains(@class, "t_grid_datain")]'
            trs = response.xpath(xpath_str.format(title=title))
            selected_tr = None
            for tr in trs:
                company_field = tr.xpath('.//td[position()=5]').extract()
                if c_name not in company_field[0]:
                    continue
                date = tr.xpath('.//td[position()=2]/text()').extract()
                pdf_url = tr.xpath('.//td[position()=4]/a/@href').extract()
                pdf_url = urlparse.urljoin(response.url, pdf_url[0])
                if selected_tr:
                    if self.compare(selected_tr['date'], date[0]):
                        continue
                selected_tr = { 'date': date[0], 'pdf_url': pdf_url }
            if selected_tr:
                yield {
                    'file_urls': [selected_tr['pdf_url']],
                    'company_name': c_name,
                    'date': selected_tr['date']
                }

    def compare(self, a, b):
        a = a.split('/')
        b = b.split('/')
        if int(a[2]) < int(b[2]): return False
        elif int(a[2]) > int(b[2]): return True
        if int(a[0]) < int(b[0]): return False
        elif int(a[0]) > int(b[0]): return True
        if int(a[1]) < int(b[1]): return False
        elif int(a[1]) > int(b[1]): return True
        return True
