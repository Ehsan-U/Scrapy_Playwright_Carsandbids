import json
import re
from urllib.parse import urljoin
import scrapy
from scrapy_playwright.page import PageMethod 
from scrapy.selector import Selector
from rich.console import Console
from scrapy.loader import ItemLoader
from ..items import CarsandbidsItem

class CarsSpider(scrapy.Spider):
    not_required = ['seller','body style','seller type','drivetrain']
    name = 'pastcars'
    urls = set()
    counter = 0
    page_count = 1
    allowed_domains = ['carsandbids.com']
    con = Console()
    def start_requests(self):
        url = "https://carsandbids.com/past-auctions/"
        yield scrapy.Request(
            url,callback=self.parse,
            meta={"playwright":True,"playwright_include_page":True,"playwright_page_methods":[
                PageMethod("wait_for_selector","//li[@class='auction-item ']"),
            ]},
            errback=self.errback,
            )

    # parse main page & extract url of each car page & also handle pagination
    async def parse(self,response):
        page = response.meta.get("playwright_page")
        source = await page.content()
        sel = Selector(text=source)
        priv_urls = len(self.urls)
        extracted_urls = set()
        # extract 50 urls from a page
        for link in sel.xpath("//div[@class='auction-title']/a/@href").getall():
            link = response.urljoin(link)
            self.urls.add(link)
            extracted_urls.add(link)
        self.con.print("[+] [bold green] Extracted URLS [bold cyan]",len(extracted_urls))
        await page.close()
        self.page_count+=1
        # parse extracted 50 url pages
        for url in extracted_urls:
            yield scrapy.Request(
            url,callback=self.parse_car,
            meta={"playwright":True,"playwright_include_page":True,"playwright_page_methods":[
                PageMethod("wait_for_selector","//div[@class='quick-facts']"),
            ]},
            errback=self.errback,
            )
        # add more 50 urls from a page & repeat the process until no unique car urls remain.
        if len(self.urls) > priv_urls:
            url = f"https://carsandbids.com/past-auctions/?page={self.page_count}"
            yield scrapy.Request(
                url,callback=self.parse,
                meta={"playwright":True,"playwright_include_page":True,"playwright_page_methods":[
                    PageMethod("wait_for_selector","//li[@class='auction-item ']"),
                ]},
                errback=self.errback,
                )

    # parsing car page
    async def parse_car(self,response):
        try:
            loader = ItemLoader(item=CarsandbidsItem(),response=response)
            sel = Selector(text=response.body)
            year = sel.xpath("//div[@class='auction-title']/h1/text()").get()[:4]
            raw_title = sel.xpath("//div[@class='auction-title']/h1/text()").get()
            raw_subtitle = sel.xpath("//div[@class='d-md-flex justify-content-between flex-wrap']/h2/text()").get()
            if sel.xpath("//div[@class='d-md-flex justify-content-between flex-wrap']//h2/span").get():
                no_reserver = "True"
            else:
                no_reserver = "False"
            source = response.url
            price = sel.xpath("//span[@class='value']/span[@class='bid-value']/text()").get()
            main_image = sel.xpath("//div[@class='preload-wrap main loaded']/img/@src").get()
            images = ",".join(sel.xpath("//div[@class='preload-wrap  loaded']/img/@src").getall())
            if "kilometers" in sel.xpath("//div[@class='detail-wrapper']").get().lower():
                kilometers = "True"
            else:
                kilometers = "False"
            dt_tags = sel.xpath("//div[@class='quick-facts']//dt")
            dd_tags = sel.xpath("//div[@class='quick-facts']//dd")
            for dt,dd in zip(dt_tags,dd_tags):
                if dd.xpath(".//a"):
                    if not dt.xpath(".//text()").get().lower() in self.not_required:
                        loader.add_value(dt.xpath(".//text()").get(),dd.xpath(".//a/text()").get())
                else:
                    if not dt.xpath(".//text()").get().lower() in self.not_required:
                        if dt.xpath(".//text()").get() == "Mileage":
                            raw_miles = dd.xpath(".//text()").get()
                            if "TMU" in raw_miles:
                                tmu = "True"
                            else:
                                tmu = "False"
                            Mileage = ''
                            miles_characters = list(dd.xpath(".//text()").get())
                            for c in miles_characters:
                                if c.isdigit():
                                    Mileage +=c
                            # data["Mileage"] = Mileage
                            loader.add_value('Mileage',Mileage)
                        elif "title" in dt.xpath(".//text()").get().lower():
                            loader.add_value("Title_Status",dd.xpath(".//text()").get())
                        elif "exterior" in dt.xpath(".//text()").get().lower():
                            loader.add_value("ExteriorColor",dd.xpath(".//text()").get())
                        elif "interior" in dt.xpath(".//text()").get().lower():
                            loader.add_value("InteriorColor",dd.xpath(".//text()").get())
                        else:
                            loader.add_value(dt.xpath(".//text()").get(), dd.xpath(".//text()").get())
    
            loader.add_value("Year",year)
            loader.add_value("Price",price)
            loader.add_value("Kilometers",kilometers)
            loader.add_value("TMU",tmu)
            loader.add_value("No_Reserver",no_reserver)
            loader.add_value("URL",response.url)
            loader.add_value("Raw_Title",raw_title)
            loader.add_value("Raw_Subtitle",raw_subtitle)
            loader.add_value("Raw_Miles",raw_miles)
            loader.add_value("Source",response.url)
            loader.add_value("Main_Image",main_image)
            loader.add_value("All_Images",images)
            page = response.meta.get("playwright_page")
            await page.close()
            self.counter+=1
            self.con.print(f"[+] [bold green]]Processed Items: [bold cyan]{self.counter},[bold green] Remaining Items: [bold cyan]{len(self.urls)-self.counter}")
            yield loader.load_item()
        # self.con.print(data) 
        except:
            self.con.print_exception()
    async def errback(self,failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
