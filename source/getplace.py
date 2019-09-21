import requests
import json
import urllib.request
import HazapModules
import math
import Routes
import time
import Earthquake
from PIL import Image
from websocket import create_connection
import shutil
import Coastplace
def get_Coordinates(pos):
    #この関数は緯度,経度を投げればその地点からの避難場所を返してくれる
    sta = {
        "appid": "dj00aiZpPWlGdHd2QlFKTDZZWiZzPWNvbnN1bWVyc2VjcmV0Jng9ODg-", 
        "output":"&output=json"
        }
    redata=[]
    tellist=[]
    url="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+str(pos.lat)+"&lon="+str(pos.lon)+"&dist=1"+sta["output"]+"&gc=0425&sort=geo"
    url2="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+str(pos.lat)+"&lon="+str(pos.lon)+"&dist=1"+sta["output"]+"&gc=0423007&sort=geo"
    url3="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+str(pos.lat)+"&lon="+str(pos.lon)+"&dist=1"+sta["output"]+"&gc=0305007&sort=geo"
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
        foo[0],foo[1]=foo[1],foo[0]
        if i["Geometry"]["Coordinates"] not in name:
            redata[i["Name"]]=foo

            suburl="https://map.yahooapis.jp/inner/V1/building?lat="+foo[0]+"&lon="+foo[1]+"&appid="+sta["appid"]+sta["output"]
            subres=urllib.request.urlopen(suburl)
            subdata=json.loads(subres.read().decode())
            if(subdata["ResultInfo"]["Count"]!=0):
                name[i["Geometry"]["Coordinates"]]=int(subdata["Dictionary"]["Building"][0][0]["Floor"])
                redata[i["Name"]].append(int(subdata["Dictionary"]["Building"][0][0]["Floor"]))
            else:
                name[i["Geometry"]["Coordinates"]]=1
                redata[i["Name"]].append(1)
        else:

            redata[i["Name"]]=foo
            redata[i["Name"]].append(name[i["Geometry"]["Coordinates"]])
        arvurl="http://www.j-shis.bosai.go.jp/map/api/sstrct/V3/meshinfo.geojson?position={current_pos}&epsg=4301" 
        accessurl=arvurl.format(current_pos=(foo[1]+","+foo[0]))
        result=requests.get(accessurl)
        result=result.json()
        redata[i["Name"]].append(float(result["features"][0]["properties"]["ARV"]))
    return redata

def searchplace(pos,disaster,disasterScale):
    #この関数は座標を投げるとその地点からいい避難場所への道のりにある建物の階数、つまり高さを足していって低い順にソートして返す
    data=get_Coordinates(pos)
    jsondata={}
    name={}
    sumstep=[]
    for i in range(len(data)):
        sumstep.append(0)

    for i in range(len(data)):
        pos2=HazapModules.Coordinates()
        pos2.lat=data[i][0]
        pos2.lon=data[i][1]
        jsondata[i]=Reray(pos,pos2,name)
        value=0
        for k in jsondata[i]:
            #sumstep[i]+=jsondata[i][k][2]
            value+=(jsondata[i][k][2]*jsondata[i][k][3])
        #jsondata[i]["step"]=sumstep[i]
        jsondata[i]["coordinates"]=data[i]
        jsondata[i]["Evaluation"]=CarcuEva(pos2,disaster,disasterScale)
        jsondata[i]["value"]=value-jsondata[i]["Evaluation"]
        wes = create_connection("ws://"+HazapModules.addres+":5000") 
        wes.send("long:"+str(pos.lat)+","+str(pos.lon)+":"+data[i][0]+","+data[i][1])
        dist=0
        while True:
            result =  wes.recv()
            ravel=result.split(":")
            if ravel[0] == "value":
                dist=float(ravel[1])
                break
        wes.close()
        jsondata[i]["range"]=dist
        #if dist==0:
        #    jsondata[i]["value"]=0
        #else:
        #    jsondata[i]["value"]=sumstep[i]/dist

    jsondata=HazapModules.TwoDimensionsSort(jsondata,"value",0,len(jsondata)-1)#stepsort
    return jsondata

#lat=緯度　lon=経度
def CarcuEva(Coordinates,disaster,disasterScale):
    #座標を投げたらその座標の建物の種類の評価値を返します
    sta = {
        "appid": "dj00aiZpPWlGdHd2QlFKTDZZWiZzPWNvbnN1bWVyc2VjcmV0Jng9ODg-", 
        "output":"&output=json"
        }
    url1="https://map.yahooapis.jp/geoapi/V1/reverseGeoCoder?lat="+str(Coordinates.lat)+"&lon="+str(Coordinates.lon)+"&appid="+sta["appid"]+sta["output"]
    res1=urllib.request.urlopen(url1)
    data1=json.loads(res1.read().decode())


    hoge=data1["Feature"][0]["Geometry"]["Coordinates"].split(',')
    url="https://map.yahooapis.jp/search/local/V1/localSearch?appid="+sta["appid"]+"&lat="+hoge[1]+"&lon="+hoge[0]+"&dist=1"+sta["output"]+"&gc=0425,0406,0305007,0412021&sort=dist"

    res=urllib.request.urlopen(url)
    data=json.loads(res.read().decode())
    targetPlace=data["Feature"][0]["Geometry"]["Coordinates"].split(",")
    addressurl="https://map.yahooapis.jp/geocode/V1/geoCoder?appid={apikey}&lat={lat}&lon={lon}&sort=dist&output=json"
    address1url=addressurl.format(apikey=sta["appid"],lat=targetPlace[1],lon=targetPlace[0])
    address1Result=requests.get(address1url)
    address1Result=address1Result.json()#Feature->0->Name

    address2url=addressurl.format(apikey=sta["appid"],lat=Coordinates.lat,lon=Coordinates.lon)
    address2Result=requests.get(address2url)
    address2Result=address2Result.json()

    if(data["ResultInfo"]["Count"]==0 or address1Result["Feature"][0]["Name"]!=address2Result["Feature"][0]["Name"]):#建物の座標が一切取れなかった、ゴール地点の建物が取得されなかった場合
        print("No places")
        return 0
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
    #建物の高さを取得し、評価値を変更
    placeJson=json.load(open("../data/dangerplaces.json",encoding="utf_8_sig"))
    placeHeight=0
    sumStep=0
    for i in range(len(placeJson)-1):
        sumStep+=int(placeJson[str(i)]["Step"])
        if(placeHeight==0 and math.isclose(round(float(Coordinates.lat),3),round(float(placeJson[str(i)]["Coordinates"].split(",")[1]),3),rel_tol=0.001,abs_tol=0.001) and math.isclose(round(float(Coordinates.lon),3),round(float(placeJson[str(i)]["Coordinates"].split(",")[0]),3),rel_tol=0.001,abs_tol=0.001)):
            placeHeight=int(placeJson[str(i)]["Step"])
    print("Height:",placeHeight)
    #また、地震の場合はARV地、津波の場合は、標高と海岸線までの距離を取得し、評価値変更
    if(disaster=="地震"):
        arvurl="http://www.j-shis.bosai.go.jp/map/api/sstrct/V3/meshinfo.geojson?position={current_pos}&epsg=4301" 
        accessurl=arvurl.format(current_pos=str(Coordinates.lon)+","+str(Coordinates.lat))
        resultARV=requests.get(accessurl)
        resultARV=resultARV.json()
        dangerJson=None
        arv=float(resultARV["features"][0]["properties"]["ARV"])
        with open("../data/dangerplaces.json",encoding="utf_8_sig") as f:
            dangerJson=json.load(f)
        minARV=float(dangerJson["MinARV"].split(",")[0])
        value*=(minARV/arv)
        if(sumStep/(len(placeJson)-1)<placeHeight):
            value*=((sumStep)/(len(placeJson)-1))/placeHeight
    elif(disaster=="津波"):
        #海抜（標高）を取得
        coastIdx=Coastplace.Fullpos(Coordinates,True)
        coastJson=json.load(open("../data/coastplaces.json",encoding="utf_8_sig"))
        coastPos=HazapModules.Coordinates()
        coastPos.lat,coastPos.lon=float(coastJson[str(coastIdx)].split(" ")[0]),float(coastJson[str(coastIdx)].split(" ")[1])
        altitudeurl="https://map.yahooapis.jp/alt/V1/getAltitude?appid={apikey}&coordinates={pos1},{pos2}&output=json"
        altitudeurl=altitudeurl.format(apikey=sta["appid"],pos1=str(Coordinates.lon)+","+str(Coordinates.lat),pos2=str(coastPos.lon)+","+str(coastPos.lat))
        resultAltitude=requests.get(altitudeurl)
        resultAltitude=resultAltitude.json()
        altitude=resultAltitude["Feature"][0]["Property"]["Altitude"]
        coastAltitude=resultAltitude["Feature"][1]["Property"]["Altitude"]
        coastS=(coastAltitude+float(disasterScale.split(":")[0]))*float(disasterScale.split(":")[1])
        hc=coastS/HazapModules.Calculatedistance(Coordinates,coastPos)
        hc-=altitude
        if(hc>placeHeight*5):
            value*=(placeHeight*5)/hc
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

def GenerateHazard(sta,end):
#    #指定した座標のハザードマップを生成するやつ
#    dis=HazapModules.Calculatedistance(sta,end)
#    radius=0
#    for i in range(2,100):
#        if(dis<i*1000):
#            radius=i
#            break
#    f=open("../data/dangerplaces.json",encoding="utf-8_sig")
#    resultJson=json.load(f)
#    e="0,255,0,0,3,0,255,0,127,"+str(sta.lat)+","+str(sta.lon)+","+"1000"
#    for i in resultJson:
#        foo=resultJson[i]["Coordinates"].split(",")
#        foo[0],foo[1]=foo[1],foo[0]
#        concen=110*(1/float(resultJson[i]["ARV"]))
#        if 126<concen:
#            concen=126
#        stre=":0,0,0,127,1,255,0,0,"+str(100*(1/float(resultJson[i]["ARV"])))+","+foo[0]+","+foo[1]+","+str(10*int(resultJson[i]["Step"]))
#        e+=stre
#
#    f=open("../data/dangerplaces.json",encoding="utf-8_sig")
#    resultJson=json.load(f)
#    mark=""
#    hoge=json.load(open("../data/result.json",encoding="utf-8_sig"))
#    postdata={
#    "output":"png",
#    "lat":str(sta.lat),
#    "lon":str(sta.lon),
#    "e":e,
#    "autoscale":"on",
#    "width":"1000",
#    "height":"1000"
#    }
#
##    for i in hoge["EvacuationPlaces"]:
##        postdata["pin"+str(int(i)+1)]=hoge["EvacuationPlaces"][i]["coordinates"][0]+","+hoge["EvacuationPlaces"][i]["coordinates"][1]
#
#    
#    
#
#    #yhurl="https://map.yahooapis.jp/map/V1/static?appid=dj00aiZpPWNIMG5nZEpkSXk3OSZzPWNvbnN1bWVyc2VjcmV0Jng9ZDk-"+mark+"&e="+e+"&autoscale=on&width=1000&height=1000&output=png"
#
#    with requests.post(url, data=postdata) as web_file:
#        data=web_file.text.encode()
#        with open("../img/test.html",mode="wb")as local_file:
#            local_file.write(data)
#    Routes.Download_route(yhurl,"../img/Generate.png")
    return 0


#if __name__=="__main__":
#    hh=HazapModules.Coordinates()
#    hh.lat=32.0341
#    hh.lon=131.501
#    print(Coastplace.Fullpos(hh))
