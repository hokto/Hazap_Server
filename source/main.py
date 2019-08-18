import getplace
import Routes
def OptimalEvacuation(start_pos):#最適な避難場所の探索、及び最適な避難経路の探索、実際に避難した経路と最適な避難場所を同じ画像に出力
    places=getplace.searchplace(str(start_pos.lat),str(start_pos.lon))#最適な避難場所を取得
    optimal_goal=places[0]["coordinates"]
    goal_pos=Routes.Pos()
    goal_pos.lat,goal_pos.lon=float(optimal_goal[0]),float(optimal_goal[1])
    Routes.Search_route(start_pos,goal_pos)#最適なルートを作成
start=Routes.Pos()
start.lat=31.760254#仮設定:都城高専からの避難
start.lon=131.080396
OptimalEvacuation(start)
