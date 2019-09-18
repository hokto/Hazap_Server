import zipfile
import os.path
import requests
import os
from lxml import etree
import json
import HazapModules


def Coastplaces_get(interval):#海岸線取得用の関数
    url="http://nlftp.mlit.go.jp/ksj/api/1.0b/index.php/app/getKSJURL.xml?appId={key}&lang={lang}&dataformat=1&identifier=C23&prefCode={pref}&fiscalyear={year}"
    url=url.format(key="ksjapibeta1",lang="J",pref="45",year="2006")
    result=requests.get(url)
    tree=etree.fromstring(result.content)
    for i in tree.iter():
        if(i.tag=="zipFileUrl"):
            Download_zip(i.text)
    coastDict=Xml_parse(interval)
    with open("../data/coastplaces.json","w") as f:
        json.dump(coastDict,f,ensure_ascii=False,indent=4)

def Xml_parse(interval):#xmlファイルをパースし、海岸線の座標を取得（座標は50m間隔）
    tree=etree.ElementTree(file="../data/C23-06_45-g.xml")
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
def Download_zip(text):#zipファイルをダウンロードしてくる関数
    filename=text.split("/")[-1]
    result=requests.get(text)
    with open(filename,"wb")as f:
        for chunk in result.iter_content(chunk_size=1024):
            if(chunk):
                f.write(chunk)
                f.flush()
        Uncompress_zip(filename)
    os.remove(filename)#zipファイル削除

def Uncompress_zip(filename):#zipファイル解凍して指定したパスに保存する関数
    filepath="../data"
    zfile=zipfile.ZipFile(filename)
    zfile.extractall(filepath)

def Fullpos(pos):
    placelist=json.load(open("../data/coastplaces.json",encoding="utf-8_sig"))
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
    returnlist={}
    count=0
    for i in range(max(0,index-50),min(index+50,len(placelist))):
        returnlist[str(count)]=placelist[str(i)]
        count+=1
    with open("../data/squeezed.json","w") as f:
        json.dump(returnlist,f,ensure_ascii=False,indent=4)