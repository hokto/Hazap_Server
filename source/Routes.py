import requests
import json
import urllib
import HazapModules
from itertools import chain
def Search_route(start,goal,realRoute):#最適ルートを取得する関数。
    APIKEY="dj00aiZpPWNIMG5nZEpkSXk3OSZzPWNvbnN1bWVyc2VjcmV0Jng9ZDk-"
    url="https://map.yahooapis.jp/spatial/V1/shapeSearch?mode=circle&appid={key}&coordinates={start_lon},{start_lat} {start_lon},{start_lat} {goal_lon},{goal_lat} {goal_lon},{goal_lat}&sort=box&results=100&output=json"
    access_url=url.format(key=APIKEY,start_lat=start.lat,start_lon=start.lon,goal_lat=goal.lat,goal_lon=goal.lon)#必要なデータの代入
    result=requests.get(access_url)#データをjsonで取得し、連想配列に変換
    result=result.json()
    list_places=[]#取得した場所の緯度、経度を格納
    for i in range(result["ResultInfo"]["Total"]):#取得できた数だけ格納する
        place=result["Feature"][i]["Geometry"]["Coordinates"]
        list_places.append(place)
    safty_places=Search_safty(list_places)#取得した場所の中から安全な場所を取得
    Making_route(APIKEY,str(start.lat)+","+str(start.lon),safty_places,str(goal.lat)+","+str(goal.lon),realRoute)


def Search_safty(list_places):#安全な場所を探索する関数。
    list_ARV=[]#ARV（最大増振率）を格納
    for i in range(len(list_places)):
        url="http://www.j-shis.bosai.go.jp/map/api/sstrct/V3/meshinfo.geojson?position={current_pos}&epsg=4301"
        access_url=url.format(current_pos=list_places[i])#必要なデータを代入
        result=requests.get(access_url)#データをjsonで取得、連想配列に変換
        result=result.json()
        list_ARV.append(result["features"][0]["properties"]["ARV"])#ARVを格納
        place=list_places[i].split(",")
        list_places[i]=place[1]+","+place[0]
    if(len(list_places)==0):#例外処理（スタートからゴールまでの距離が近いとき）
        return None
    Sort_places(list_places,list_ARV,0,len(list_places)-1)#ARVが小さい順に取得した場所をソート
    min_val=list_ARV[0]
    safty_places=[]#ARVが小さい場所の緯度、経度を格納
    for i in range(5):#修正する可能性あり
        if(not(min_val==list_ARV[i] or i<len(list_ARV)/2)):#最低でも半分の場所を格納
            break
        safty_places.append(list_places[i])
    return safty_places


def Sort_places(list_places,list_ARV,left,right):#ARVが小さい順に場所とARVをソート（クイックソート）
    i=left+1
    k=right
    while(i<k):
        while(list_ARV[i]<list_ARV[left] and i<right):
            i+=1
        while(list_ARV[k]>=list_ARV[left] and k>left):
            k-=1
        if(i<k):
            wrap=list_ARV[i]
            list_ARV[i]=list_ARV[k]
            list_ARV[k]=wrap

            wrap=list_places[i]
            list_places[i]=list_places[k]
            list_places[k]=wrap
    if(list_ARV[left]>list_ARV[k]):
        wrap=list_ARV[left]
        list_ARV[left]=list_ARV[k]
        list_ARV[k]=wrap

        wrap=list_places[left]
        list_places[left]=list_places[k]
        list_places[k]=wrap
    if(left<k-1):
        Sort_places(list_places,list_ARV,left,k-1)
    if(k+1<right):
        Sort_places(list_places,list_ARV,k+1,right)


def Making_route(APIKEY,start,list_via,optimal_goal,list_realRoute):#最適ルートと、実際に通ったルートの作成関数。
    if(list_via==None):#経由地点なしの場合
        url="https://map.yahooapis.jp/course/V1/routeMap?appid={apikey}&route={RealRoute}|start:on|goal:on|&route={start_place},{optimal_goal}|color:ff000099|start:off|goal:on"
        access_url=url.format(apikey=APIKEY,start_place=start,optimal_goal=optimal_goal,RealRoute=",".join(list_realRoute))
    else:
        url="https://map.yahooapis.jp/course/V1/routeMap?appid={apikey}&route={RealRoute}|start:on|goal:on&route={start_place},{via_places},{optimal_goal}|color:ff000099|start:off|goal:on"
        access_url=url.format(apikey=APIKEY,start_place=start,via_places=",".join(list_via),optimal_goal=optimal_goal,RealRoute=",".join(list_realRoute))
    Download_route(access_url,"../img/route.png")


def Download_route(url,file_path):#探索したルートの画像を取得して保存する関数。
    try:
        with urllib.request.urlopen(url) as web_file:
            data=web_file.read()
            with open(file_path,mode="wb")as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        print(e)

