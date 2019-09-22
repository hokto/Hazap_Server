import math
import socket
import requests
from lxml import etree
import json
import os.path
import zipfile
host = socket.gethostname()
addres = socket.gethostbyname(host)
r=6378100
print("servers ip is "+addres)
APIPubWord="appid=dj00aiZpPWNIMG5nZEpkSXk3OSZzPWNvbnN1bWVyc2VjcmV0Jng9ZDk-&output=json"
class Coordinates:#緯度、経度格納クラス
    lat=0.0
    lon=0.0
    

def TwoDimensionsSort(data,targetIdx,left,right):#二次元配列用ソート。引数にそれぞれ、ソートしたいデータのリスト、ソートする対象となるデータが入っている要素番号、リストの先頭、リストの末尾を入れる。
    i=left+1
    k=right
    while(i<k):
        while(float(data[i][targetIdx])<float(data[left][targetIdx]) and i<right):
            i+=1
        while(float(data[k][targetIdx])>=float(data[left][targetIdx]) and k>left):
            k-=1
        if(i<k):
            data[i],data[k]=data[k],data[i]
        if(float(data[left][targetIdx])>float(data[k][targetIdx])):
            data[left],data[k]=data[k],data[left]
        if(left<k-1):
            TwoDimensionsSort(data,targetIdx,left,k-1)
        if(k+1<right):
            TwoDimensionsSort(data,targetIdx,k+1,right)
    return data
def Calculatedistance(pos1,pos2):
    return math.sqrt((r*math.radians(abs(pos1.lon-pos2.lon)))**2+(r*math.radians(abs(pos1.lat-pos2.lat)))**2)
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
