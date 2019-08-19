import getplace
import Routes
import Aliverate
import HazapModules

def OptimalEvacuation(start_pos,realRoute):#最適な避難場所の探索、及び最適な避難経路の探索、実際に避難した経路と最適な避難場所を同じ画像に出力
    places=getplace.searchplace(start_pos)#最適な避難場所を取得
    goal_pos=places[0]["coordinates"]
    optimal_goal=HazapModules.Coordinates()
    optimal_goal.lat,optimal_goal.lon=float(goal_pos[0]),float(goal_pos[1])
    Routes.Search_route(start_pos,optimal_goal,realRoute)#最適なルートを作成
    return places#評価の高かった場所のリストを返す

def Result(start_pos,realRoute):#リザルト画面に必要な処理を行う関数。主に、経路作成や生存率の計算など
    places=OptimalEvacuation(start_pos,realRoute)#経路作成と最適な場所を取得
    optimal_goal=HazapModules.Coordinates()
    optimal_goal.lat,optimal_lon=float(places[0]["coordinates"][0]),float(places[0]["coordinates"][1])#最適な場所の座標
    real_goal=HazapModules.Coordinates()
    real_goal.lat,real_goal.lon=list(map(float,realRoute[len(realRoute)-1].split(",")))#実際の避難場所の座標
    routesPercentage=Aliverate.Compare_route(start_pos,optimal_goal,real_goal)#ルート比較の割合
    print("Route:"+str(routesPercentage))
    placePercentage=getplace.CarcuEva(real_goal)
    print("Place:"+str(placePercentage))
start=HazapModules.Coordinates()
start.lat=31.7536429#仮設定
start.lon=131.0504333
realRoute=[]
realRoute.append("31.7536429,131.0504333")
realRoute.append("31.7534066,131.051341")
Result(start,realRoute)
