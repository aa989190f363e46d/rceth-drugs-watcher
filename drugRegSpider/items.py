# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DrugregSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #Торговое наименование 
    name              = scrapy.Field()    
    #Международное наименование  
    mnn               = scrapy.Field()    
    #Формы выпуска
    lForm             = scrapy.Field()        
    #Производитель   
    manufacturer      = scrapy.Field()    
    #Заявитель  
    invoker           = scrapy.Field()    
    #Номер удостоверения   
    certNum           = scrapy.Field()    
    #Дата регистрации  
    regDtBegin        = scrapy.Field()    
    #Срок действия   
    regDtExpire       = scrapy.Field()    
    #Оригинальное    
    originality       = scrapy.Field() 
    # Руководства
    manuals           = scrapy.Field()
    # Files pipeline 
    # http://doc.scrapy.org/en/latest/topics/media-pipeline.html#using-the-files-pipeline
    file_urls         = scrapy.Field()
    files             = scrapy.Field()
