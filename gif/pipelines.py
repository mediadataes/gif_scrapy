# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.utils.project import get_project_settings
from gif.items import GifItem
from gif.utils import mkdirs
import os
import json
import logging
import time
from airtable import Airtable
settings = get_project_settings()
logger = logging.getLogger(__name__)


class GifPipeline(object):
    def process_item(self, item, spider):
        return item


class SaveToFilePipeline(object):
    """ pipeline that save data to disk """

    def __init__(self):
        self.saveGifPath = settings['SAVE_GIF_PATH']
        mkdirs(self.saveGifPath)  # ensure the path exists

    def process_item(self, item, spider):
        if isinstance(item, GifItem):
            save_path = os.path.join(self.saveGifPath, item['id'])
            if os.path.isfile(save_path):
                pass  # simply skip existing items
                # or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,save_path)
                # logger.info("Update tweet:%s"%dbItem['url'])
            else:
                self.save_to_file(item, save_path)
                logger.info("Add gif:%s" % item['url'])

        else:
            logger.info("Item type is not recognised! type = %s" % type(item))

    @staticmethod
    def save_to_file(item, fname):
        """ input:
                item - a dict like object
                fname - where to save
        """
        with open(fname, 'w') as f:
            json.dump(dict(item), f)


class SaveToAirtablePipeline(object):
    """ pipeline that save data to airtable """

    def __init__(self):
        self.airtable = Airtable(base_key='<>', table_name='<>', api_key='<>')

    def process_item(self, gif_item, spider):
        if isinstance(gif_item, GifItem):
            # time.sleep(2)
            self.airtable.insert({
                "id": gif_item['id'],
                "gif": [
                    {
                        "url": gif_item['file_url']
                    }
                ],
                "site": gif_item['site'],
                "title": gif_item['title'],
                "url": gif_item['url'],
                "tags": gif_item['tags'],
                "author": gif_item['author'],
                "created": gif_item['created'],
                "category": gif_item['category'],
                "duration": gif_item['duration'],
                "dimensions": gif_item['dimensions']
            })

