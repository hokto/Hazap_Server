import getplace
import Routes
import HazapModules

def OptimalEvacuation(start_pos):#最適な避難場所の探索、及び最適な避難経路の探索、実際に避難した経路と最適な避難場所を同じ画像に出力
    places=getplace.searchplace(start_pos)#最適な避難場所を取得
    optimal_goal=places[0]["coordinates"]
    goal_pos=HazapModules.Coordinates()
    goal_pos.lat,goal_pos.lon=float(optimal_goal[0]),float(optimal_goal[1])
    Routes.Search_route(start_pos,goal_pos)#最適なルートを作成
start=HazapModules.Coordinates()
start.lat="31.760254"#仮設定:都城高専からの避難
start.lon="131.080396"
OptimalEvacuation(start)
