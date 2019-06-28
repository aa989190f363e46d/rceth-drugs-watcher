# -*- coding: utf-8 -*-

from scrapy.exporters import CsvItemExporter
from scrapy.pipelines.files import FilesPipeline
from scrapy.http import Request
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.conf import settings

import logging
import sqlite3
from os import path

class DrugregspiderFilesPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        
        def already_done(url): 
          return path.isfile(self.store._get_filesystem_path('full/%s' % (url.split('/')[-1],)))

        done = [url for url in item.get(self.FILES_URLS_FIELD, []) if already_done(url)]

        for n,u in enumerate(done):
          logging.info(u'%i. File %s already done. SKIPPED' % (n,u))

        return [Request(x) for x in item.get(self.FILES_URLS_FIELD, []) if not x in done]

    def file_path(self, request, response=None, info=None):        
        image_guid = request.url.split('/')[-1]
        return 'full/%s' % (image_guid)


class DrugregspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class SQLiteRegistryStorePipeline(object):

    def __init__(self):

        self.filename = settings.get('DB_FILE','/data/registry.sqlite')
        self.FEED_EXPORT_FIELDS  = settings['FEED_EXPORT_FIELDS']
        self.query_tmplt = "insert into registry(%s) values (%s)" % (','.join(self.FEED_EXPORT_FIELDS),','.join(['?' for _ in self.FEED_EXPORT_FIELDS]))
        self.conn = None
        
        dispatcher.connect(self.initialize, signals.engine_started)
        dispatcher.connect(self.finalize, signals.engine_stopped)
 
    def process_item(self, item, domain):
        
        try:
            self.conn.execute(self.query_tmplt, tuple([item[fl] for fl in self.FEED_EXPORT_FIELDS]))                                          
        except Exception as e:
            logging.error('Failed to insert item: ' + item['mnn'] + '. Error: ' + str(e))
            
        return item
 
    def initialize(self):
        if path.exists(self.filename):
            self.conn = sqlite3.connect(self.filename)
        else:
            self.conn = self.create_table()

    def finalize(self):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None
 
    def create_table(self):

        fld_sttmnt = ', '.join(['%s text' % (fn,) for fn in self.FEED_EXPORT_FIELDS if fn != 'certNum'])

        conn = sqlite3.connect(self.filename)

        ccry = """
                create table registry(
                    %s,
                    certNum         text primary key, 
                    tmstmp          DATETIME DEFAULT CURRENT_TIMESTAMP);
                """ % (fld_sttmnt,)

        conn.execute(ccry)

        logging.info("Table created with query %s" % (ccry,))

        for fn in self.FEED_EXPORT_FIELDS:
            if fn in ['name','mnn']:
                conn.execute("create index %s on registry(%s);" % (fn,fn))

        conn.commit()

        return conn

class DrugregspiderCsvItemExporter(CsvItemExporter):

    def __init__(self, *args, **kwargs):
        delimiter = settings.get('CSV_DELIMITER', ',')
        kwargs['delimiter'] = delimiter

        fields_to_export = settings.get('FEED_EXPORT_FIELDS', [])
        if fields_to_export :
            kwargs['fields_to_export'] = fields_to_export

        super(DrugregspiderCsvItemExporter, self).__init__(*args, **kwargs)
