import requests
import json
import urllib
import math
import Routes

def Cal_Arclength(a,b,c,r):#余弦定理を用いて角度を出し、l=rθより弧の長さを求める
    cosC=(a**2+b**2-c**2)/(2*a*b)
    if(cosC>1):
        cosC=1
    elif(cosC<-1):
        cosC=-1
    radian=math.acos(cosC)
    arclength=r*radian
    return arclength
def Compare_route(start_pos,optimal_goal,real_goal):#ルート比較用関数
    real_dx=(real_goal.lon-start_pos.lon)#実際のルートにおける緯度、経度の変位を求め、傾きを計算 
    real_dy=(real_goal.lat-start_pos.lat)#dx,dyが0のときの例外処理が必要
    real_inclination=real_dy/real_dx
    optimal_dx=(optimal_goal.lon-start_pos.lon)#実際のルートでも同様に傾きを計算
    optimal_dy=(optimal_goal.lat-start_pos.lat)
    optimal_inclination=optimal_dy/optimal_dx
    minr=min(abs(real_dx),abs(real_dy),abs(optimal_dx),abs(optimal_dy))#半径を求める
    totaldiff=0
    for i in range(100):
        r=(minr/100)*(i+1)#同心円の半径
        circumference=2*math.pi*r#円周
        real_x=r/math.sqrt(real_inclination**2+1)#実際のゴール地点の傾きにおける各座標
        if(real_dx<0):
            real_x*=-1
        real_y=real_inclination*real_x
        optimal_x=r/math.sqrt(real_inclination**2+1)#最適なゴール地点の傾きにおける各座標
        if(optimal_dx<0):
            optimal_x*=-1
        optimal_y=optimal_inclination*optimal_x
        realDistance=math.sqrt(real_x**2+real_y**2)#スタートー実際のゴール間の距離
        optimalDistance=math.sqrt(optimal_x**2+optimal_y**2)#スタートー最適なゴール間の距離
        OptimalRealdiff=math.sqrt((real_x-optimal_x)**2+(real_y-optimal_y)**2)#最適なゴールー実際のゴール間の距離
        arcLength=Cal_Arclength(realDistance,optimalDistance,OptimalRealdiff,r)#弧の長さ
        totaldiff+=50-(arcLength/circumference)*100#最大割合が50%
    return (totaldiff/100*2)#割合の平均値を返す
start_pos=Routes.Pos()
optimal_goal=Routes.Pos()
real_goal=Routes.Pos()

start_pos.lat=31.760254
start_pos.lon=131.080396

optimal_goal.lat=32.760254
optimal_goal.lon=132.080396

real_goal.lat=30.760254
real_goal.lon=130.080396

print(Compare_route(start_pos,optimal_goal,real_goal))

