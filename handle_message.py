from rasa_nlu.training_data import load_data
from rasa_nlu.model import Trainer
from rasa_nlu import config
import re
import random
import yfinance as yf
import time
import matplotlib.pyplot as plt
import pylab as pl
import sqlite3
import json
import spacy
import nltk

conn=sqlite3.connect("scrapy_dir/scrapy_dir/Database/stocks.db",check_same_thread = False)
cursor=conn.cursor()

nlp=spacy.load("en")

pattern = """handlable_intent:{<DT>(<JJ>|<JJS>)?<NN>}
             ORG:{<NN>{2,}|<NNP>+}"""  # org实体的词性组合
cp = nltk.RegexpParser(pattern)

trainer = Trainer(config.load("config_spacy.yml"))
training_data = load_data('intent_parse.json')
interpreter = trainer.train(training_data)

bot_name='financebot'

intent_responses = {
         "greet":[ "Hi",
                   "Hello",
                   "Howdy",
                   "Hi there"],
         'affirm': ["It's my pleasure to help you:)",
                    'So smart I am:)',
                    'Any other question then?',
                    ':)',
                    'Happy to have helped you:)'],
         'goodbye': ['Bye',
                     'Bye bye',
                     "Good Bye"],
         'name_query': ['My name is {}'.format(bot_name),
                        'They call me {}'.format(bot_name),
                        'You can call me {}'.format(bot_name)],
        }

pattern_list=["I'd like to know (.*)","Could you tell me (.*)","Could you please tell me (.*)","Do you know (.*)","I wonder (.*)","How about (.*)","What about (.*)","What's (.*)","What was (.*)"]

handlable_intent=['highest_price_query','lowest_price_query','price_query','open_price_query','close_price_query','volume_query']

start_date=None
end_date=None
period=None
intent=None
entities={}
org_list=[]
chat_id=None

paint_color=['r','y','','b','g']
dot_style=['-o','--o','-.o','-d','-.s']

def process2orglist(message):
    message= nltk.word_tokenize(message)  #先将消息进行分词
    message= nltk.pos_tag(message)  #消息贴标签
    cs = cp.parse(message)  #按指定正则式匹配公司名
    org_list = []
    handlable_intent_flag=False
    for item in cs:
        org = []
        if type(item) is not tuple:
            if item.label()=='handlable_intent':
                handlable_intent_flag=True
            else:
                for i in item:
                    org.append(i[0])
                org_name = ' '.join(org)
                org_list.append(org_name)
    return org_list,handlable_intent_flag

def format_returndata(data,photo):
    return {"data":data,"photo":photo}

def get_info(message):
    global intent
    data = interpreter.parse(message)
    it = data["intent"]["name"]  # 获取消息意图
    entities = data["entities"]  # 获取消息中的实体
    org_list=[]
    entity_dic={}  #存放消息实体的字典
    list,handlable_intent_flag=process2orglist(message)
    org_list.extend(list)
    stock_query_flag=True  #判断意图是否为股票名查询，针对语句只有股票名的查询语句
    for ent in entities:
        entity_dic[ent["entity"]]=str(ent["value"])
        stock_query_flag=False
    if it not in intent_responses:  #如果当前意图不为greet,affirm,goodbye或name_query时
        if intent in handlable_intent and handlable_intent_flag==False and stock_query_flag==True:  #如果意图不为可处理意图且股票查询意图为真，更新意图为股票名查询
            it='stock_query'
    return it,org_list,entity_dic


def formattime(t):
    array=time.strptime(t,"%Y-%m-%d %H:%M:%S")
    return time.strftime("%Y-%m-%d",array)

def find_mostsimilar(org):
    cursor.execute("select * from stocks")  # 最后找和名字相似度最近的股票
    results = cursor.fetchall()
    for o in org:
        max = 0
        stock_code = ''
        doc = nlp(o)
        for i in results:
            similarity = doc.similarity(nlp(i[1]))
            if similarity > max:
                max = similarity
                stock_code = i[0]
    return stock_code

def querydate(org,start_date,end_date,index):
    result = ''
    plt.cla()
    flag=None
    for seq, item in enumerate(org):
        date_list = []
        value_list = []
        cursor.execute("select code from stocks where name=?", (item,))  #先搜索名字
        stock_code = cursor.fetchall()
        if len(stock_code)!=0:
            stock_code=stock_code[0][0]
        else:
            cursor.execute("select code from stocks where code=?", (item,))  #再搜索代码
            stock_code = cursor.fetchall()
            if len(stock_code) != 0:
                stock_code = stock_code[0][0]
            else:
                stock_code=find_mostsimilar(org)
        result += item + ':\n'
        data = yf.download(stock_code, start=start_date, end=end_date)  #data为DataFrame类型
        flag=data.empty
        if flag:
            return format_returndata('Sorry,the stock market is CLOSED during the\nappointed period!\n','')
        else:
            if index=='Price':
                data_set = data['Close']  # data_set为Series类型
            else:
                data_set = data[index]  # data_set为Series类型
            data_len=len(data_set)
            result += 'Date               ' + index + '\n'
            for i in range(data_len):
                date=formattime(str(data_set.index[i]))   #date为str类型
                value='%.6f' % data_set.values[i]         #value为str类型
                result+=date+'   '+value+'\n'
                date_list.append(date)
                value=float(value)         #将value转为float类型，方便绘图
                value_list.append(value)
            plt.plot(date_list, value_list, paint_color[seq]+dot_style[seq],label=item)
        result+="\n"
    if flag==False:
        result+="And I'll draw you a graph to illustrate more clearly. "
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Quantity', fontsize=14)
        plt.legend(loc="best")
        pl.xticks(rotation=75)  # 逆时针旋转
        now_time = str(int(time.time()))  # 获取当前时间的时间戳并转换为字符串形式
        plt.savefig("static/pictures/" + now_time + '.png', dpi=200, bbox_inches='tight')
        return format_returndata(result, now_time)
    return format_returndata(result, '')

def queryperiod(org,period,index):
    result = ''
    plt.cla()
    flag=None
    for seq, item in enumerate(org):
        date_list = []
        value_list = []
        cursor.execute("select code from stocks where name=?", (item,))  #先搜索名字
        stock_code = cursor.fetchall()
        if len(stock_code)!=0:
            stock_code=stock_code[0][0]
        else:
            cursor.execute("select code from stocks where code=?", (item,))  #再搜索代码
            stock_code = cursor.fetchall()
            if len(stock_code) != 0:
                stock_code = stock_code[0][0]
            else:
                stock_code=find_mostsimilar(org)
        result += item + ':\n'
        data = yf.download(stock_code, period=period)  # data为DataFrame类型
        flag=data.empty
        if flag:
            return format_returndata('Sorry,the stock market is CLOSED during the\nappointed period!\n', '')
        else:
            if index=='Price':
                data_set = data['Close']  # data_set为Series类型
            else:
                data_set = data[index]  # data_set为Series类型
            data_len=len(data_set)
            result += 'Date               ' + index + '\n'
            for i in range(data_len):
                date = formattime(str(data_set.index[i]))  # date为str类型
                value = '%.6f' % data_set.values[i]  # value为str类型
                result += date + '   ' + value + '\n'
                date_list.append(date)
                value = float(value)  # 将value转为float类型，方便绘图
                value_list.append(value)
            plt.plot(date_list, value_list, paint_color[seq] + dot_style[seq], label=item)
        result += "\n"
    if flag == False:
        result += "And I'll draw you a graph to illustrate more clearly. "
        plt.xlabel('Date', fontsize=14)
        plt.ylabel('Quantity', fontsize=14)
        plt.legend(loc="best")
        pl.xticks(rotation=75)
        now_time = str(int(time.time()))  # 获取当前时间的时间戳并转换为字符串形式
        plt.savefig("static/pictures/" + now_time + '.png', dpi=200, bbox_inches='tight')
        return format_returndata(result, now_time)
    return format_returndata(result, '')

def highest_price_query(org, start_date, end_date, period):
    if start_date!=None:
        return querydate(org,start_date,end_date,'High')
    else:
        return queryperiod(org,period,'High')

def lowest_price_query(org, start_date, end_date, period):
    if start_date != None:
        return querydate(org, start_date, end_date, 'Low')
    else:
        return queryperiod(org,period,'Low')

def price_query(org,start_date,end_date, period):
    if start_date != None:
        return querydate(org, start_date, end_date, 'Price')
    else:
        return queryperiod(org,period,'Price')

def open_price_query(org,start_date,end_date, period):
    if start_date != None:
        return querydate(org, start_date, end_date, 'Open')
    else:
        return queryperiod(org,period,'Open')

def close_price_query(org,start_date,end_date, period):
    if start_date != None:
        return querydate(org, start_date, end_date, 'Close')
    else:
        return queryperiod(org,period,'Close')

def volume_query(org,start_date,end_date, period):
    if start_date != None:
        return querydate(org, start_date, end_date, 'Volume')
    else:
        return queryperiod(org,period,'Volume')

def formatdate(date):  #将日期加一天，根据yfinance.download()函数的start参数的性质来决定的
    beforeArray = time.strptime(date, "%Y-%m-%d")  # 转为时间数组
    timeStamp = int(time.mktime(beforeArray))  # 转为时间戳
    timeStamp+=24*60*60
    afterArray=time.localtime(timeStamp)
    return time.strftime("%Y-%m-%d", afterArray)

def handle(intent,org_list):
    global start_date
    global end_date
    global period
    global entities
    for key,value in entities.items():
        if key=='start_date':
            start_date=end_date=value
        elif key=='end_date':
            end_date=value
        elif key=='period':
            period=value
    #处理多轮对话
    if len(org_list)==0 and start_date==None and period==None:  #只有意图，没有实体
        return format_returndata("So which stock do you want to ask about?",'')
    elif len(org_list)==0 and (start_date!=None or period!=None):  #start_date和period二选一即可
        return format_returndata("So which stock do you want to ask about?",'')
    elif len(org_list)!=0 and (start_date==None and period==None):
        return format_returndata("Then for which period do you want to ask about?",'')
    else:
        if start_date!=None:
            start_date = start_date.replace(" ", "")  # 去掉日期空白符
            start_date = formatdate(start_date)
            end_date = end_date.replace(" ", "")
            end_date = formatdate(end_date)
        if intent == 'highest_price_query':
            return highest_price_query(org_list, start_date, end_date, period)
        elif intent == 'lowest_price_query':
            return lowest_price_query(org_list, start_date, end_date, period)
        elif intent == 'price_query':
            return price_query(org_list, start_date, end_date, period)
        elif intent == 'open_price_query':
            return open_price_query(org_list, start_date, end_date, period)
        elif intent == 'close_price_query':
            return close_price_query(org_list, start_date, end_date, period)
        elif intent == 'volume_query':
            return volume_query(org_list, start_date, end_date, period)

def handle_text(message):
    global intent
    global entities
    global org_list
    global start_date
    global end_date
    global chat_id
    global period
    for item in pattern_list:  #去掉不重要信息
        match=re.search(item,message,re.I)
        if match is not None:
            message=match.group(1)
            break
    cur_intent,cur_org_list,cur_entities=get_info(message)  #获取当前消息的意图和实体字典
    if cur_intent=='greet' or cur_intent=='affirm' or cur_intent=='goodbye' or cur_intent=='name_query':
        return format_returndata(random.choice(intent_responses[cur_intent]),'')
    else:
        if cur_intent in handlable_intent:  # 当前意图在可处理意图中时处理当前意图
            intent = cur_intent
            entities = cur_entities.copy()
            org_list = cur_org_list[:]
            start_date = None
            end_date = None
            period=None
        else:  # 当前意图不在可处理意图中时
            if intent in handlable_intent:
                if len(cur_org_list)!=0:  #如果重新问询公司名，则清除之前的公司名
                    org_list.clear()
                for item in cur_org_list:
                    org_list.append(item)
                for key, value in cur_entities.items():
                    if key=='period' or key=='start_date':
                        if 'period' in entities:  # 如果之前问询过时间段则清除记录，此处代码可以不必写，这是根据几个价格查询函数内部逻辑来的：先判断start_date是否为None
                            period = None
                            del entities['period']
                        if 'end_date' in entities:  # 如果前一轮有问询过起止时间则清除之前的记录
                            start_date = end_date = None
                            del entities['start_date']
                            del entities['end_date']
                    entities[key] = str(value)
            else:  # 不可识别意图，直接赋值
                intent = cur_intent
        print(intent, org_list,entities)
        return handle(intent, org_list)  # 处理消息意图和实体