#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from tornado import gen
import web.base as webBase
import logging

# 首映 bokeh 画图。
from bokeh.plotting import figure
from bokeh.embed import components
import datetime
import libs.common as common
import stockstats
import numpy as np
import pandas as pd
from bokeh.layouts import gridplot
from bokeh.palettes import Category20
from math import radians
from bokeh.models import DatetimeTickFormatter


# 获得页面数据。
class GetDataIndicatorsHandler(webBase.BaseHandler):
    @gen.coroutine
    def get(self):
        code = self.get_argument("code", default=None, strip=False)
        logging.info(code)
        # self.uri_ = ("self.request.url:", self.request.uri)
        # print self.uri_
        comp_list = []

        try:
            date_now = datetime.datetime.now()
            date_end = date_now.strftime("%Y-%m-%d")
            date_start = (date_now + datetime.timedelta(days=-300)).strftime("%Y-%m-%d")
            print(code, date_start, date_end)

            # open, high, close, low, volume, price_change, p_change, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover
            # 使用缓存方法。加快计算速度。
            stock = common.get_hist_data_cache(code, date_start, date_end)
            logging.info(stock.head(1))

            # print(stock) [186 rows x 14 columns]
            # 初始化统计类
            # stockStat = stockstats.StockDataFrame.retype(pd.read_csv("002032.csv"))
            stockStat = stockstats.StockDataFrame.retype(stock)
            batch_add(comp_list, stockStat)


        except Exception as e:
            logging.info("error :", e)
        logging.info("#################### GetStockHtmlHandlerEnd ####################")

        self.render("stock_indicators.html", comp_list=comp_list, leftMenu=webBase.GetLeftMenu(self.request.uri))


# 配置数据
indicators_dic = [
    {
        "title": "1，交易量delta指标分析",
        "desc": "The Volume Delta (Vol ∆) ",
        "dic": ["volume", "volume_delta"]
    }, {
        "title": "2，计算n天差",
        "desc": "可以计算，向前n天，和向后n天的差。",
        "dic": ["close", "close_1_d", "close_2_d", "close_-1_d", "close_-2_d"]
    }, {
        "title": "3，n天涨跌百分百计算",
        "desc": "可以看到，-n天数据和今天数据的百分比。",
        "dic": ["close", "close_-1_r", "close_-2_r"]
    }, {
        "title": "4，CR指标",
        "desc": """
            http://wiki.mbalib.com/wiki/CR%E6%8C%87%E6%A0%87 价格动量指标
            4. CR跌穿a、b、c、d四条线，再由低点向上爬升160时，为短线获利的一个良机，应适当卖出股票。
            5. CR跌至40以下时，是建仓良机。而CR高于300~400时，应注意适当减仓。
        """,
        "dic": ["close","cr","cr-ma1","cr-ma2","cr-ma3"]
    }, {
        "title": "5，最大值，最小值",
        "desc": """
            计算区间最大值
            volume max of three days ago, yesterday and two days later
            stock["volume_-3,2,-1_max"]
            volume min between 3 days ago and tomorrow
            stock["volume_-3~1_min"]
            实际使用的时候使用 -2~2 可计算出5天的最大，最小值。
        """,
        "dic": ["volume","volume_-2~2_max","volume_-2~2_min"]
    }, {
        "title": "5，KDJ指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E9%9A%8F%E6%9C%BA%E6%8C%87%E6%A0%87
            随机指标(KDJ)一般是根据统计学的原理，通过一个特定的周期（常为9日、9周等）内出现过的最高价、最低价及最后一个计算周期的收盘价及这三者之间的比例关系，来计算最后一个计算周期的未成熟随机值RSV，然后根据平滑移动平均线的方法来计算K值、D值与J值，并绘成曲线图来研判股票走势。
            （3）在使用中，常有J线的指标，即3乘以K值减2乘以D值（3K－2D＝J），其目的是求出K值与D值的最大乖离程度，以领先KD值找出底部和头部。J大于100时为超买，小于10时为超卖。
        """,
        "dic": ["close","kdjk","kdjd","kdjj"]
    }, {
        "title": "6，SMA指标",
        "desc": """
            http://wiki.mbalib.com/wiki/Sma
            简单移动平均线（Simple Moving Average，SMA）
            可以动态输入参数，获得几天的移动平均。
        """,
        "dic": ["close","close_5_sma","close_10_sma"]
    }, {
        "title": "7，MACD指标",
        "desc": """
            http://wiki.mbalib.com/wiki/MACD
            平滑异同移动平均线(Moving Average Convergence Divergence，简称MACD指标)，也称移动平均聚散指标
            MACD
            stock["macd"]
            MACD signal line
            stock["macds"]
            MACD histogram
            stock["macdh"]
            MACD技术分析，运用DIF线与MACD线之相交型态及直线棒高低点与背离现象，作为买卖讯号，尤其当市场股价走势呈一较为明确波段趋势时，
            MACD 则可发挥其应有的功能，但当市场呈牛皮盘整格局，股价不上不下时，MACD买卖讯号较不明显。
            当用MACD作分析时，亦可运用其他的技术分析指标如短期 K，D图形作为辅助工具，而且也可对买卖讯号作双重的确认。
        """,
        "dic": ["close","macd","macds","macdh"]
    }, {
        "title": "8，BOLL指标",
        "desc": """
        http://wiki.mbalib.com/wiki/BOLL
            布林线指标(Bollinger Bands)
            bolling, including upper band and lower band
            stock["boll"]
            stock["boll_ub"]
            stock["boll_lb"]
            1、当布林线开口向上后，只要股价K线始终运行在布林线的中轨上方的时候，说明股价一直处在一个中长期上升轨道之中，这是BOLL指标发出的持股待涨信号，如果TRIX指标也是发出持股信号时，这种信号更加准确。此时，投资者应坚决持股待涨。
            2、当布林线开口向下后，只要股价K线始终运行在布林线的中轨下方的时候，说明股价一直处在一个中长期下降轨道之中，这是BOLL指标发出的持币观望信号，如果TRIX指标也是发出持币信号时，这种信号更加准确。此时，投资者应坚决持币观望。
        """,
        "dic": ["close","boll","boll_ub","boll_lb"]
    }, {
        "title": "9，RSI指标",
        "desc": """
            http://wiki.mbalib.com/wiki/RSI
            相对强弱指标（Relative Strength Index，简称RSI），也称相对强弱指数、相对力度指数
            6 days RSI
            stock["rsi_6"]
            12 days RSI
            stock["rsi_12"]
            （2）强弱指标保持高于50表示为强势市场，反之低于50表示为弱势市场。
            （3）强弱指标多在70与30之间波动。当六日指标上升到达80时，表示股市已有超买现象，如果一旦继续上升，超过90以上时，则表示已到严重超买的警戒区，股价已形成头部，极可能在短期内反转回转。
            （4）当六日强弱指标下降至20时，表示股市有超卖现象，如果一旦继续下降至10以下时则表示已到严重超卖区域，股价极可能有止跌回升的机会。
        """,
        "dic": ["close","rsi_6","rsi_12"]
    }, {
        "title": "10，WR指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E5%A8%81%E5%BB%89%E6%8C%87%E6%A0%87
            威廉指数（Williams%Rate）该指数是利用摆动点来度量市场的超买超卖现象。
            10 days WR
            stock["wr_10"]
            6 days WR
            stock["wr_6"]
        """,
        "dic": ["close","wr_10","wr_6"]
    }, {
        "title": "11，CCI指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E9%A1%BA%E5%8A%BF%E6%8C%87%E6%A0%87
            顺势指标又叫CCI指标，其英文全称为“Commodity Channel Index”，
            是由美国股市分析家唐纳德·蓝伯特（Donald Lambert）所创造的，是一种重点研判股价偏离度的股市分析工具。
             CCI, default to 14 days
            stock["cci"]
             20 days CCI
            stock["cci_20"]
            1、当CCI指标从下向上突破﹢100线而进入非常态区间时，表明股价脱离常态而进入异常波动阶段，
              中短线应及时买入，如果有比较大的成交量配合，买入信号则更为可靠。
            2、当CCI指标从上向下突破﹣100线而进入另一个非常态区间时，表明股价的盘整阶段已经结束，
              将进入一个比较长的寻底过程，投资者应以持币观望为主。
        """,
        "dic": ["close","cci","cci_20"]
    }, {
        "title": "12，TR、ATR指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E5%9D%87%E5%B9%85%E6%8C%87%E6%A0%87
            均幅指标（Average True Ranger,ATR）
            均幅指标（ATR）是取一定时间周期内的股价波动幅度的移动平均值，主要用于研判买卖时机。
            TR (true range)
            stock["tr"]
             ATR (Average True Range)
            stock["atr"]
            均幅指标无论是从下向上穿越移动平均线，还是从上向下穿越移动平均线时，都是一种研判信号。
        """,
        "dic": ["close","tr","atr"]
    }, {
        "title": "13，DMA指标",
        "desc": """
            http://wiki.mbalib.com/wiki/DMA
            DMA指标（Different of Moving Average）又叫平行线差指标，是目前股市分析技术指标中的一种中短期指标，它常用于大盘指数和个股的研判。
            DMA, difference of 10 and 50 moving average
            stock["dma"]
        """,
        "dic": ["close","dma"]
    }, {
        "title": "14，DMI，+DI，-DI，DX，ADX，ADXR指标",
        "desc": """
            http://wiki.mbalib.com/wiki/DMI
            动向指数Directional Movement Index,DMI）
            http://wiki.mbalib.com/wiki/ADX
            平均趋向指标（Average Directional Indicator，简称ADX）
            http://wiki.mbalib.com/wiki/%E5%B9%B3%E5%9D%87%E6%96%B9%E5%90%91%E6%8C%87%E6%95%B0%E8%AF%84%E4%BC%B0
            平均方向指数评估（ADXR）实际是今日ADX与前面某一日的ADX的平均值。ADXR在高位与ADX同步下滑，可以增加对ADX已经调头的尽早确认。
            ADXR是ADX的附属产品，只能发出一种辅助和肯定的讯号，并非入市的指标，而只需同时配合动向指标(DMI)的趋势才可作出买卖策略。
            在应用时，应以ADX为主，ADXR为辅。
        """,
        "dic": ["close","pdi","mdi","dx","adx","adxr"]
    }, {
        "title": "15，TRIX，MATRIX指标",
        "desc": """
            http://wiki.mbalib.com/wiki/TRIX
            TRIX指标又叫三重指数平滑移动平均指标（Triple Exponentially Smoothed Average）
        """,
        "dic": ["close","trix","trix_9_sma"]
    }, {
        "title": "16，VR，MAVR指标",
        "desc": """
            http://wiki.mbalib.com/wiki/%E6%88%90%E4%BA%A4%E9%87%8F%E6%AF%94%E7%8E%87
            成交量比率（Volumn Ratio，VR）（简称VR），是一项通过分析股价上升日成交额（或成交量，下同）与股价下降日成交额比值，
            从而掌握市场买卖气势的中期技术指标。
             VR, default to 26 days
            stock["vr"]
             MAVR is the simple moving average of VR
            stock["vr_6_sma"]
        """,
        "dic": ["close","vr","vr_6_sma"]
    }
]


# 批量添加数据。
def batch_add(comp_list, stockStat):
    for conf in indicators_dic:
        logging.info(conf)

        comp_list.append(add_plot(stockStat, conf))


# 增加画图方法
def add_plot(stockStat, conf):
    p_list = []
    logging.info("############################", type(conf["dic"]))
    # 循环 多个line 信息。
    for key, val in enumerate(conf["dic"]):
        logging.info(key)
        logging.info(val)

        p1 = figure(width=1000, height=150, x_axis_type="datetime")
        # add renderers
        stockStat["date"] = pd.to_datetime(stockStat.index.values)
        # ["volume","volume_delta"]
        # 设置20个颜色循环，显示0 2 4 6 号序列。
        p1.line(stockStat["date"], stockStat[val], color=Category20[20][key * 2])

        # Set date format for x axis 格式化。
        p1.xaxis.formatter = DatetimeTickFormatter(
            hours=["%Y-%m-%d"], days=["%Y-%m-%d"],
            months=["%Y-%m-%d"], years=["%Y-%m-%d"])
        # p1.xaxis.major_label_orientation = radians(30) #可以旋转一个角度。

        p_list.append([p1])

    gp = gridplot(p_list)
    script, div = components(gp)
    return {
        "script": script,
        "div": div,
        "title": conf["title"],
        "desc": conf["desc"]
    }
