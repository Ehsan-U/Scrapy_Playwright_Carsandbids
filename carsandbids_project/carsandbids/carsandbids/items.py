# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst

class CarsandbidsItem(scrapy.Item):
    # define the fields for your item here like:
    Make = scrapy.Field(output_processor=TakeFirst())
    Model = scrapy.Field(output_processor=TakeFirst())
    Mileage = scrapy.Field(output_processor=TakeFirst())
    VIN = scrapy.Field(output_processor=TakeFirst())
    Title_Status = scrapy.Field(output_processor=TakeFirst())
    Location = scrapy.Field(output_processor=TakeFirst())
    Engine = scrapy.Field(output_processor=TakeFirst())
    Transmission = scrapy.Field(output_processor=TakeFirst())
    ExteriorColor = scrapy.Field(output_processor=TakeFirst())
    InteriorColor = scrapy.Field(output_processor=TakeFirst())
    Year = scrapy.Field(output_processor=TakeFirst())
    Price = scrapy.Field(output_processor=TakeFirst())
    Kilometers = scrapy.Field(output_processor=TakeFirst())
    TMU = scrapy.Field(output_processor=TakeFirst())
    No_Reserver = scrapy.Field(output_processor=TakeFirst())
    URL = scrapy.Field(output_processor=TakeFirst())
    Raw_Title = scrapy.Field(output_processor=TakeFirst())
    Raw_Subtitle = scrapy.Field(output_processor=TakeFirst())
    Raw_Miles = scrapy.Field(output_processor=TakeFirst())
    Source = scrapy.Field(output_processor=TakeFirst())
    Main_Image = scrapy.Field(output_processor=TakeFirst())
    All_Images = scrapy.Field(output_processor=TakeFirst())
