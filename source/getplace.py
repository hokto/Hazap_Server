import requests
import json
import urllib.request
import HazapModules
import math
import Routes
import time

def get_Coordinates(pos):
    #この関数は緯度,経度を投げればその地点からの避難場所を返してくれる
    sta = {
        "appid": "dj00aiZpPWlGdHd2QlFKTDZZWiZzPWNvbnN1bWVyc2VjcmV0Jng9ODg-", 
        "output":"&output=json"
        }
    redata=[]
    tellist=[]
    url="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+str(pos.lat)+"&lon="+str(pos.lon)+"&dist=2"+sta["output"]+"&gc=0425&sort=geo"
    url2="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+str(pos.lat)+"&lon="+str(pos.lon)+"&dist=2"+sta["output"]+"&gc=0423007&sort=geo"
    url3="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+str(pos.lat)+"&lon="+str(pos.lon)+"&dist=2"+sta["output"]+"&gc=0305007&sort=geo"
    res=urllib.request.urlopen(url)
    res2=urllib.request.urlopen(url2)
    res3=urllib.request.urlopen(url3)
    data=json.loads(res.read().decode())
    data2=json.loads(res2.read().decode())
    data3=json.loads(res3.read().decode())
    #この下の処理で座標をリストにまとめてreturn
    if(data["ResultInfo"]["Count"]!=0):
        for i in data["Feature"]:
            if(tellist.count(i["Property"]["Tel1"])==0):
                tellist.append(i["Property"]["Tel1"])
                redata.append(i["Geometry"]["Coordinates"].split(','))
    if(data2["ResultInfo"]["Count"]!=0):
        for i in data2["Feature"]:
            if(tellist.count(i["Property"]["Tel1"])==0):
                tellist.append(i["Property"]["Tel1"])
                redata.append(i["Geometry"]["Coordinates"].split(','))
    if(data3["ResultInfo"]["Count"]!=0):
        for i in data3["Feature"]:
            if(tellist.count(i["Property"]["Tel1"])==0):
                tellist.append(i["Property"]["Tel1"])
                redata.append(i["Geometry"]["Coordinates"].split(','))
    for i in range(len(redata)):
        redata[i][0],redata[i][1]=redata[i][1],redata[i][0]
    return redata

def Reray(pos1,pos2,name):
    sta = {
        "appid": "dj00aiZpPWlGdHd2QlFKTDZZWiZzPWNvbnN1bWVyc2VjcmV0Jng9ODg-", 
        "output":"&output=json"
        }
    redata={}
    url="https://map.yahooapis.jp/spatial/V1/shapeSearch?appid="+sta["appid"]+"&coordinates="+str(pos1.lon)+","+str(pos1.lat)+"%20"+str(pos1.lon)+","+str(pos1.lat)+"%20"+str(pos2.lon)+","+str(pos2.lat)+"&mode=line"+sta["output"]
    res=urllib.request.urlopen(url)
    data=json.loads(res.read().decode())

    for i in data["Feature"]:
        foo=i["Geometry"]["Coordinates"].split(",")
        if i["Geometry"]["Coordinates"] not in name:
            foo[0],foo[1]=foo[1],foo[0]
            redata[i["Name"]]=foo
            suburl="https://map.yahooapis.jp/inner/V1/building?lat="+foo[0]+"&lon="+foo[1]+"&appid="+sta["appid"]+sta["output"]
            subres=urllib.request.urlopen(suburl)
            subdata=json.loads(subres.read().decode())
           ## print(subdata,"\n\n")
            if(subdata["ResultInfo"]["Count"]!=0):
                name[i["Geometry"]["Coordinates"]]=int(subdata["Dictionary"]["Building"][0][0]["Floor"])
                redata[i["Name"]].append(int(subdata["Dictionary"]["Building"][0][0]["Floor"]))
            else:
                name[i["Geometry"]["Coordinates"]]=1
                redata[i["Name"]].append(1)
        else:
            redata[i["Name"]]=foo
            redata[i["Name"]].append(name[i["Geometry"]["Coordinates"]])
    return redata

def searchplace(pos):
    #この関数は座標を投げるとその地点からいい避難場所への道のりにある建物の階数、つまり高さを足していって低い順にソートして返す
    data=get_Coordinates(pos)
    hoge={}
    name={}
    sumstep=[]
    for i in range(len(data)):
        sumstep.append(0)

    for i in range(len(data)):
        pos2=HazapModules.Coordinates()
        pos2.lat=data[i][0]
        pos2.lon=data[i][1]
        hoge[i]=Reray(pos,pos2,name)
        for k in hoge[i]:
            sumstep[i]+=hoge[i][k][2]
        hoge[i]["step"]=sumstep[i]
        hoge[i]["coordinates"]=data[i]

    hoge=HazapModules.TwoDimensionsSort(hoge,"step",0,len(hoge)-1)#stepsort
    return hoge

#lat=緯度　lon=経度
def CarcuEva(Coordinates):
    #座標を投げたらその座標の建物の種類の評価値を返します
    sta = {
        "appid": "dj00aiZpPWlGdHd2QlFKTDZZWiZzPWNvbnN1bWVyc2VjcmV0Jng9ODg-", 
        "output":"&output=json"
        }
    url1="https://map.yahooapis.jp/geoapi/V1/reverseGeoCoder?lat="+str(Coordinates.lat)+"&lon="+str(Coordinates.lon)+"&appid="+sta["appid"]+sta["output"]
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
    r=6378100#これは地球の半径で、単位はメートル
    n=len(Coordinates)
    data={}
    for i in range(n):
        data[i]=0

    for i in range(n):
        for k in range(n-i-1):
            distance=math.sqrt((r*math.radians(abs(float(Coordinates[i][1])-float(Coordinates[k+i+1][1]))))**2+(r*math.radians(abs(float(Coordinates[i][0])-float(Coordinates[k+i+1][0]))))**2)
            if(distance<=150):
                data[i]+=1
                data[i+k+1]+=1
    return data

def GenerateHazard(Coordinates):
    url="http://www.j-shis.bosai.go.jp/map/api/pshm/Y2010/AVR/TTL_MTTL/meshinfo.geojson?position="+str(Coordinates.lon)+","+str(Coordinates.lat)+"&epsg=4301"
    res=urllib.request.urlopen(url)
    data=json.loads(res.read().decode())
    img=""
    mark=""
    hoge=searchplace(Coordinates)
    n=len(hoge)
    for i in range(n):
        mark+="&pin"+str(i+1)+"="+hoge[i]["coordinates"][0]+","+hoge[i]["coordinates"][1]
    print(mark)

    for i in range(len(data["features"][0]["geometry"]["coordinates"][0])):
        img+=","+str(data["features"][0]["geometry"]["coordinates"][0][i][1])+","+str(data["features"][0]["geometry"]["coordinates"][0][i][0])
    print(img)
    yhurl="https://map.yahooapis.jp/map/V1/static?appid=dj00aiZpPWNIMG5nZEpkSXk3OSZzPWNvbnN1bWVyc2VjcmV0Jng9ZDk-&"+mark+"&p=0,0,255,0,3,0,0,255,60"+img+"&e=0,255,0,0,5,0,255,0,127,"+str(Coordinates.lat)+","+str(Coordinates.lon)+",2000&z=16&width=1000&height=1000&output=png32"
    Routes.Download_route(yhurl,"../img/test.png")

    return 0

if __name__=="__main__":
    pos=HazapModules.Coordinates()
    pos.lat=31.760254
    pos.lon=131.080396
    GenerateHazard(pos)