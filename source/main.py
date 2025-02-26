import getplace
import Routes
import HazapModules
import os
import json

def OptimalEvacuation(start_pos,realRoute,resultFlag,disaster,disasterScale):#最適な避難場所の探索、及び最適な避難経路の探索、実際に避難した経路と最適な避難場所を同じ画像に出力
    if(resultFlag):
        #そこから取得
        with open("../data/result.json",encoding="utf-8_sig") as f:
            resultJson=json.load(f)
        places=resultJson["EvacuationPlaces"]
        goal_pos=places["0"]["coordinates"]
        optimal_goal=HazapModules.Coordinates()
        optimal_goal.lat,optimal_goal.lon=float(goal_pos[0]),float(goal_pos[1])
    else:
        places=getplace.searchplace(start_pos,disaster,disasterScale)#最適な避難場所を取得
        resultJson={}
        resultJson["EvacuationPlaces"]=places
        with open("../data/result.json","w",encoding="utf-8_sig") as f:
            json.dump(resultJson,f,ensure_ascii=False,indent=4)
        goal_pos=places[0]["coordinates"]
        optimal_goal=HazapModules.Coordinates()
        optimal_goal.lat,optimal_goal.lon=float(goal_pos[0]),float(goal_pos[1])
    Routes.Search_route(start_pos,optimal_goal,realRoute,resultFlag)#最適なルートを作成
    return places#評価の高かった場所のリストを返す

def Result(start_pos,realRoute,hp,disaster,disasterScale):#リザルト画面に必要な処理を行う関数。主に、経路作成や生存率の計算など
    if(os.path.exists("../data/result.json")):
        ResultFlag=True
    else:
        ResultFlag=False
    places=OptimalEvacuation(start_pos,realRoute,ResultFlag,disaster,disasterScale)#経路作成と最適な場所を取得
    optimal_goal=HazapModules.Coordinates()
    if(ResultFlag):
        optimal_goal.lat,optimal_goal.lon=float(places["0"]["coordinates"][0]),float(places["0"]["coordinates"][1])#最適な場所の座標
    else:
        optimal_goal.lat,optimal_goal.lon=float(places[0]["coordinates"][0]),float(places[0]["coordinates"][1])#最適な場所の座標
    real_goal=HazapModules.Coordinates()
    real_goal.lat,real_goal.lon=list(map(float,realRoute[len(realRoute)-1].split(",")))#実際の避難場所の座標
    optimalEva=getplace.CarcuEva(optimal_goal,disaster,disasterScale)
    realEva=getplace.CarcuEva(real_goal,disaster,disasterScale)
    rate=""
    placePercentage=0
    if(optimalEva<realEva):
        placePercentage=100
    else:
        placePercentage=(realEva/optimalEva)*100
    print("Place:"+str(placePercentage))
    rate+=str(placePercentage)+":"
    #rate+=(100/(placePercentage+0.01)*0.4)
    print("HP:"+str(hp))
    rate+=str(hp)+":"
    #rate+=(100/(hp+0.01)*0.2)
    return rate
