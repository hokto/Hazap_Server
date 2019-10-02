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
	for i in range(len(coordinatelist)):
		count+=1
		if count==1:
			pos1.lat=float(coordinatelist[str(i)].split(",")[1])
			pos1.lon=float(coordinatelist[str(i)].split(",")[0])
			continue
		pos2.lat=float(coordinatelist[str(i)].split(",")[1])
		pos2.lon=float(coordinatelist[str(i)].split(",")[0])
		sumdis+=HazapModules.Calculatedistance(pos1,pos2)#pos1,pos2に値を設定し、距離を測定。総距離に足していく
		pos1.lat=float(coordinatelist[str(i)].split(",")[1])
		pos1.lon=float(coordinatelist[str(i)].split(",")[0])
	return sumdis

def simulatetunami(placelist,h,x):
	table={}
	print("The simulator started running")
	foo=copy.deepcopy(placelist)
	for i in foo:
		foo[i]=foo[i].replace(" ",",").split(",")[1]+","+foo[i].replace(" ",",").split(",")[0]
	table["0"]=foo
	sumx=x
	sumdis=sumDisinList(table["0"])
	vol=sumdis*h*x#津波の体積V=海岸線の長さ*点と点の間隔*波の高さ*震源地から海岸までの距離。
	count=1
	base="https://map.yahooapis.jp/alt/V1/getAltitude?"
	base+=(HazapModules.APIPubWord+"&coordinates=")

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
				if(flgpl[k]==4):
					sub[str(k)]=table[str(count-1)][str(k)]
					exceptcount+=1
				elif(subdata["Feature"][k%(requestsize*4)-exceptcount]["Property"]["Altitude"]>height):
					flgpl[k]=4
					sub[str(k)]=table[str(count-1)][str(k)]
				else:
					sub[str(k)]=subdata["Feature"][k%(requestsize*4)-exceptcount]["Geometry"]["Coordinates"]
				k+=1
		table[str(count)]=copy.deepcopy(sub)#tableに記録
		count+=1
		sumx+=metl#x1+x2,津波が移動した距離をsumxつまり総移動距離に加える
		sumdis=sumDisinList(sub)#海岸線の長さ
		height=vol/(sumdis*sumx)#高さ=体積/(海岸線の長さ*総移動距離)
		json.dump(table,open("../data/simulated.json","w"),ensure_ascii=False,indent=4)
		if height<0.3:
			break
		metl=math.sqrt(9.8*height)
		changle=math.degrees(metl/HazapModules.r)

	return table

if __name__=="__main__":
	try:
		simulatetunami(json.load(open("../data/squeezed.json",encoding="utf_8_sig")),20,1000)
	except KeyboardInterrupt:
		print("server was stopped by keybord")
	