import HazapModules
import os
import requests
import json

def get_Dangerplaces(centerPos):#地震の揺れやすさを表す指標(ARV値)を取得
    APIKEY="dj00aiZpPWNIMG5nZEpkSXk3OSZzPWNvbnN1bWVyc2VjcmV0Jng9ZDk-"
    places_url="https://map.yahooapis.jp/search/local/V1/localSearch?appid={key}&lat={lat}&lon={lon}&sort=dist&results=100&output=json&dist=2&distinct=false"
    places_url=places_url.format(key=APIKEY,lat=centerPos.lat,lon=centerPos.lon)
    places=requests.get(places_url)
    places=places.json()
    before_place=""
    dangerPlaces={}
    for i in range(places["ResultInfo"]["Count"]):
        if(before_place==places["Feature"][i]["Geometry"]["Coordinates"]):
            continue
        dangerPlaces[i]={}
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
        dangerPlaces[i]["Coordinates"]=before_place
        if(len(placesHeight["Feature"][0]["Property"])!=4):
            dangerPlaces[i]["Step"]=0
        else:
            dangerPlaces[i]["Step"]=placesHeight["Feature"][0]["Property"]["Building"][0]["Floor"]
        dangerPlaces[i]["ARV"]=list_ARV["features"][0]["properties"]["ARV"]
    with open("../data/dangerplaces.json","w") as f:
        json.dump(dangerPlaces,f,ensure_ascii=False,indent=4)
