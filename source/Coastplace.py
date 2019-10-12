import zipfile
import os.path
import requests
import os
from lxml import etree
import json
import HazapModules
import requests
import math

def Coastplaces_get(interval,prefCode):#海岸線取得用の関数
    url="http://nlftp.mlit.go.jp/ksj/api/1.0b/index.php/app/getKSJURL.xml?appId={key}&lang={lang}&dataformat=1&identifier=C23&prefCode={pref}&fiscalyear={year}"
    url=url.format(key="ksjapibeta1",lang="J",pref=prefCode,year="2006")
    result=requests.get(url)
    tree=etree.fromstring(result.content)
    for i in tree.iter():
        if(i.tag=="zipFileUrl"):
            HazapModules.Download_zip(i.text)
    coastDict=Xml_parse(interval,prefCode)
    with open("../data/coastplaces.json","w") as f:
        json.dump(coastDict,f,ensure_ascii=False,indent=4)

def Xml_parse(interval,prefCode):#xmlファイルをパースし、海岸線の座標を取得（座標は50m間隔）
    tree=etree.ElementTree(file="../data/C23-06_"+prefCode+"-g.xml")
    xml=tree.getroot()
    coast_list=[]
    counthoge=1
    for Curve in xml:
        flg=0
        for i in Curve.attrib:
            if(Curve.attrib[i]=="c_00001"):
                flg=1
        if flg==0:
            continue

        for segments in Curve:
            for LineStringSegment in segments:
                for coastplace in LineStringSegment:
                    counthoge+=1
                    coastplace.text.split("\n").pop()
                    coast_list+=coastplace.text.split("\n")
                    coast_list.pop()
    pos_idx=0
    interval_idx=interval/50#50m間隔なので100mごとの座標は要素間では2要素間隔になる
    i=0
    dict={}
    while(pos_idx<len(coast_list)):
        #print(coast_list[int(pos_idx)])
        dict[i]={}
        if(coast_list[int(pos_idx)]==""):
            pos_idx+=interval_idx
            continue
        dict[i]=coast_list[int(pos_idx)]
        pos_idx+=interval_idx
        i+=1
    return dict
def Fullpos(pos,evacuFlag):#pos:探索したい座標 evacuFlag:Carcuevaで使うかどうか（一番近いところまでの海岸線の距離を取得するため)
    asize=60
    placelist=json.load(open("../data/coastplaces.json",encoding="utf-8_sig"))#全ての座標が入っているリスト
    size=len(placelist)
    pos2=HazapModules.Coordinates()
    pos2.lat=float(placelist[str(0)].split(" ")[0])
    pos2.lon=float(placelist[str(0)].split(" ")[1])
    mindis=HazapModules.Calculatedistance(pos,pos2)
    index=0
    for i in range(1,size):
        pos2.lat=float(placelist[str(i)].split(" ")[0])
        pos2.lon=float(placelist[str(i)].split(" ")[1])
        dis=HazapModules.Calculatedistance(pos,pos2)
        if(mindis>dis):
            mindis=dis
            index=i

    print("Index:",index)
    if(evacuFlag):
        return index 
    returnlist={}#最終的に書き出すjsonのやつ
    count=0
    #searchedlist=[False for i in range(len(placelist))]
    #searchedlist[index]=True
    #sublist={}
    #sublist[str(asize)]=placelist[str(index)]
    #Reclist(placelist,sublist,asize-1,asize,searchedlist)
    #Reclist(placelist,sublist,asize+1,asize,searchedlist)
    #print(json.dumps(sublist,indent=2))
    #for i in range(len(sublist)):
    #    returnlist[str(i)]=sublist[str(i)]
    for i in range(max(index-asize,0),min(index+asize,size)):
        returnlist[str(count)]=placelist[str(i)]
        count+=1
    with open("../data/squeezed.json","w") as f:
        json.dump(returnlist,f,ensure_ascii=False,indent=4)


def Reclist(placelist,returnlist,nowindex,asize,searchedlist):#一番近いところを全探索して書き込んでいく関数
    print(nowindex,asize)
    if nowindex>asize:
        pos1=HazapModules.Coordinates()
        pos1.lat=float(returnlist[str(nowindex-1)].split(" ")[0])
        pos1.lon=float(returnlist[str(nowindex-1)].split(" ")[1])
        pos2=HazapModules.Coordinates()
        mindis=10000000
        minindex=0
        for i in range(len(placelist)):
            pos2.lat=float(placelist[str(i)].split(" ")[0])
            pos2.lon=float(placelist[str(i)].split(" ")[1])
            distance=HazapModules.Calculatedistance(pos1,pos2)
            if mindis>distance and searchedlist[i]==False and distance>10:
                mindis=distance
                minindex=i
        returnlist[str(nowindex)]=placelist[str(minindex)]
        searchedlist[minindex]=True
        if nowindex==asize*2:
            return 0
        return Reclist(placelist,returnlist,nowindex+1,asize,searchedlist)
    else:
        pos1=HazapModules.Coordinates()
        pos1.lat=float(returnlist[str(nowindex+1)].split(" ")[0])
        pos1.lon=float(returnlist[str(nowindex+1)].split(" ")[1])
        pos2=HazapModules.Coordinates()
        mindis=10000000
        minindex=0
        for i in range(len(placelist)):
            pos2.lat=float(placelist[str(i)].split(" ")[0])
            pos2.lon=float(placelist[str(i)].split(" ")[1])
            distance=HazapModules.Calculatedistance(pos1,pos2)
            if mindis>distance and searchedlist[i]==False and distance>10:
                mindis=distance
                minindex=i
        returnlist[str(nowindex)]=placelist[str(minindex)]
        searchedlist[minindex]=True
        if nowindex==0:
            return 0
        return Reclist(placelist,returnlist,nowindex-1,asize,searchedlist)

