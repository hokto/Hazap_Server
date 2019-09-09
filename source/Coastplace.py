import zipfile
import os.path
import requests
import os
from lxml import etree


def Coastplaces_get(interval):#海岸線取得用の関数
    url="http://nlftp.mlit.go.jp/ksj/api/1.0b/index.php/app/getKSJURL.xml?appId={key}&lang={lang}&dataformat=1&identifier=C23&prefCode={pref}&fiscalyear={year}"
    url=url.format(key="ksjapibeta1",lang="J",pref="45",year="2006")
    result=requests.get(url)
    tree=etree.fromstring(result.content)
    for i in tree.iter():
        if(i.tag=="zipFileUrl"):
            Download_zip(i.text)
    Xml_parse(interval)
    
def Xml_parse(interval):#xmlファイルをパースし、海岸線の座標を取得（座標は50m間隔）
    tree=etree.ElementTree(file="../data/C23-06_45-g.xml")
    xml=tree.getroot()
    coast_list=[]
    for Curve in xml:
        for segments in Curve:
            for LineStringSegment in segments:
                for coastplace in LineStringSegment:
                    coast_list=(coastplace.text.split("\n"))
                    coast_list.pop()
    pos_idx=0
    interval_idx=interval/50#50m間隔なので100mごとの座標は要素間では2要素間隔になる(100mは仮)
    while(pos_idx<len(coast_list)):
        print(coast_list[int(pos_idx)])
        pos_idx+=interval_idx
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
