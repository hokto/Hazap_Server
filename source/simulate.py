import urllib.request
import HazapModules
import json
import math
import copy
import os

def sumDisinList(coordinatelist):#全ての座標の間の距離の総和を返す。投げる座標の区切りは,であること
	sumdis=0.0
	count=0
	pos1=HazapModules.Coordinates()
	pos2=HazapModules.Coordinates()
	for i in coordinatelist:
		count+=1
		if count==1:
			pos1.lat=float(coordinatelist[i].split(",")[0])
			pos1.lon=float(coordinatelist[i].split(",")[1])
			continue
		pos2.lat=float(coordinatelist[i].split(",")[0])
		pos2.lon=float(coordinatelist[i].split(",")[1])
		sumdis+=HazapModules.Calculatedistance(pos1,pos2)#pos1,pos2に値を設定し、距離を測定。総距離に足していく
		pos1.lat=float(coordinatelist[i].split(",")[0])
		pos1.lon=float(coordinatelist[i].split(",")[1])
	return sumdis

def simulatetunami(placelist,h,x):
	print("The simulator started running")
	table={}
	sumx=x
	vol=(len(placelist)-1)*100*h*x#津波の体積V=(辞書の大きさ-1)*点と点の間隔*波の高さ*震源地から海岸までの距離。
	#(辞書の大きさ-1)としているのは、例えば12個の点を結ぶ線の辺は11本になるため。辞書の要素数がそのまま点の数になる
	foo=copy.deepcopy(placelist)
	for i in foo:
		foo[i]=foo[i].replace(" ",",").split(",")[1]+","+foo[i].replace(" ",",").split(",")[0]
	table["0"]=foo
	count=1

	sta = {
	"appid": "dj00aiZpPWlGdHd2QlFKTDZZWiZzPWNvbnN1bWVyc2VjcmV0Jng9ODg-", 
	"output":"json"
	}

	base="https://map.yahooapis.jp/alt/V1/getAltitude?"
	base+="appid="+sta["appid"]+"&output="+sta["output"]+"&coordinates="

	height=h#波の高さ
	requestsize=10#最大10。4方向*10でGETリクエスト上限の40になるため。POSTリクエストだと上限が100になるため、最大25
	metl=math.sqrt(9.8*height)#1秒間に進む距離√g*h
	changle=math.degrees(metl/HazapModules.r)#1秒間に変化する角度

	flgpl=[]#4方向にアクセスした際の1番高い方向のフラグを管理
	for i in range(len(placelist)):
		flgpl.append(0)
	for i in range(0,len(placelist),requestsize):
		url=base
		for k in range(i,min(i+requestsize,len(placelist))):
			url+=str(float(table[str(count-1)][str(k)].split(",")[0]))+","+str(float(table[str(count-1)][str(k)].split(",")[1])+changle)+","#上
			url+=str(float(table[str(count-1)][str(k)].split(",")[0])+changle)+","+str(float(table[str(count-1)][str(k)].split(",")[1]))+","#右
			url+=str(float(table[str(count-1)][str(k)].split(",")[0]))+","+str(float(table[str(count-1)][str(k)].split(",")[1])-changle)+","#下
			url+=str(float(table[str(count-1)][str(k)].split(",")[0])-changle)+","+str(float(table[str(count-1)][str(k)].split(",")[1]))+","#左
		data=json.loads(urllib.request.urlopen(url.rstrip(",")).read().decode())
		for k in range(i,min(i+requestsize,len(placelist))):
			maxindex=4*k%40
			maxdir=4*k%40%4
			for d in range(4*k%40,4*k%40+4):
				if(data["Feature"][d]["Property"]["Altitude"]>data["Feature"][maxindex]["Property"]["Altitude"]):
					maxindex=d
					maxdir=d%4
			flgpl[k]=maxdir
		
	#フラグ設定完了。これより、ループ処理に参る。


	while True:
		sub={}
		for i in range(0,len(placelist),requestsize*4):
			suburl=base
			#40個分の座標をsuburlに追加。もしflgpl[k]が4だったらそこは津波が到達できないところなので、直前のデータを入れる
			for k in range(i,min(i+requestsize*4,len(placelist))):
				index=0
				if(flgpl[k]==4):
					sub[str(k)]=table[str(count-1)][str(k)]
					continue
				elif(flgpl[k]==0):
					suburl+=str(float(table[str(count-1)][str(k)].split(",")[0]))+","+str(float(table[str(count-1)][str(k)].split(",")[1])+changle)+","#上
				elif(flgpl[k]==1):
					suburl+=str(float(table[str(count-1)][str(k)].split(",")[0])+changle)+","+str(float(table[str(count-1)][str(k)].split(",")[1]))+","#右
				elif(flgpl[k]==2):
					suburl+=str(float(table[str(count-1)][str(k)].split(",")[0]))+","+str(float(table[str(count-1)][str(k)].split(",")[1])-changle)+","#下
				elif(flgpl[k]==3):
					suburl+=str(float(table[str(count-1)][str(k)].split(",")[0])-changle)+","+str(float(table[str(count-1)][str(k)].split(",")[1]))+","#左

			subdata=json.loads(urllib.request.urlopen(suburl.rstrip(",")).read().decode())
			#print("\nlen=",len(subdata["Feature"]))
			exceptcount=0
			k=i
			while k<min(i+requestsize*4,len(placelist)):
				#print("count=",count,",k=",k,",k%(requestsize*4)=",k%(requestsize*4),",flgpl[k]=",flgpl[k])
				if(flgpl[k]==4):
					sub[str(k)]=table[str(count-1)][str(k)]
					exceptcount+=1
				elif(subdata["Feature"][k%(requestsize*4)-exceptcount]["Property"]["Altitude"]>height):
					flgpl[k]=4
					sub[str(k)]=table[str(count-1)][str(k)]
				else:
					sub[str(k)]=subdata["Feature"][k%(requestsize*4)-exceptcount]["Geometry"]["Coordinates"]
				k+=1
		table[str(count)]=copy.deepcopy(sub)
		count+=1
		sumx+=metl#x1+x2
		height=vol/(sumDisinList(sub)*sumx)#高さ=体積/(海岸線の長さ*(x1+x2))
		json.dump(table,open("../data/simulated.json","w"),ensure_ascii=False,indent=4)
		if height<0.3:
			break
		metl=math.sqrt(9.8*height)
	return table