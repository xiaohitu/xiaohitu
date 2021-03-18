from flask import Flask,render_template,request
import sqlite3,jieba
app = Flask(__name__)
@app.route('/')
def welcome():
    return  render_template('index.html')
@app.route('/index')
def index():
    return welcome()
@app.route('/top50')
def top50():
    datalist = []
    con = sqlite3.connect("NBA球员数据库.db")
    c = con.cursor()
    #设置当前页数
    page=int(request.args.get('page',1))
    year=int(page)+2009
    sql= '''
    select * from 球员数据'''+str(year)+'''年
    '''
    data=c.execute(sql)
    for item in data:
        datalist.append(item)
    c.close()
    con.close()
    # 设置总页码数
    pagemax = 10
    return render_template('top50.html',datalist=datalist,page=page,pagemax=pagemax)
@app.route('/cloud')
def cloud():
    return render_template('cloud.html')
@app.route('/chart')
def chart():
    datalist = []
    years=[]  #年份
    xx=[]#x坐标数据
    #存放球队的名称的列表
    team=[['76人'], ['公牛'], ['凯尔特人'], ['勇士'], ['国王'], ['太阳'], ['奇才'], ['小牛'], ['尼克斯'], ['开拓者'], ['快船'], ['掘金'], ['森林狼'], ['步行者'], ['活塞'], ['湖人'], ['火箭'], ['灰熊'], ['热火'], ['爵士'], ['猛龙'], ['篮网'], ['老鹰'], ['雄鹿'], ['雷霆'], ['马刺'], ['骑士'], ['魔术'], ['鹈鹕'], ['黄蜂']]
    #存放球队名称的字符串
    # 存放字符的字符串
    text = ''
    con = sqlite3.connect("NBA球员数据库.db")
    c = con.cursor()
    # 设置当前页数
    page = 1
    year = int(page) + 2009
    for i in range(year, 2020):
        data_peryear = []
        years.append(i)
        sql = '''
                    select * from 球员数据''' + str(i) + '''年
                    '''
        data = c.execute(sql)
        for item in data:
            data_peryear.append(item)
            #将球队名称练成字符串
            text += item[4]
        datalist.append(data_peryear)
    for index in range(10):
        xx.append(str(index+2010)+str(datalist[index][0][1]))
    c.close()
    con.close()
    #利用字符串统计球队名称出现的次数
    for i in range(len(team)):
        number=text.count(team[i][0])
        team[i].append(str(number))
    return render_template('chart.html',datalist=datalist,years=years,xx=xx,team=team)
@app.route('/team')
def team():
    return render_template('team.html')

if __name__ == '__main__':
    app.run(debug=True)
