import scrapy

class StocksSpider(scrapy.Spider):
    name="stocks"
    start_urls=[]
    url='http://eoddata.com/stocklist/NASDAQ/{}.htm'

    for i in range(65,91):
        start_urls.append(url.format(chr(i)))

    def parse(self, response):
        for stock in response.css("div#ctl00_cph1_divSymbols table.quotes tr")[1:]:  #不处理第一个tr
            yield{
                'code':stock.css("td a::text").get(),
                'name':stock.css("td")[1].css("::text").get()
            }

#python -m scrapy crawl stocks -o stocks.jl

