#-*- codeing = utf-8 -*-
#@Author:xiaohitu(201701050105冯帆涛)
#@Time:2020/7/1919:22
#@File:NBAPlayer.py
#@software:PyCharm
import bs4
import re
import urllib.request,urllib.error
import xlwt
import sqlite3
import socket
import time
import json

def main():     #主程序
    print("开始爬取.....")
    year=2010  #起始年份
    baseurl='https://china.nba.com/static/data/league/playerstats_All_All_All_0_All_false_2018_2_All_Team_points_All_perGame.json'
    #获得数据
    NBAPlayerdatadict=getdata(baseurl,year)
    #所需信息的抬头列表
    cols_index2 = ['displayName',"code", 'position', 'name',"code",'games',
                   'points', 'pointsPg', 'rebsPg', 'assistsPg',
                   'minsPg', 'fgpct', 'tppct', 'ftpct', 'blocksPg',
                   'foulsPg', 'height', 'weight'
                   ]
    cols_index1 = ['playerProfile','playerProfile', 'playerProfile', 'teamProfile',
                   'teamProfile',  'statAverage',
                   'statTotal', 'statAverage', 'statAverage', 'statAverage',
                   'statAverage', 'statAverage', 'statAverage', 'statAverage',
                   'statAverage', 'statAverage', 'playerProfile', 'playerProfile'
                   ]
    #保存数据
    savepath='.//'+str(year)+'年-2020年NBA球员数据排行TOP50.xls'
    savedata(NBAPlayerdatadict,savepath,year,cols_index1,cols_index2)
    #数据库位置
    dbpath='.//NBA球员数据库.db'
    #将数据保存到数据库
    saveDB(NBAPlayerdatadict,dbpath,year,cols_index1,cols_index2)
    print('成功爬取并保存数据!')
def getdata(baseurl,year):    #爬取网页获得需要的数据
    Playerdatadict={}
    for i in range(year,2020):
        #创建模式匹配更换url获取不同年份的data
        pattern_date = re.compile(r'(_\d*?_\d)', re.S)
        newbaseurl = re.sub(pattern_date, '_'+str(i)+'_2', baseurl)
        html=askUrl(newbaseurl)
        # 将html中的文件进行json解析得到Playerdata字典
        Playerdata=json.loads(html)
        # 将Playerdata放大字典中并带上年份
        Playerdatadict.setdefault(str(i)+"年", {}).update(Playerdata)
        time.sleep(0.05)  # 设置爬虫间隔
    print('成功获取数据!')
    return Playerdatadict
def savedata(Playerdatadict,savepath,year,cols_index1,cols_index2):    #保存数据到Excel
    cols=['排名','球员','球员链接','位置','球队','球队链接',
          '出场数','赛季得分','场均得分','场均篮板',
          '场均助攻','分钟','命中率','三分命中率(%)',
          '罚球命中率','场均盖帽','场均失误','身高(m)','体重']
    workbook = xlwt.Workbook(encoding='UTF-8')  # 创建workbook
    for i in range(year, 2020):
        worksheet = workbook.add_sheet(str(i) + '年')  # 创建工作表
        for j in range(len(cols)):
            worksheet.write(0,j,cols[j])
        for k in range(len(Playerdatadict[str(i) + '年']['payload']['players'])):
            worksheet.write(k + 1, 0, k + 1)
            for n in range(len(cols_index1)):
                p_link = r'https://china.nba.com/players/#!/'
                t_link = r'https://china.nba.com/'
                # 从Playerdatadict将有效信息取出来
                Playerdatadict_info = Playerdatadict[str(i) + "年"]['payload']['players'][k][cols_index1[n]][
                    cols_index2[n]]
                if n != 1 and n != 4:
                    worksheet.write(k + 1, n + 1, Playerdatadict_info)
                elif n == 1:  # 球员链接+str(link)
                    worksheet.write(k + 1, n + 1, p_link + Playerdatadict_info)
                else:
                    worksheet.write(k + 1, n + 1, t_link + Playerdatadict_info)
    workbook.save(savepath)
    print('保存数据成功!')
def askUrl(url):      #获得请求得到一个html(字符串的形式)
    headers={     #伪装身份信息
        'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 80.03987.122Safari / 537.36'
    }
    request = urllib.request.Request(url,headers=headers)
    html=''
    try:
        response=urllib.request.urlopen(request) #提交
        html=response.read().decode('UTF-8')
        print("成功爬取到html!")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        if isinstance(e.reason, socket.timeout):
            print('time out!')
    return html
def saveDB(Playerdatadict,dbpath,year,cols_index1,cols_index2):      #保存数据到数据库
    for i in range(year, 2020):
        #表的名称
        tablename="球员数据"+str(i)+'年'
        #初始化数据库
        initDB(tablename,dbpath)
        con=sqlite3.connect(dbpath)
        c=con.cursor()
        #Playerdatadict_info为从Playerdatadict字典里面提取到的有用信息
        Playerdatadict_info = Playerdatadict[str(i) + "年"]['payload']['players']
        for j in range(len(Playerdatadict_info)):   #球员信息个数len(Playerdatadict_info)
            data_need = []  # 每一行所需信息
            for k in range(len(cols_index1)):
                # 从Playerdatadict将有效信息取出来
                info = Playerdatadict_info[j][cols_index1[k]][cols_index2[k]]
                p_link = r'https://china.nba.com/players/#!/'
                t_link = r'https://china.nba.com/'
                if k!= 1 and k!= 4:
                    data_need.append(str(info))
                elif k==1:
                    data_need.append(p_link+str(info))
                else:
                    data_need.append(t_link + str(info))
            for index in range(len(data_need)):
                data_need[index] = '"' + data_need[index] + '"'
            sql = '''
                        insert into '''+str(tablename)+'''(
                        name,name_link,position,teamname,team_link,games,points,averpoints,averrebound,averassist,minutes,fgpct,tppct,ftpct,averblocks,averfouls,height,weight)
                        values (%s)'''%(",".join(data_need))
            c.execute(sql)
            con.commit()
        c.close()
        con.close()
    initDB(str(year)+'',dbpath)
    print('数据成功保存到数据库!')
def initDB(tablename,dbpath):
    sql = '''
         create table ''' + str(tablename) + '''(
         ranking  integer primary key autoincrement,
         name    text,
         name_link text,
         position text,
         teamname text,
         team_link text,
         games   integer ,
         points  integer ,
         averpoints integer ,
         averrebound integer,
         averassist  integer ,
         minutes    integer ,
         fgpct      integer,
         tppct      integer,
         ftpct     integer ,
         averblocks integer ,
         averfouls  integer,
         height  integer,
         weight  text
         );
        '''
    con = sqlite3.connect(dbpath)  # 连接数据库
    c = con.cursor()  # 创建游标
    c.execute(sql)
    con.commit()
    c.close()
    con.close()
    print('表' + str(tablename) + "创建成功!")
if __name__ == '__main__':
    main()