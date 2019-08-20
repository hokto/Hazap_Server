import requests
import json
import urllib.request
import HazapModules
import math

def get_Coordinates(pos):
    #この関数は緯度,経度を投げればいい感じのを返してくれる
    sta = {
        "appid": "dj00aiZpPWlGdHd2QlFKTDZZWiZzPWNvbnN1bWVyc2VjcmV0Jng9ODg-", 
        "output":"&output=json"
        }
    redata=[]
    url="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+pos.lat+"&lon="+pos.lon+"&dist=2"+sta["output"]+"&gc=0425&sort=geo"
    url2="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+pos.lat+"&lon="+pos.lon+"&dist=2"+sta["output"]+"&gc=0423007&sort=geo"
    url3="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+pos.lat+"&lon="+pos.lon+"&dist=2"+sta["output"]+"&gc=0305007&sort=geo"
    res=urllib.request.urlopen(url)
    res2=urllib.request.urlopen(url2)
    res3=urllib.request.urlopen(url3)
    data=json.loads(res.read().decode())
    data2=json.loads(res2.read().decode())
    data3=json.loads(res3.read().decode())
    #この下の処理で座標をリストにまとめてreturn
    if(data["ResultInfo"]["Count"]!=0):
        for i in data["Feature"]:
            redata.append(i["Geometry"]["Coordinates"].split(','))
    if(data2["ResultInfo"]["Count"]!=0):
        for i in data2["Feature"]:
            redata.append(i["Geometry"]["Coordinates"].split(','))
    if(data3["ResultInfo"]["Count"]!=0):
        for i in data3["Feature"]:
            redata.append(i["Geometry"]["Coordinates"].split(','))


    for i in range(len(redata)):
        redata[i][0],redata[i][1]=redata[i][1],redata[i][0]
    return redata

def Reray(pos1,pos2):
    sta = {
        "appid": "dj00aiZpPWlGdHd2QlFKTDZZWiZzPWNvbnN1bWVyc2VjcmV0Jng9ODg-", 
        "output":"&output=json"
        }
    redata={}
    url="https://map.yahooapis.jp/spatial/V1/shapeSearch?appid="+sta["appid"]+"&coordinates="+pos1.lon+","+pos1.lat+"%20"+pos1.lon+","+pos1.lat+"%20"+pos2.lon+","+pos2.lat+"&mode=line"+sta["output"]
    res=urllib.request.urlopen(url)
    data=json.loads(res.read().decode())
    #print(data)
    for i in data["Feature"]:
        foo=i["Geometry"]["Coordinates"].split(",")
        foo[0],foo[1]=foo[1],foo[0]
        redata[i["Name"]]=foo
        suburl="https://map.yahooapis.jp/inner/V1/building?lat="+foo[0]+"&lon="+foo[1]+"&appid="+sta["appid"]+sta["output"]
        subres=urllib.request.urlopen(suburl)
        subdata=json.loads(subres.read().decode())
        if(subdata["ResultInfo"]["Count"]!=0):
            redata[i["Name"]].append(int(subdata["Dictionary"]["Building"][0][0]["Floor"]))
        else:
            redata[i["Name"]].append(1)
    return redata

def stepsort(redata):
    n=len(redata)
    carrent=0
    for i in range(n-1):
        carrent=i
        for k in range(i,n):
            if redata[i]["step"]>redata[k]["step"]:
                carrent=k
        redata[i],redata[carrent]=redata[carrent],redata[i]
    return 0;

def searchplace(pos):
    data=get_Coordinates(pos)
    hoge={}
    sumstep=[]
    for i in range(len(data)):
        sumstep.append(0)
    for i in range(len(data)):
        pos2=HazapModules.Coordinates()
        pos2.lat=data[i][0]
        pos2.lon=data[i][1]
        hoge[i]=Reray(pos,pos2)
        for k in hoge[i]:
            sumstep[i]+=hoge[i][k][2]
        hoge[i]["step"]=sumstep[i]
        hoge[i]["coordinates"]=data[i]

    stepsort(hoge)
    return hoge

#lat=緯度　lon=経度
def CarcuEva(Coordinates):
    #座標を投げたらその座標の建物の種類の評価値を返します
    sta = {
        "appid": "dj00aiZpPWlGdHd2QlFKTDZZWiZzPWNvbnN1bWVyc2VjcmV0Jng9ODg-", 
        "output":"&output=json"
        }
    url1="https://map.yahooapis.jp/geoapi/V1/reverseGeoCoder?lat="+Coordinates.lat+"&lon="+Coordinates.lon+"&appid="+sta["appid"]+sta["output"]
    res1=urllib.request.urlopen(url1)
    data1=json.loads(res1.read().decode())

    hoge=data1["Feature"][0]["Geometry"]["Coordinates"].split(',')
    url="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+hoge[1]+"&lon="+hoge[0]+"&dist=2"+sta["output"]+"&gc=0425&sort=geo"
    res=urllib.request.urlopen(url)
    data=json.loads(res.read().decode())
    st=data["Feature"][0]["Property"]["Genre"][0]["Name"]
    value=0
    if st.find("避難")!=-1:
        value=100
    elif  st.find("学校")!=-1:
        value=75
    elif  st.find("公園")!=-1:
        value=50
    elif  st.find("ガソリンスタンド")!=-1:
        value=25


    return value

def Calcudens(Coordinates):
    pi=math.pi
    r=6378100#これは地球の半径で、単位はメートル
    n=len(Coordinates)
    data=[]
    for i in range(n):
        data.append(0)

    for i in range(n):
        for k in range(n-i-1):
            d=math.sqrt((r*math.radians(abs(float(Coordinates[i][1])-float(Coordinates[k+i+1][1]))))**2+(r*math.radians(abs(float(Coordinates[i][0])-float(Coordinates[k+i+1][0]))))**2)
            if(d<=150):
                data[i]+=1
                data[i+k+1]+=1
    print("data=",data)
    return 0
