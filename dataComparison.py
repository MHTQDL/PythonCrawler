#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import MySQLdb
from decimal import Decimal
from decimal import getcontext
import time as Time
import xlrd
#澳门改为false HKD
RMB=True
class MysqlTool:
    def connect(self):
        #打开连接
        self.__conn = MySQLdb.connect(host="xxx.xxx.xxx.xx", user="xxx", passwd="xxx", db="xx", charset='utf8')
        # 使用cursor()方法获取操作游标
        self.__cursor = self.__conn.cursor()

    def updata(self,sql):
        try:
            # 执行sql
            self.__cursor.execute(sql)
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

    def query(self,sql):
        try:
            self.__cursor.execute(sql)
            results = self.__cursor.fetchall()
            return results
        except MySQLdb.Error, e:
            try:
                sqlError = "Error %d:%s" % (e.args[0], e.args[1])
                print "sqlError:", sqlError
            except IndexError:
                print "MySQL Error:%s" % str(e)
                # 发生错误时回滚
            finally:
                print '发生错误:', sql
    #日志记录 保利拍卖会id，保利专场id，日志记录，雅昌拍卖会id，雅昌专场id，日志记录
    def contrast_log(self,a_auction_id,a_special_id,a_log,b_auction_id,b_special_id,b_log,a,b,c):

        sql = "INSERT INTO contrast_log(a_auction_id,a_special_id,a_log,b_auction_id,b_special_id,a,b,c) values('" + a_auction_id + "','" + a_special_id + "','" + a_log + "','" + b_auction_id + "','" + b_special_id + "','"+str(a)+"','"+str(b)+"','"+str(c)+"')"

        try:
            # 执行sql
            self.__cursor.execute(sql)
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

    #查找保利比雅昌多的拍品
    def findAMoreThanB(self,a_auction_id,a_special_id,b_auction_id,b_special_id):
        sql ="select * from (select a.lot,b.lot_id from (select lot from auction_item where STATUS !=4 and auction_id ='"+a_auction_id+"' and event_id='"+a_special_id+"' ) a LEFT join ( select lot_id from crawler_lot where special_id='"+b_special_id+"' and auction_id='"+b_auction_id+"') b on a.lot=b.lot_id ) a where a.lot_id is null"
        return self.query(sql)

    #查找保利比雅昌少的拍品
    def findALessThanB(self,a_auction_id,a_special_id,b_auction_id,b_special_id):
        sql ="select * from (select a.lot,b.lot_id from (select lot from auction_item where STATUS !=4 and auction_id ='"+a_auction_id+"' and event_id='"+a_special_id+"' ) a right join ( select lot_id from crawler_lot where special_id='"+b_special_id+"' and auction_id='"+b_auction_id+"' ) b on a.lot=b.lot_id ) a where a.lot is null"
        return self.query(sql)

    # 更新多余数据 为删除标识
    def updateALot(self,lot,a_auction_id,a_special_id):
        sql = "update auction_item set STATUS=4 where lot ='"+lot+"' and auction_id ='"+a_auction_id+"' and event_id='"+a_special_id+"'"
        self.updata(sql)

    #保利 成交总数
    def sumNumberA(self,a_auction_id,a_special_id):
        sql="SELECT count(1) FROM auction_item a_item  INNER JOIN auction a ON a_item.auction_id=a.id  INNER JOIN event e  ON e.id=a_item.event_id  where a_item.status!=4 and a_item.RMB_price>0 and a_item.auction_id ='"+a_auction_id+"' and a_item.event_id='"+a_special_id+"'"
        results=self.query(sql)
        for res in results:
            if res[0] == None:
                return 0
            else:
                return res[0]

    #保利 成交总额
    def sumPriceA(self,a_auction_id,a_special_id):
        sql = "SELECT SUM(a_item.RMB_price) FROM auction_item a_item INNER JOIN auction a ON a_item.auction_id=a.id INNER JOIN event e ON e.id=a_item.event_id where a_item.status!=4  and a_item.RMB_price>0 and a_item.auction_id ='"+a_auction_id+"' and a_item.event_id='"+a_special_id+"' "
        results = self.query(sql)
        for res in results:
            if res[0] ==  None:
                return 0
            else:
                return res[0]

    #保利 拍品总数
    def sumLotA(self,auction_id,special_id):
        sqlA_count = "select count(*) from auction_item where STATUS !=4 and auction_id ='" +auction_id + "' and event_id='" + special_id+ "'"
        countA = self.query(sqlA_count)
        for a in countA:
            if a[0] ==  None:
                return 0
            else:
                return a[0]


    #雅昌 成交总数
    def sumNumberB(self,auction_id,b_special_id):
        sql = "select count(1) from crawler_lot where transaction_price != '--' and transaction_price != '流拍' and special_id='"+b_special_id+"' and auction_id='"+auction_id+"'"
        results = self.query(sql)
        for res in results:
            if res[0] == None:
                return 0
            else:
                return res[0]


    #雅昌 成交总额
    def sumPriceB(self,auction_id,b_special_id):
        sql = "select SUM(REPLACE(REPLACE(transaction_price,'RMB',''),',','')) from crawler_lot where transaction_price != '--' and transaction_price != '流拍'  and special_id='"+b_special_id+"' and auction_id='"+auction_id+"' "
        results = self.query(sql)
        for res in results:
            if res[0] == None:
                return 0
            else:
                return res[0]

    #雅昌 拍品总数
    def sumLotB(self,auction_id,special_id):
        sqlB_count = "select count(*) from crawler_lot where special_id='" +special_id+ "' and auction_id='"+auction_id+"' "
        countB = self.query(sqlB_count)
        for b in countB:
            if b[0] == None:
                return 0
            else:
                return b[0]

    #查找保利比雅昌多的成交拍品
    def findAMoreThanB_turnoverNumber(self,a_auction_id,a_special_id,b_auction_id,b_special_id):
        sql = "select * from ( select a.lot,b.lot_id from (select lot from auction_item where STATUS !=4 and RMB_price>0 and auction_id ='"+a_auction_id+"' and event_id='"+a_special_id+"' ) a LEFT join ( select lot_id from crawler_lot where transaction_price != '--' and special_id='"+b_special_id+"' and auction_id = '"+b_auction_id+"') b on a.lot=b.lot_id  ) a where a.lot_id is null"
        return self.query(sql)

    # 查找保利比雅昌少的成交拍品
    def findALessThanB_turnoverNumber(self, a_auction_id, a_special_id,b_auction_id,b_special_id):
        sql = "select * from ( select a.lot,b.lot_id from (select lot from auction_item  where STATUS !=4 and RMB_price>0 and auction_id ='" + a_auction_id + "' and event_id='" + a_special_id + "' ) a right join ( select lot_id from crawler_lot where transaction_price != '--' and special_id='" + b_special_id + "' and auction_id = '"+b_auction_id+"' ) b on a.lot=b.lot_id  ) a where a.lot is null"
        return self.query(sql)
    def unequalRMB(self,a_auction_id, a_special_id,b_auction_id,b_special_id):
        sql = "select * from ( SELECT lot,a_item.RMB_price as rmb FROM auction_item a_item  INNER JOIN auction a ON a_item.auction_id=a.id INNER JOIN event e ON e.id=a_item.event_id  where a_item.status!=4 and a_item.RMB_price>0 and a_item.auction_id ='"+a_auction_id+"' and a_item.event_id='"+a_special_id+"' ) a inner join (select lot_id,REPLACE(REPLACE(transaction_price,'RMB',''),',','') as rmb from crawler_lot where transaction_price != '--' and auction_id='"+b_auction_id+"' and special_id='"+b_special_id+"' ) b on a.lot=b.lot_id where a.rmb!= b.rmb"
        return self.query(sql)
    def unequalHKD(self,a_auction_id, a_special_id,b_auction_id,b_special_id):
        sql = "select * from ( SELECT lot,a_item.HKD_price as rmb FROM auction_item a_item  INNER JOIN auction a ON a_item.auction_id=a.id INNER JOIN event e ON e.id=a_item.event_id  where a_item.status!=4 and a_item.RMB_price>0 and a_item.auction_id ='"+a_auction_id+"' and a_item.event_id='"+a_special_id+"' ) a inner join (select lot_id,REPLACE(REPLACE(transaction_price,'HKD',''),',','') as rmb from crawler_lot where transaction_price != '--' and auction_id='"+b_auction_id+"' and special_id='"+b_special_id+"' ) b on a.lot=b.lot_id where a.rmb!= b.rmb"
        return self.query(sql)
    def updateRMB(self,lot,a_auction_id, a_special_id,rmb):
        sql = "update auction_item set RMB_price='"+rmb+"' where lot ='" + lot + "' and auction_id ='" + a_auction_id + "' and event_id='" + a_special_id + "'"
        self.updata(sql)
    def updateHKD(self,lot,a_auction_id, a_special_id,rmb):
        sql = "update auction_item set HKD_price='"+rmb+"' where lot ='" + lot + "' and auction_id ='" + a_auction_id + "' and event_id='" + a_special_id + "'"
        self.updata(sql)
    def updateEvent(self,lot_total,turnover_rate,total_rmb_w,auction_id,event_id):
        sql = "update event set lot_total='"+lot_total+"' , turnover_rate='"+turnover_rate+"',total_rmb_w='"+total_rmb_w+"' where auction_id ='"+auction_id+"' and id='"+event_id+"'"
        self.updata(sql)

    def insertAuction_item(self,lot,a_auction_id,a_special_id,b_auction_id,b_special_id):
        selectSql = "select lot_name,REPLACE(REPLACE(transaction_price,'RMB',''),',','') from crawler_lot where auction_id='"+b_auction_id+"' and special_id='"+b_special_id+"' and lot_id='"+lot+"'"
        results = self.query(selectSql)

        selectSql1 = "select code from event where id='" + a_special_id + "'"
        results1 = self.query(selectSql1)
        for res1 in results1:
            code = "pp" + res1[0][2:-1]

            selectLotSql = "select lot,name,RMB_price,status from auction_item where auction_id='" + a_auction_id + "' and event_id='" + a_special_id + "' and lot='" + lot + "'"
            results2 = self.query(selectLotSql)

            for res in results:
                time = str(round(Time.time(), 0))
                name = res[0]
                rmb = ""
                # status 0新增 1 预展 2历史 3拍卖 4 废弃
                # dealStatus  0：撤拍 1：成交，2：流拍，3：未提供成交价
                code += lot
                print "名称:", res[0]
                print "RMB:", res[1]
                print "results2",len(results2)
                if len(results2) > 0:
                    print "update"

                    print "lot",results2[0][0]
                    print "name",results2[0][1]
                    print "RMB_price",results2[0][2]
                    print "status",results2[0][3]
                    if str(res[1]) == "--":
                        sql = "update auction_item set RMB_price='0',status='2' ,deal_status='0' where auction_id='" + a_auction_id + "' and event_id='" + a_special_id + "' and lot='" + lot + "'"
                    elif str(res[1]) =="流拍":
                        sql = "update auction_item set RMB_price='0'  , status='2' ,deal_status='2'  where auction_id='" + a_auction_id + "' and event_id='" + a_special_id + "' and lot='" + lot + "'"
                    else:
                        rmb = str(res[1])
                        sql = "update auction_item set RMB_price='" + rmb + "'  , status='3' ,deal_status='1'  where auction_id='" + a_auction_id + "' and event_id='" + a_special_id + "' and lot='" + lot + "'"
                else:
                    print "INSERT INTO"
                    if str(res[1]) == "--":

                        sql = "INSERT INTO auction_item(auction_id,event_id,lot,name,remark,status,version,create_time,rmb_version,img_version,code,deal_status) " \
                                   "values('" + a_auction_id + "','" + a_special_id + "','" + lot + "','" + name + "','2','2','" + time + "','" + time + "','" + time + "','" + time + "','" + code + "','0')"
                    elif res[1] == "流拍":
                        sql = "INSERT INTO auction_item(auction_id,event_id,lot,name,RMB_price,remark,status,version,create_time,rmb_version,img_version,code,deal_status) " \
                              "values('" + a_auction_id + "','" + a_special_id + "','" + lot + "','" + name + "','0','2','2','" + time + "','" + time + "','" + time + "','" + time + "','" + code + "','2')"
                    else:
                        rmb = str(res[1])
                        sql = "INSERT INTO auction_item(auction_id,event_id,lot,name,RMB_price,remark,status,version,create_time,rmb_version,img_version,code,deal_status) " \
                                   "values('" + a_auction_id + "','" + a_special_id + "','" + lot + "','" + name + "','" + rmb + "','2','2','" + time + "','" + time + "','" + time + "','" + time + "','" + code + "','1')"


                self.updata(sql)

    def insertAuction_item_HKD(self, lot, a_auction_id, a_special_id, b_auction_id, b_special_id):
        selectSql = "select lot_name,REPLACE(REPLACE(transaction_price,'HKD',''),',','') from crawler_lot where auction_id='" + b_auction_id + "' and special_id='" + b_special_id + "' and lot_id='" + lot + "'"
        results = self.query(selectSql)

        selectSql1 = "select code from event where id='"+a_special_id+"'"
        results1 = self.query(selectSql1)
        for res1 in results1:
            code = "pp"+res1[0][2:-1]

            selectLotSql = "select * from auction_item where auction_id='" + a_auction_id + "' and event_id='" + a_special_id + "' and lot='" + lot + "'"
            results2 = self.query(selectLotSql)

            for res in results:
                time = str(round(Time.time(),0))
                name = res[0]
                rmb=""
                # status 0新增 1 预展 2历史 3拍卖 4 废弃
                # dealStatus  0：撤拍 1：成交，2：流拍，3：未提供成交价

                code += lot
                print "名称:",res[0]
                print "HKD:",str(res[1])
                print "results2", len(results2)
                if len(results2) > 0:
                    if str(res[1]) == "--":
                        sql = "update auction_item set status='2' ,deal_status='0' where auction_id='" + a_auction_id + "' and event_id='" + a_special_id + "' and lot='" + lot + "'"
                    elif str(res[1]) == "流拍":
                        sql = "update auction_item set HKD_price='0'  , status='2' ,deal_status='2' where auction_id='" + a_auction_id + "' and event_id='" + a_special_id + "' and lot='" + lot + "'"

                    else:
                        hkd = str(res[1])
                        sql = "update auction_item set HKD_price='" + hkd + "'  , status='3' ,deal_status='1'  where auction_id='" + a_auction_id + "' and event_id='" + a_special_id + "' and lot='" + lot + "'"
                else:
                    if str(res[1]) == "--":
                        sql = "INSERT INTO auction_item(auction_id,event_id,lot,name,remark,status,version,create_time,rmb_version,img_version,code,deal_status) " \
                                   "values('" + a_auction_id + "','" + a_special_id + "','" + lot + "','" + name + "','2','2','" + time + "','" + time + "','" + time + "','" + time + "','" + code + "','0')"
                    elif str(res[1]) == "流拍":
                        sql = "INSERT INTO auction_item(auction_id,event_id,lot,name,HKD_price,remark,status,version,create_time,rmb_version,img_version,code,deal_status) " \
                              "values('" + a_auction_id + "','" + a_special_id + "','" + lot + "','" + name + "','0','2','2','" + time + "','" + time + "','" + time + "','" + time + "','" + code + "','2')"
                    else:
                        hkd = str(res[1])
                        sql = "INSERT INTO auction_item(auction_id,event_id,lot,name,HKD_price,remark,status,version,create_time,rmb_version,img_version,code,deal_status) " \
                                   "values('" + a_auction_id + "','" + a_special_id + "','" + lot + "','" + name + "','" + hkd + "','2','3','" + time + "','" + time + "','" + time + "','" + time + "','" + code + "','1')"

                self.updata(inserSql)
    def closeConnect(self):
        # 关闭数据库连接
        self.__conn.close()
        print "连接关闭"

    def open_excel(self):
        try:
            data = xlrd.open_workbook('data.xlsx')
            return data
        except Exception, e:
            print str(e)
#
class Comparison:

    #查询 专场信息
    def step1(self,listA,listB):
        #getcontext().prec = 4  # 设置精度
        str1="   |   "

        mysql=MysqlTool()
        mysql.connect()

        for k in range(0,len(listA)):
            log='拍卖会 A:'+listA[k]['auction_id']+"   B:"+listB[k]['auction_id']+str1
            log+='专场 A:'+listA[k]['special_id']+"   B:"+listB[k]['special_id']+str1
            # 查询 拍品总数 #################################################################
            listA[k]['lot_Total'] = mysql.sumLotA(listA[k]['auction_id'], listA[k]['special_id'])
            lot_Total_A = listA[k]['lot_Total']
            log += '拍品总数 A:' + str(listA[k]['lot_Total'])

            listB[k]['lot_Total'] = mysql.sumLotB(listB[k]['auction_id'], listB[k]['special_id'])
            lot_Total_B = listB[k]['lot_Total']
            log += '    B:' + str(listB[k]['lot_Total']) + str1
            #################################################################

            #记录分析结果 相等改为0
            a=4
            b=4
            c=4

            # 查询 成交总数 与 成交额 #################################################################

            #保利 成交总数
            listA[k]['turnover_number'] = mysql.sumNumberA(listA[k]['auction_id'], listA[k]['special_id'])
            turnover_number_A = listA[k]['turnover_number']
            #保利 成交额
            listA[k]['turnover'] = mysql.sumPriceA(listA[k]['auction_id'], listA[k]['special_id'])
            turnover_A = round(Decimal(listA[k]['turnover'])/10000,3)

            #雅昌 成交总数
            listB[k]['turnover_number'] = mysql.sumNumberB(listB[k]['auction_id'], listB[k]['special_id'])
            turnover_number_B = listB[k]['turnover_number']
            #雅昌 成交额
            listB[k]['turnover'] = mysql.sumPriceB(listB[k]['auction_id'], listB[k]['special_id'])
            turnover_B = round(Decimal(listB[k]['turnover'])/10000,3)

            log += "成交总数 A:" + str(turnover_number_A) + "    B:" + str(turnover_number_B)

            log += str1 + "成交总额 A:" + str(turnover_A) + "    B:" + str(turnover_B)
            #################################################################


            log +=str1+ "拍品总数分析"
            # 拍品总数 #############################################
            if lot_Total_A > lot_Total_B:
                a = 1
                log += str1 + "拍品总数 A>B" + str1

                results = mysql.findAMoreThanB(listA[k]['auction_id'], listA[k]['special_id'],
                                               listB[k]['auction_id'], listB[k]['special_id'])

                log += "更新auction_item表 STATUS字段为4 拍卖会id:" + str(listA[k]['auction_id']) + " 专场id:" + str(
                    listA[k]['special_id']) + " LOT号:"

                for res in results:
                    log += str(res[0].encode('utf-8')) + " "
                    mysql.updateALot(res[0], listA[k]['auction_id'], listA[k]['special_id'])
                log +=str1
            elif lot_Total_A < lot_Total_B:
                a = 2
                log += str1 + "拍品总数 A<B" + str1
                log += "自动添加缺失拍品" + str1
                #查找缺失拍品LOT号

                results = mysql.findALessThanB(listA[k]['auction_id'], listA[k]['special_id'],
                                                listB[k]['auction_id'], listB[k]['special_id'])



                log += "缺失拍品LOT:"

                for res in results:
                    log += str(res[1]) + " "
                    #澳门 改为false
                    if RMB:
                        mysql.insertAuction_item(str(res[1]), listA[k]['auction_id'], listA[k]['special_id'],
                                                 listB[k]['auction_id'], listB[k]['special_id'])
                    else:
                        mysql.insertAuction_item_HKD(str(res[1]), listA[k]['auction_id'], listA[k]['special_id'],
                                                 listB[k]['auction_id'], listB[k]['special_id'])



                log += str1
            else:
                a=0
                log +=str1 + "拍品总数 A==B" + str1
            #############################################

            log += "成交拍品总数分析"
            # 成交拍品总数 #############################################
            if turnover_number_A>turnover_number_B:
                b = 1
                log += "成交拍品总数 A>B"+ str1
                log += "更改多余成交拍品" + str1
                results = mysql.findAMoreThanB_turnoverNumber(listA[k]['auction_id'], listA[k]['special_id'],
                                                              listB[k]['auction_id'],listB[k]['special_id'])

                log += "更新auction_item表 STATUS字段为4 拍卖会id:" + str(listA[k]['auction_id']) + " 专场id:" + str(listA[k]['special_id']) + " LOT号:"

                for res in results:
                    log += str(res[0]) + " "
                    mysql.updateALot(res[0], listA[k]['auction_id'], listA[k]['special_id'])
                log += str1
            elif turnover_number_A<turnover_number_B:
                b = 2
                log += "成交拍品总数 A<B"+ str1
                log += "自动添加缺失成交拍品" + str1
                # 查找缺失成交拍品LOT号
                results = mysql.findALessThanB_turnoverNumber(listA[k]['auction_id'], listA[k]['special_id'],
                                                             listB[k]['auction_id'],listB[k]['special_id'])
                log +="缺失成交拍品LOT:"
                for res in results:
                    log += str(res[1]) + " "
                    # 澳门 改为false
                    if RMB:
                        mysql.insertAuction_item(str(res[1]), listA[k]['auction_id'], listA[k]['special_id'],
                                             listB[k]['auction_id'], listB[k]['special_id'])
                    else:
                        mysql.insertAuction_item_HKD(str(res[1]), listA[k]['auction_id'], listA[k]['special_id'],
                                             listB[k]['auction_id'], listB[k]['special_id'])

                log +=  str1
            else:
                b=0
                log += str1 + "成交拍品总数 A==B" + str1
            #############################################

            log += "成交总额分析" + str1
            # 成交总额 #############################################
            if turnover_A != turnover_B:
                c = 1
                if turnover_A > turnover_B:
                    log += "成交总额 A>B" + str1
                elif turnover_A < turnover_B:
                    log += "成交总额 A<B" + str1
                # 澳门 改为false
                if RMB:
                    # 找出交易价格不相等拍品
                    results = mysql.unequalRMB(listA[k]['auction_id'], listA[k]['special_id'],
                                               listB[k]['auction_id'], listB[k]['special_id'])
                else:
                    # 找出交易价格不相等拍品
                    results = mysql.unequalHKD(listA[k]['auction_id'], listA[k]['special_id'],
                                               listB[k]['auction_id'], listB[k]['special_id'])





                log += "成交拍品成交价不相等LOT:"
                for res in results:
                    log += str(res[0]) + " "
                    log += str1
                    #更新交易价格
                    # 澳门 改为false
                    if RMB:
                        mysql.updateRMB(str(res[0]), listA[k]['auction_id'], listA[k]['special_id'], str(res[3]))
                    else:
                        mysql.updateHKD(str(res[0]), listA[k]['auction_id'], listA[k]['special_id'], str(res[3]))


            else:
                c=0
                log += "成交总额 A==B" + str1
            #############################################
            # if c!=0 or b!=0 or a!=0:
            log +="更新event表"+ str1
            if lot_Total_B==0:
                lot_Total_B=1
            log +="总数："+str(lot_Total_B)+" 成交数："+str(turnover_number_B)+" 成交率："+str(round(Decimal(turnover_number_B)/Decimal(lot_Total_B)*100,2))
            mysql.updateEvent(str(lot_Total_B),str(turnover_number_B/lot_Total_B*100),str(turnover_B),listA[k]['auction_id'], listA[k]['special_id'])
            print log
            mysql.contrast_log(listA[k]['auction_id'], listA[k]['special_id'], log,
                                listB[k]['auction_id'], listB[k]['special_id'], log,a,b,c)



        mysql.closeConnect()



if __name__ == '__main__':

    #组装数据

    #保利
    listA = []

    # 雅昌
    listB = []

    t=MysqlTool()
    data = t.open_excel()
    table = data.sheets()[0]
    nrows = table.nrows  # 行数
    for row in range(0,nrows):
        cell_A1 = str(int(table.cell(row, 0).value))
        cell_B1 = str(int(table.cell(row, 1).value))
        cell_C1 = table.cell(row, 2).value
        cell_D1 = str(table.cell(row, 3).value)
        cell_E1 = str(table.cell(row, 4).value)
        cell_F1 = table.cell(row, 5).value

        special_A = {'special_id': cell_B1, 'auction_id': cell_A1}
        listA.append(special_A)
        special_B = {'special_id': cell_E1, 'auction_id': cell_D1}
        listB.append(special_B)

    comparison=Comparison()
    comparison.step1(listA,listB)
