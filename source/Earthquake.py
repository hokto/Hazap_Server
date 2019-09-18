import HazapModules
import os
import requests
import json

def get_Dangerplaces(centerPos):#地震の揺れやすさを表す指標(ARV値)を取得
    if(os.path.exists("../data/"+str(int(centerPos.lat*10**3))+str(int(centerPos.lon*10**3))+".json")):
        with open("../data/"+str(int(centerPos.lat*10**3))+str(int(centerPos.lon*10**3))+".json",encoding="utf_8_sig") as f:
            dangerPlaces=json.load(f,encoding="utf_8_sig")
    else:
            APIKEY="dj00aiZpPWlGdHd2QlFKTDZZWiZzPWNvbnN1bWVyc2VjcmV0Jng9ODg-"
            places_url="https://map.yahooapis.jp/search/local/V1/localSearch?appid={key}&lat={lat}&lon={lon}&sort=-dist&results=100&output=json&dist=1&distinct=false"
            places_url=places_url.format(key=APIKEY,lat=centerPos.lat,lon=centerPos.lon)
            places=requests.get(places_url)
            places=places.json()
            count=places["ResultInfo"]["Count"]
            subcount=places["ResultInfo"]["Count"]
            minplace=HazapModules.Coordinates()
            minplace.lat=float(places["Feature"][99]["Geometry"]["Coordinates"].split(",")[1])
            minplace.lon=float(places["Feature"][99]["Geometry"]["Coordinates"].split(",")[0])
            debugcount=0
            while True:
                if subcount>0:
                    distance=HazapModules.Calculatedistance(centerPos,minplace)
                    print(distance,subcount)
                    subplaces_url="https://map.yahooapis.jp/search/local/V1/localSearch?appid={key}&lat={lat}&lon={lon}&sort=-dist&results=100&output=json&dist="+str(distance/1000)+"&distinct=false"
                    subplaces_url=subplaces_url.format(key=APIKEY,lat=centerPos.lat,lon=centerPos.lon)
                    subplaces=requests.get(subplaces_url)
                    subplaces=subplaces.json()
                    count+=subplaces["ResultInfo"]["Count"]
                    subcount=subplaces["ResultInfo"]["Count"]
                    for i in range(subplaces["ResultInfo"]["Count"]):
                        places["Feature"].append(subplaces["Feature"][i])
                    minplace.lat=float(subplaces["Feature"][subplaces["ResultInfo"]["Count"]-1]["Geometry"]["Coordinates"].split(",")[1])
                    minplace.lon=float(subplaces["Feature"][subplaces["ResultInfo"]["Count"]-1]["Geometry"]["Coordinates"].split(",")[0])
                    if subcount<100:
                        break;
                else:
                    break

            print("success")
            before_place=""
            dangerPlaces={}
            idx=0
            for i in range(count):
                if(before_place==places["Feature"][i]["Geometry"]["Coordinates"]):
                    continue
                dangerPlaces[idx]={}
                if(places["Feature"][i]["Property"]["Genre"]==[]):
                    dangerPlaces[idx]["Code"]="Null"
                else:
                    dangerPlaces[idx]["Code"]=places["Feature"][i]["Property"]["Genre"][0]["Code"]
                arv_url="http://www.j-shis.bosai.go.jp/map/api/sstrct/V3/meshinfo.geojson?position={pos}&epsg=4301"
                arv_url=arv_url.format(pos=places["Feature"][i]["Geometry"]["Coordinates"])
                list_ARV=requests.get(arv_url)
                list_ARV=list_ARV.json()

                placesHeight_url="https://map.yahooapis.jp/geoapi/V1/reverseGeoCoder?lat={lat}&lon={lon}&appid={key}&output=json"
                lon,lat=places["Feature"][i]["Geometry"]["Coordinates"].split(",")
                placesHeight_url=placesHeight_url.format(lat=lat,lon=lon,key=APIKEY)
                placesHeight=requests.get(placesHeight_url)
                placesHeight=placesHeight.json()
                before_place=places["Feature"][i]["Geometry"]["Coordinates"]
                dangerPlaces[idx]["Coordinates"]=before_place
                if(len(placesHeight["Feature"][0]["Property"])!=4):
                    dangerPlaces[idx]["Step"]="0"
                else:
                    dangerPlaces[idx]["Step"]=placesHeight["Feature"][0]["Property"]["Building"][0]["Floor"]
                dangerPlaces[idx]["ARV"]=list_ARV["features"][0]["properties"]["ARV"]
                idx+=1
            with open("../data/"+str(int(centerPos.lat*10**3))+str(int(centerPos.lon*10**3))+".json","w") as f:
                json.dump(dangerPlaces,f,ensure_ascii=False,indent=4)
    with open("../data/dangerplaces.json","w") as f:
             json.dump(dangerPlaces,f,ensure_ascii=False,indent=4)

