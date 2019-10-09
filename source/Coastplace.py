import zipfile
import os.path
import requests
import os
from lxml import etree
import json
import HazapModules
import requests


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
    for i in range(1,):
        pos2.lat=float(placelist[str(i)].split(" ")[0])
        pos2.lon=float(placelist[str(i)].split(" ")[1])
        dis=HazapModules.Calculatedistance(pos,pos2)
        if(mindis>dis):
            mindis=dis
            index=i
    if(evacuFlag):
        return index 
    returnlist={}#最終的に書き出すjsonのやつ
    #この時点で現在地から一番近い座標のインデックスが判明してるからそれをもとに一番近い海岸線の座標を+-60方向に探索
    count=0
    sublist={}
    sublist[str(asize)]=placelist[str(index)]
    for i in range(2*asize+1):
        if i==index:
            continue
    searchedlist=[False for i in range(len(placelist))]
    Reclist(placelist,sublist,asize-1,asize,searchedlist)
    Reclist(placelist,sublist,asize+1,asize,searchedlist)
#    for i in range(max(0,index-asize),min(index+asize+1,len(placelist))):
#        returnlist[str(count)]=placelist[str(i)]
#        count+=1    
    for i in range(len(sublist)):
        returnlist[str(i)]=sublist[str(i)]
    sorted(returnlist.items(), key=lambda x: x[0])
    with open("../data/squeezed.json","w") as f:
        json.dump(returnlist,f,ensure_ascii=False,indent=4)
    with open("../../log.json","w") as f:
        json.dump(searchedlist,f,ensure_ascii=False,indent=4)


def Reclist(placelist,returnlist,nowindex,asize,searchedlist):#一番近いところを全探索して書き込んでいく関数
    #returnlist[str(asize)]=placelist[str(index)]
    print("nowindex",nowindex,"asize",asize)
    if nowindex>asize:
        pos1=HazapModules.Coordinates()
        pos1.lat=float(returnlist[str(nowindex-1)].split(" ")[0])
        pos1.lon=float(returnlist[str(nowindex-1)].split(" ")[1])
        pos2=HazapModules.Coordinates()
        pos2.lat=float(placelist["0"].split(" ")[0])
        pos2.lon=float(placelist["0"].split(" ")[1])
        mindis=HazapModules.Calculatedistance(pos1,pos2)
        minindex=0
        for i in range(1,len(placelist)-1):
            pos2=HazapModules.Coordinates()
            pos2.lat=float(placelist[str(i)].split(" ")[0])
            pos2.lon=float(placelist[str(i)].split(" ")[1])
            distance=HazapModules.Calculatedistance(pos1,pos2)
            if distance<10:
                continue
            elif mindis>distance and searchedlist[i]==False:
                mindis=distance
                minindex=i
        returnlist[str(nowindex)]=placelist[str(minindex)]
        searchedlist[minindex]=True
        if asize*2==nowindex:
            return 0
        return Reclist(placelist,returnlist,nowindex+1,asize,searchedlist)
    else:
        pos1=HazapModules.Coordinates()
        pos1.lat=float(returnlist[str(nowindex+1)].split(" ")[0])
        pos1.lon=float(returnlist[str(nowindex+1)].split(" ")[1])
        pos2=HazapModules.Coordinates()
        pos2.lat=float(placelist["0"].split(" ")[0])
        pos2.lon=float(placelist["0"].split(" ")[1])
        mindis=HazapModules.Calculatedistance(pos1,pos2)
        minindex=0
        for i in range(1,len(placelist)-1):
            pos2=HazapModules.Coordinates()
            pos2.lat=float(placelist[str(i)].split(" ")[0])
            pos2.lon=float(placelist[str(i)].split(" ")[1])
            distance=HazapModules.Calculatedistance(pos1,pos2)
            if distance<10:
                continue
            elif mindis>distance and searchedlist[i]==False:
                mindis=distance
                minindex=i
        returnlist[str(nowindex)]=placelist[str(minindex)]
        searchedlist[minindex]=True
        if nowindex==0:
            return 0
        return Reclist(placelist,returnlist,nowindex-1,asize,searchedlist)

if __name__=="__main__":
    pos=HazapModules.Coordinates()
    pos.lat=32.03426306
    pos.lon=131.50147778
    pos1=HazapModules.Coordinates()
    pos1.lat=32.03412250
    pos1.lon=131.50141139
    print(HazapModules.Calculatedistance(pos,pos1))
    #Fullpos(pos,False)