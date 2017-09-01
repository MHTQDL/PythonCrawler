#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from bs4 import BeautifulSoup
import urllib2
import urllib

# 爬取数据
class CrawlingData(object):
    # 爬取数据
    def funCrawData(self, urllib2, url, headers, data, isJson):
        postdata=data
        req = urllib2.Request(url, postdata, headers)
        return urllib2.urlopen(req).read()


if __name__ == '__main__':
    # 爬取数据
    crawlingData = CrawlingData()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0'}
    lot_html = crawlingData.funCrawData(urllib2, 'http://house.map.qq.com/mobile/list.html?id=230217', headers, "", False)
    print lot_html
    bs_obj_login = BeautifulSoup(lot_html,"html.parser")
    print bs_obj_login.getText();
