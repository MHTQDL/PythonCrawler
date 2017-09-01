#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
from bs4 import BeautifulSoup
import urllib2
import urllib
import cookielib
import MySQLdb

# 解析
class Analysis(object):
    """docstring for Analysis"""


    #拍卖会分页解析  page_html=分页html  crawlingData=访问网页返回html urllib2 headers  data
    def funPaging(self,page_html):
        bs_obj = BeautifulSoup(page_html, "html.parser")
        # 1.找到分页div
        div = bs_obj.find(attrs={'class': 'result-page'})
        #2.找到div下的所有a标签
        a_arr = div.find_all('a')
        #3.清理掉 首页 下一页 确定
        a_arr = a_arr[1:len(a_arr) - 2]
        return  a_arr


    #计算共几页数
    def funPagingSum(self,page_html):
        bs_obj = BeautifulSoup(page_html, "html.parser")
        div = bs_obj.find(attrs={'class': 'result-page'})
        if div !=None:
            #获取共几页
            sum=div.find(attrs={'class': 'sum'}).get_text()
            sum=int(sum[1:len(sum)-1].encode('utf-8'))
            return sum
        else:
            return 1


    # 拍卖品列表解析
    def funLot(self,html):
        list = []
        bs_obj = BeautifulSoup(html, "html.parser")
        # 1.找到ul列表
        dataList = bs_obj.find(attrs={'class': 'imgList specWorks clearfix'})
        for data in dataList.contents:
            if data != "\n":
                map={}
                # map['名称']=data.find('h3').find('a').get_text()
                map['名称']=data.find('h3').find('a').attrs.get('title')
                print "名称=",map['名称']

                # if str(map['名称']) == "中国青花瓷器、Christie's  300 years of Jade(HK)":
                #     return list

                map['url']=data.find('h3').find('a').attrs.get('href')
                li_arr = data.find('ul').find_all('li')
                for li in li_arr:
                    if li.find('em', text='LOT号：'):
                        map['LOT号']= li.get_text()[5:len(li.get_text())]
                        print "LOT号=",map['LOT号']
                    if li.find('em', text='估价：'):
                        map['估价']= li.find('span').get_text()
                        print "估价=", map['估价']
                    if li.find('em', text='成交价：'):
                        map['成交价'] = li.find('span').get_text()
                        print "成交价=", map['成交价']
                    if li.find('em', text='城市：'):
                        map['城市'] = li.get_text()[3:len(li.get_text())]
                        print "城市=", map['城市']
                    if li.find('em', text='日期：'):
                        map['日期'] = li.get_text()[3:len(li.get_text())]
                        print "日期=", map['日期']
                list.append(map)
        return list

    # 专场列表解析
    def funSpecialList(self, html):
        list=[]
        bs_obj = BeautifulSoup(html, "html.parser")
        # 1.找到ul列表
        dataList = bs_obj.find(attrs={'class': 'imgList noteList clearfix'})
        # 2.循环列表每一行数据
        for data in dataList.contents:
            # 3.清理数据 筛选掉\n 和 不是数据的li标签
            if len(data)>3:
                map={}
                li_arr=data.find('ul').find_all('li')

                # 专场名称
                map['专场名称'] = data.find('h3').find('a').get_text()
                print '专场名称=', data.find('h3').find('a').get_text()
                # 专场url
                map['专场url'] = data.find('h3').find('a').attrs.get('href')
                print '专场url=', data.find('h3').find('a').attrs.get('href')
                url_arr=data.find('h3').find('a').attrs.get('href').split('/')
                if len(url_arr)>3:
                    map['拍卖会id'] = url_arr[2].encode('utf-8')
                    print '拍卖会id=', url_arr[2].encode('utf-8')
                    map['专场id']=url_arr[3].encode('utf-8')
                    print '专场id=',url_arr[3].encode('utf-8')
                else:
                    map['专场id']="-7"

                for li in li_arr:
                    if li.find('em',text='拍卖时间：'):
                        map['专场拍卖时间'] = li.find('span').get_text()
                        print '拍卖时间=', li.find('span').get_text()
                    elif li.find('em',text='拍卖地点：'):
                        map['专场拍卖地点'] = li.get_text()[5:len(li.get_text())]
                        print '拍卖地点=', li.get_text()[5:len(li.get_text())]
                    elif li.find('em',text='拍卖总数：'):
                        map['专场拍卖总数'] =li.find('span').get_text()
                        print '拍卖总数=', li.find('span').get_text()
                    elif li.find('em',text='成交额：'):
                        map['专场成交额'] = li.get_text()[8:len(li.get_text())]
                        print '成交额=', li.get_text()[8:len(li.get_text())]
                    elif li.find('em',text='成交率：'):
                        map['专场成交率'] = li.get_text()[8:len(li.get_text())]
                        print '成交率=', li.get_text()[8:len(li.get_text())]
                print '####################################################################'
                list.append(map)
        return list

    # 拍卖会列表数据解析
    def funAuctionList(self, html):
        #list
        list = []
        bs_obj = BeautifulSoup(html, "html.parser")
        #1.找到ul列表
        dataList = bs_obj.find(attrs={'class': 'dataList'})
        #2.循环列表每一行数据
        for data in dataList.contents:
            #3.清理数据 筛选掉\n
            if data != "\n":
                #key:value
                map={}
                #4.获取一行li ->(第1个)ul->(6个)li
                date_li_arr=data.contents[1].find_all('li')
                if len(date_li_arr) >= 1:
                    #拍卖会名称
                    map['拍卖会名称']=date_li_arr[0].find('a').attrs.get('alt')
                    print '拍卖会名称 =',date_li_arr[0].find('a').attrs.get('alt')
                    #拍卖会 url
                    map['拍卖会url']=date_li_arr[0].find('a').attrs.get('href')
                    url_arr=date_li_arr[0].find('a').attrs.get('href').split('/')
                    map['公司id'] = url_arr[1]
                    map['拍卖会id']=url_arr[2]
                    print '公司id=', url_arr[1]
                    print '拍卖会id=',url_arr[2]
                    print '拍卖会url =',date_li_arr[0].find('a').attrs.get('href')
                if len(date_li_arr) >= 2:
                    #上拍/成交(件)
                    map['拍卖会上拍/成交(件)']=date_li_arr[1].get_text()
                    print '上拍/成交(件) =',date_li_arr[1].get_text()
                if len(date_li_arr) >= 3:
                    #成交额(万)
                    map['拍卖会成交额(万)']=date_li_arr[2].get_text()
                    print '成交额(万) =',date_li_arr[2].get_text()
                if len(date_li_arr) >= 4:
                    #拍卖公司
                    map['拍卖会拍卖公司']=date_li_arr[3].find('a').get_text()
                    print '拍卖公司 =',date_li_arr[3].find('a').get_text()
                    #拍卖公司url
                    map['拍卖会拍卖公司url']=date_li_arr[3].find('a').attrs.get('href')
                    print '拍卖公司url =',date_li_arr[3].find('a').attrs.get('href')
                if len(date_li_arr) >= 5:
                    #拍卖城市
                    map['拍卖会拍卖城市']=date_li_arr[4].get_text()
                    print '拍卖城市 =',date_li_arr[4].get_text()
                if len(date_li_arr) >= 6:
                    #拍卖日前
                    map['拍卖会拍卖日期']=date_li_arr[5].get_text()
                    print '拍卖日期 =',date_li_arr[5].get_text()
                list.append(map)
                print '####################################################################'
        return list

    #拍卖会详细页
    def funAuctionDetailed(self,html):
        bs_obj = BeautifulSoup(html, "html.parser")
        dataList = bs_obj.find(attrs={'class': 'infDetail'})
        #1.查找到拍卖信息
        data=dataList.find_all('dl')[1]
        li_arr=data.find('ul').find_all('li')
        map = {}

        for li in li_arr:
            if li.find('em',text='时间：'):
                map['时间'] = li.get_text()[3:len(li.get_text())].strip()
                print '时间=', li.get_text()[3:len(li.get_text())].strip()
            elif li.find('em', text='地点：'):
                map['地点'] = li.get_text()[3:len(li.get_text())].strip()
                print '地点=', li.get_text()[3:len(li.get_text())].strip()
            elif li.find('em', text='成交总额：'):
                map['成交总额'] = li.get_text()[5:len(li.get_text())]
                print '成交总额=', li.get_text()[5:len(li.get_text())]
            elif li.find('em', text='成 交 率：'):
                map['成交率'] = li.get_text()[6:len(li.get_text())]
                print '成交率=', li.get_text()[6:len(li.get_text())]

        return map

# 爬取数据
class CrawlingData(object):
    # 爬取数据
    def funCrawData(self, urllib2, url, headers, data, isJson):
        if isJson:
            postdata = urllib.urlencode(data)
        else:
            postdata=data
        req = urllib2.Request(url, postdata, headers)
        return urllib2.urlopen(req,timeout=120).read()
    #ajax
    def request_ajax_data(self,urllib2,url, data, isJson):
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
        req.add_header('X-Requested-With', 'XMLHttpRequest')
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0')
        #重要
        req.add_header('Referer','http://auction.artron.net')
        if isJson:
            postdata = urllib.urlencode(data)
        else:
            postdata=data
        response = urllib2.urlopen(req,postdata ,timeout=120)
        text = response.read()

        if isJson:
            return json.loads(text)
        else:
            return text
class MysqlTool():
    def connect(self):
        #打开连接
        self.__conn = MySQLdb.connect(host="111.206.163.56", user="poly", passwd="poly.thinda", db="bl", charset='utf8')
        # self.__conn = MySQLdb.connect(host="xxx.xxx.xxx.xx", user="xxx", passwd="xxxx", db="xxx", charset='utf8')
        # 使用cursor()方法获取操作游标
        self.__cursor = self.__conn.cursor()
    def getInsert(self,sql):
        try:
            # 执行sql
            self.__cursor.execute(sql)
            #返回最新插入行的主键ID
            # id=self.__cursor.insert_id()
            # 提交到数据库执行
            self.__conn.commit()
        except MySQLdb.Error, e:
            try:
                sqlError =  "Error %d:%s" % (e.args[0], e.args[1])
                print "sqlError:",sqlError
            except IndexError:
                print "MySQL Error:%s" % str(e)
                # 发生错误时回滚
            finally:
                print '发生错误回滚:', sql
                self.__conn.rollback()
    def queryAuction(self,id):

        # SQL 查询语句
        sql = "SELECT auction_id FROM crawler_auction WHERE auction_id='" + id + "'"
        try:
            self.__cursor.execute(sql)
            results = self.__cursor.fetchall()
            if len(results)>0:
                return True
            else:
                return False
        except MySQLdb.Error, e:
            try:
                sqlError = "Error %d:%s" % (e.args[0], e.args[1])
                print "sqlError:", sqlError
            except IndexError:
                print "MySQL Error:%s" % str(e)
                # 发生错误时回滚
            finally:
                print '发生错误:', sql

    def querySpecial(self,special_id,special_name):

        # SQL 查询语句
        sql = "SELECT special_id FROM crawler_special WHERE special_id='" + special_id + "' AND special_name='"+special_name+"'"
        try:
            self.__cursor.execute(sql)
            results = self.__cursor.fetchall()
            if len(results)>0:
                return True
            else:
                return False
        except MySQLdb.Error, e:
            try:
                sqlError = "Error %d:%s" % (e.args[0], e.args[1])
                print "sqlError:", sqlError
            except IndexError:
                print "MySQL Error:%s" % str(e)
                # 发生错误时回滚
            finally:
                print '发生错误:', sql

    def queryLot(self,c1,c6):
        # SQL 查询语句
        sql = "SELECT lot_id FROM crawler_lot WHERE special_id='" + c6 + "' AND lot_id='" + c1 + "'"
        try:
            self.__cursor.execute(sql)
            results = self.__cursor.fetchall()
            if len(results) > 0:
                return True
            else:
                return False
        except MySQLdb.Error, e:
            try:
                sqlError = "Error %d:%s" % (e.args[0], e.args[1])
                print "sqlError:", sqlError
            except IndexError:
                print "MySQL Error:%s" % str(e)
                # 发生错误时回滚
            finally:
                print '发生错误:', sql

    def closeConnect(self):
        # 关闭数据库连接
        self.__conn.close()
        print "连接关闭"



if __name__ == '__main__':
    # 主地址
    url = 'http://auction.artron.net'
    # 登陆地址
    login_url = 'https://passport.artron.net/login/doing/'
    #专场ajax地址
    special_data_ajax_url = 'http://auction.artron.net/getallspecial.php'
    # 设置头信息
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0'}
    # 登陆用户名与密码
    data = {"account": "13904032887", "appid": "", "passwd": "mohaotian7", "redirect": ""}
    # 设置保存cookie的文件，同级目录下的cookie.txt
    filename = 'cookie.txt'
    # 声明一个CookieJar对象实例来保存cookie
    cookiejar = cookielib.CookieJar()
    # 声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
    cookiejar = cookielib.MozillaCookieJar(filename)


    # 爬取数据
    crawlingData = CrawlingData()
    # 解析数据
    analysis = Analysis()


    ##########################################################################
    '''
    模拟登陆 记录cookie
    '''
    whereCookie = True
    #从cookie.txt中 读取cookie
    if not whereCookie:
        # 创建MozillaCookieJar实例对象
        cookiejar = cookielib.MozillaCookieJar()
        # 从文件中读取cookie内容到变量
        cookiejar.load('cookie.txt', ignore_discard=True, ignore_expires=True)

    # 利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
    cookie = urllib2.HTTPCookieProcessor(cookiejar)
    # 通过handler来构建opener
    opener = urllib2.build_opener(cookie, urllib2.HTTPHandler())
    urllib2.install_opener(opener)
    #登陆一次获取cookie 存储到cookie.txt
    if whereCookie:
        # 登陆
        crawlingData.funCrawData(urllib2, login_url, headers, data,True)
        # 保存cookie到文件
        cookiejar.save(ignore_discard=True, ignore_expires=True)
    ##########################################################################


    #打印cookie
    # for item in cookiejar:
    #     print item.name + "=", item.value


    ##########################################################################
    #判断是否登陆成功
    bs_obj_login = BeautifulSoup(crawlingData.funCrawData(urllib2, url, headers, "",False), "html.parser")
    success = bs_obj_login.find(attrs={'class': 'logAft'})

    go = False
    if success != None:
        print '登陆成功'
        go = True
    else:
        print '登陆失败'
        go = False
    print '####################################################################'
    ##########################################################################

    # go=False
    ##########################################################################
    if go:
        try:
            #连接数据库
            mysql=MysqlTool()
            mysql.connect()
            # 拍卖结果 搜索地址
            search_url = '/result/pmh-0-0-2-0-1/?pmhname=2005秋季拍卖会'
            # 拍卖预展 搜索地址
            # search_url = '/preauction/pmh-0-0-1-0-0-1/?pmhname=第37期古董精品拍卖会'
            #1.返回搜索拍卖会列表的结果
            page_html=crawlingData.funCrawData(urllib2, url + search_url, headers, "",False)
            #2.解析拍卖会列表分页,9
            page_arr=analysis.funPaging(page_html)
            auctionList=[]
            #3.解析拍卖会列表数据qidelan7

            for a in page_arr:
                #1.获取分页url
                page_url=a.attrs.get('href')
                #2.访问此分页拍卖会列表html
                auction_list_html=crawlingData.funCrawData(urllib2, url + page_url, headers, "",False)
                #3.解析列表数据
                aucList=analysis.funAuctionList(auction_list_html)
                auctionList.extend(aucList)

            #遍历拍卖会 每一条拍卖会信息
            for auctMap in auctionList:
                #1.获取拍卖会详情页数据
                print "断点 -6"
                auc_html = crawlingData.funCrawData(urllib2,url+auctMap['拍卖会url'], headers, "", False)
                print "断点 -5"
                #2.获取拍卖会 成交率
                auctMap2=analysis.funAuctionDetailed(auc_html)

                a1 = auctMap['拍卖会id'].encode('utf-8')
                a3 = auctMap['拍卖会名称']
                print "",a1
                print "",a3



                #只读取当前条件数据
                # if a1 !='PMH000663':
                #     print a3," 停止存储"
                #     continue




                existAuction=mysql.queryAuction(a1)
                if existAuction:
                    print a3, "--存在"
                else:
                    print a3, "--不存在"
                    a2 = auctMap['拍卖会url']

                    a4 = auctMap['拍卖会拍卖城市']
                    a5 = auctMap2['地点']
                    a6 = auctMap['拍卖会拍卖日期']
                    a7 = auctMap['拍卖会上拍/成交(件)']
                    if '拍卖会成交额(万)' in auctMap:
                        a8 = auctMap['拍卖会成交额(万)']
                    else:
                        a8 = "-7"
                    if '成交率' in auctMap2:
                        a9 = auctMap2['成交率']
                    else:
                        a9 = "-7"
                    a10 = auctMap['公司id']
                    a11 = auctMap['拍卖会拍卖公司url']
                    print "断点 -4"
                    sql_auction = "INSERT INTO crawler_auction(auction_id,auction_url,auction_name,auction_city,auction_place,auction_date,turnover_number,turnover,turnover_rate,company_id,company_url) " \
                          "values ('" + a1 + "','" + a2 + "','" + a3 + "','" + a4 + "','" + a5 + "','" + a6 + "','" + a7 + "','" + a8 + "','" + a9 + "','" + a10 + "','" + a11 + "')"
                    # 2.插入数据库
                    mysql.getInsert(sql_auction)
                    print "断点 -3"
                #3.遍历专场
                #专场标示
                pmh_arr=auctMap['拍卖会url'].split('/')
                pmh=pmh_arr[2].encode('utf-8')
                #总分页数
                page=analysis.funPagingSum(auc_html)
                for i in range(1,page+1):
                    # 每一页专场列表
                    # 每一页专场列表
                    # 每一页专场列表

                    # 1.拼接分页
                    special_data_ajax ="phcd="
                    special_data_ajax+=pmh
                    special_data_ajax+="&page="
                    special_data_ajax+=str(i)
                    print "断点 -2"
                    # 2.获取专场列表html
                    special_html = crawlingData.request_ajax_data(urllib2, special_data_ajax_url, special_data_ajax, False)
                    print "断点 -1"
                    # 3.解析专场列表
                    specialList = analysis.funSpecialList(special_html)

                    # 4.存入数据库 专场数据
                    for map in specialList:
                        b1 = map['专场id']
                        b4 = map['专场名称']
                        existSpecial = mysql.querySpecial(b1,b4)
                        if existSpecial:
                            print b4,"--存在 专场"


                            # if b1 != 'PZ0003947':
                            #     print b4, " 停止存储"
                            #     continue



                        else:
                            print b4, "--不存在 专场"
                            if '拍卖会id' in map:
                                b2 = map['拍卖会id']
                            else:
                                b2 = str(pmh)
                            b3 = map['专场url']
                            b5 = map['专场拍卖时间']
                            b6 = map['专场拍卖地点']
                            if '专场拍卖总数' in map:
                                b7 = map['专场拍卖总数']
                            else:
                                b7 = "-7"
                            if '专场成交额' in map:
                                b8 = map['专场成交额']
                            else:
                                b8 = "-7"
                            if '专场成交率' in map:
                                b9 = map['专场成交率']
                            else:
                                b9 = "-7"
                            sql_special = "INSERT INTO crawler_special(special_id,auction_id,special_url,special_name,special_date,special_place,turnover_number,turnover,turnover_rate) " \
                                  "values ('" + b1 + "','" + b2 + "','" + b3 + "','" + b4 + "','" + b5 + "','" + b6 + "','" + b7 + "','" + b8 + "','" + b9 + "')"
                            # 2.插入数据库
                            mysql.getInsert(sql_special)
                        print "断点 1"
                        #拍品
                        if len(map['专场url'])>15:
                            lot_html = crawlingData.funCrawData(urllib2, url + map['专场url'], headers, "", False)
                            print "断点 2"
                            # 1.计算分页总数
                            lot_page = analysis.funPagingSum(lot_html)
                            print "断点 3"
                            for i in range(1, lot_page + 1):
                                url_str=str(map['专场url'])
                                url_str=url_str[0:len(url_str)-1]
                                lot_url=url_str+"-0-9-"+str(i)
                                #2.获取html
                                lot_html = crawlingData.funCrawData(urllib2, url + lot_url, headers, "", False)
                                print "断点 4"
                                #3.解析
                                lot_list=analysis.funLot(lot_html)
                                #4.遍历集合
                                for lot_map in lot_list:
                                    c1 = lot_map['LOT号']
                                    c6 = b1
                                    c8 = lot_map['名称']

                                    existLot = mysql.queryLot(c1, c6)
                                    if existLot:
                                        print "拍品：",c8,"--存在"
                                    else:
                                        print "拍品：",c8, "--不存在"
                                        c2 = lot_map['估价']
                                        c3 = '--'
                                        if '成交价' in lot_map:
                                            c3 = lot_map['成交价']
                                        c4 = lot_map['城市']
                                        c5 = lot_map['日期']
                                        c7 = lot_map['url']
                                        c9 = str(pmh)
                                        sql_lot="INSERT INTO crawler_lot(lot_id,appraisal,transaction_price,city,lot_date,special_id,url,lot_name,auction_id)  " \
                                            "values('"+c1+"','"+c2+"','"+c3+"','"+c4+"','"+c5+"','"+c6+"','"+c7+"','"+c8+"','"+c9+"')"

                                        # 5.插入数据库
                                        mysql.getInsert(sql_lot)

        except Exception, e:
            print e
        finally:
            mysql.closeConnect()
    ##########################################################################










