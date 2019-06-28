# -*- coding: utf-8 -*-
import scrapy
from drugRegSpider.items import DrugregSpiderItem as dri
from scrapy.http import FormRequest
import logging

class DrugsSpider(scrapy.Spider): 
    
    name            = "DrugsSpider"
    allowed_domains = ["rceth.by"]
    
    def _getReq(self, letter, pageNum = 1, controllerState = u''):
        
        logging.info(u"Make query %s-%i" % (letter,pageNum))        

        _url = u'https://rceth.by/Refbank/reestr_lekarstvennih_sredstv/results'
        _frmRqst = {u'FProps[0].IsText':          u'True',
        u'FProps[0].Name':                        u'N_LP',
        u'FProps[0].CritElems[0].Num':            u'1',
        u'FProps[0].CritElems[0].Val':            letter,
        u'FProps[0].CritElems[0].Crit':           u'Start',
        u'FProps[0].CritElems[0].Excl':           u'false',
        u'FOpt.VFiles':                           u'true',
        u'FOpt.VEField1':                         u'true',
        u'IsPostBack':                            u'true',
        u'PropSubmit':                            u'FOpt_PageN',
        u'ValueSubmit':                           u'%i' % (pageNum,),
        u'FOpt.PageC':                            u'100',
        u'FOpt.OrderBy':                          u'N_LP',
        u'FOpt.DirOrder':                         u'asc',
        u'QueryStringFind':                       controllerState
        }
        
        return FormRequest(_url, formdata=_frmRqst, callback=self.parse,
            meta={'currLetter': letter,'currPageNum': pageNum})
        
    def start_requests(self):
        _initSeq = u'АБВГДЕЖЗИКЛМНОПРСТУФХЦЧЭЮЯ0123456789'
        self.traversed = {l:[] for l in _initSeq}
        return [self._getReq(l) for l in _initSeq]

    def extract_text(self,elem):
        return elem.xpath('text()').extract()[0].strip()

    def parse(self, response):
               
        currLetter = response.meta['currLetter']
        currPageNum = response.meta['currPageNum']

        for i in range(1,len(response.xpath('//a[@name="FOpt_PageN"]'))):
            if not i in self.traversed[currLetter]:
                controllerState = response.xpath(u'//input[@id="QueryStringFind"]/@value').extract()[0]
                self.traversed[currLetter].append(i)
                yield self._getReq(currLetter,i+1, controllerState)

        for tr in response.xpath('//div[@class="table-view"]/table/tbody/tr'):
            
            currRow = tr.xpath('td')
            currItem = dri()
            
            currItem["name"]              = currRow[1].xpath('a/text()').extract()[0].strip()
            currItem["mnn"]               = self.extract_text(currRow[2])
            currItem["lForm"]             = self.extract_text(currRow[3])            
            currItem["manufacturer"]      = self.extract_text(currRow[4])
            currItem["invoker"]           = self.extract_text(currRow[5])
            currItem["certNum"]           = self.extract_text(currRow[6])
            currItem["regDtBegin"]        = self.extract_text(currRow[7])
            currItem["regDtExpire"]       = self.extract_text(currRow[8])
            currItem["originality"]       = self.extract_text(currRow[9])

            currItem["manuals"]           = '\n'.join([u':'.join([a.xpath('text()').extract()[0],a.xpath('@href').extract()[0].split('/')[-1]]) for a in currRow[1].xpath('span/a')])
            currItem["file_urls"]         = [u for u in [u'https://www.rceth.by%s' % (href,) for href in currRow[1].xpath('span/a/@href').extract()]]

            yield currItem
