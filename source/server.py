import socket
import getplace
import io
from PIL import Image
import Earthquake
import HazapModules
import main
import json
import numpy
import os
import time
from websocket import create_connection
import Coastplace
import requests
import simulate
import threading
import webbrowser

def server():
    contents=None
    startflg=0
    endflg=0
    port=4000
    count={}
    placesCoorsinates=None
    webbrowser.open_new(os.path.abspath("../HTML/websocket.html"))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        # IPアドレスとポートを指定
        n=0
        s.bind((HazapModules.addres,4000))

        Coordinates={}#最新の位置情報を格納している辞書
        CoordinateLogs={}#最新の座標も含めてそれぞれの人の今までの座標を記録している辞書
        timeLogs=[]#現在地を取得した最終時間を記録するリスト
        distLogs=[]#利用者が進んだ距離を保存するリスト
        disaster=""#災害の種類
        disasterScale=""#災害の規模
        # 1 接続
        s.listen(1)
        # connection するまで待つ
        startPos=HazapModules.Coordinates()
        message=""
        while True:
            send="Invalid"
            # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
            conn, addr = s.accept()
            print("connected from:",addr)
            with conn:
                while True:
                    # データを受け取る
                    data = conn.recv(1024)
                    #send="Invalid"
                    if not data:
                        break

                    rec=data.decode()
                    splited=rec.split(":")
                    print(splited[0])
                    if(splited[0]=="Recruit" and startflg==0):#サーバに参加を伝える
                        send=str(n)
                        CoordinateLogs[n]=[]
                        pl=splited[1].split(",")
                        CoordinateLogs[n].append(pl)
                        Coordinates[n]=splited[1].split(",")
                        send="number:"+str(n)
                        n+=1
                        print(splited)
                        conn.sendall(send.encode())
                    elif splited[0]=="Recruit" and startflg==1:#すでにスタートしていた場合、参加を拒否する

                        send="started"
                        conn.sendall(send.encode())
                    elif splited[0]=="Cancel":#参加者を除外する
                        if len(splited)>1:
                            if (int(splited[1]) in CoordinateLogs):
                                #CoordinateLogs.pop(int(splited[1]))  #IDが変わる可能性があるかも
                                CoordinateLogs[splited[1]]=None #とりあえずログを消す
                                send="Canceled"
                                conn.sendall(send.encode())
                                n-=1
                                if(n==0):
                                    os.remove("../data/result.json")#ログなどの初期化
                                    timeLogs=[]
                                    distLogs=[]
                                    CoordinateLogs={}
                                    Coordinates={}
                                    startflg=0
                    elif splited[0]=="Start":#シミュレーションをスタートする
                        message=""
                        startflg = 1
                        disaster=splited[2]
                        disasterScale=splited[3]
                        if(disaster=="津波"):
                            disasterScale+=(":"+splited[4])
                        print("serverstart")
                        #(主催者からStartが送られれば開始場所からのシミュレーションを開始
                        startPos.lat,startPos.lon=map(float,splited[1].split(","))
                        placesCoorsinates=getplace.get_Coordinates(startPos)
                        if(disaster=="地震"):
                            Earthquake.get_Dangerplaces(startPos)
                        elif (disaster=="津波"):
                            prefurl="https://map.yahooapis.jp/geoapi/V1/reverseGeoCoder?{detail}&lat={lat}&lon={lon}"
                            prefurl=prefurl.format(detail=HazapModules.APIPubWord,lat=startPos.lat,lon=startPos.lon)
                            prefResult=requests.get(prefurl)
                            prefResult=prefResult.json()
                            print(prefResult)
                            Coastplace.Coastplaces_get(100,prefResult["Feature"][0]["Property"]["AddressElement"][0]["Code"])
                            Coastplace.Fullpos(startPos,False)
                            #別スレッドで津波のシミュレーションを開始
                            #json.load(open("../data/squeezed.json",encoding="utf_8_sig"))
                            #thread = threading.Thread(target=simulate.simulatetunami, args=([json.load(open("../data/squeezed.json",encoding="utf_8_sig")),100,100]))
                            #thread.start()
                            simulate.simulatetunami(json.load(open("../data/squeezed.json",encoding="utf_8_sig")),float(splited[3]),float(splited[4]))
                        conn.sendall("DisasterStart:".encode())
                        timeLogs=[0]*n#0で初期化
                        distLogs=[0]*n
                    elif splited[0]=="Allpeople":#全参加者が何人か伝える
                        conn.sendall(("Allpeople:"+str(n)).encode())
                    elif splited[0]=="Message":#主催者からのメッセージが送られる
                        message=splited[1]
                        conn.sendall("OK".encode())
                    elif splited[0]=="Number" and startflg==1:#シミュレーションが開始されていれば参加人数と周囲にいる人数を送る
                        distflag=False
                        pos1=HazapModules.Coordinates()
                        pos1.lat=float(splited[2].split(",")[0])
                        pos1.lon=float(splited[2].split(",")[1])
                        for i in placesCoorsinates:
                            pos2=HazapModules.Coordinates()
                            pos2.lat=float(i[0])
                            pos2.lon=float(i[1])
                            dist=HazapModules.Calculatedistance(pos1,pos2)
                            if dist<107:
                                distflag=True
                                break
                        if int(splited[1]) in CoordinateLogs:
                            Coordinates[int(splited[1])]=splited[2].split(",")
                            CoordinateLogs[int(splited[1])].append(splited[2].split(","))
                            if(distflag==True):
                                send="Around:0,N:"+str(n)
                            else:
                                send="Around:"+str(count[int(splited[1])])+",N:"+str(n)
                            nowTime=time.time()
                            runFlg=0
                            currentPos=HazapModules.Coordinates()
                            currentPos.lat=float(splited[2].split(",")[0])
                            currentPos.lon=float(splited[2].split(",")[1])
                            beforePos=HazapModules.Coordinates()
                            beforePos.lat=float(CoordinateLogs[int(splited[1])][len(CoordinateLogs[int(splited[1])])-2][0])
                            beforePos.lon=float(CoordinateLogs[int(splited[1])][len(CoordinateLogs[int(splited[1])])-2][1])
                            dist=HazapModules.Calculatedistance(beforePos,currentPos)
                            distLogs[int(splited[1])]+=dist
                            if(timeLogs[int(splited[1])]!=0):#走っているかどうかの判定をする
                                if((dist/(nowTime-timeLogs[int(splited[1])]))>=(6.4*1000/3600)):#時速6.4kmよりも早ければ走ったと判定
                                    runFlg=1
                            timeLogs[int(splited[1])]=nowTime
                            send+=":"+str(runFlg)
                            print(timeLogs)
                        conn.sendall(send.encode())
                    elif (splited[0]=="Number" or splited[0]=="Wait") and startflg==0:#シミュレーションが開始されていない場合
                        send="Waiting..."
                        conn.sendall(send.encode())
                    elif splited[0]=="Wait" and startflg==1:#シミュレーションが開始されていた場合、災害ごとに必要な情報を送る
                        send="Start:"       
                        if(disaster=="地震"):
                            with open("../data/dangerplaces.json",encoding="utf_8_sig") as f:
                                jsonData=json.load(f)
                                sendData=json.dumps(jsonData,ensure_ascii=False).encode()
                        elif (disaster=="津波"):
                            with open("../data/simulated.json",encoding="utf_8_sig") as f:
                                jsonData=json.load(f)
                                sendData=json.dumps(jsonData,ensure_ascii=False).encode()
                        length=len(sendData)
                        sendSize=32768
                        left=0
                        right=sendSize
                        conn.sendall(("Start:"+str(length)+":"+disaster+":"+disasterScale).encode("utf-8"))#プレイヤーにjsonファイルのデータの長さ、災害の種類、規模の大きさを送る
                        time.sleep(1)
                        while True:
                            time.sleep(0.5)
                            if(left>length):
                                break
                            conn.sendall(sendData[left:right])
                            left+=sendSize
                            right+=sendSize
                    elif splited[0]=="End" and message!="":
                        endflg=1
                        startpoint=HazapModules.Coordinates()
                        startpoint.lat=float(CoordinateLogs[int(splited[1])][0][0])
                        startpoint.lon=float(CoordinateLogs[int(splited[1])][0][1])
                        endpoint=HazapModules.Coordinates()
                        endpoint.lat=float(CoordinateLogs[int(splited[1])][len(CoordinateLogs[int(splited[1])])-1][0])
                        endpoint.lon=float(CoordinateLogs[int(splited[1])][len(CoordinateLogs[int(splited[1])])-1][1])
                        rate=main.Result(startPos,list(map(lambda data:",".join(data),CoordinateLogs[int(splited[1])])),int(splited[2]),disaster,disasterScale)
                        places=json.load(open("../data/result.json",encoding="utf-8_sig"))
                        #ルートの長さを格納している変数
                        optimaldist=0
                        #最適な避難場所までの目安時間
                        optimaltime=0
                        if places["SaftyPlaces"]== None:
                            optimaldist=places["EvacuationPlaces"]["0"]["range"]
                            optimaltime=optimaldist/(5000/3600)
                        else:
                            wes = create_connection("ws://"+HazapModules.addres+":5000")
                            sendstr="long:"+str(startpoint.lat)+","+str(startpoint.lon)

                            for i in range(len(places["SaftyPlaces"])):
                                sendstr+=":"+places["SaftyPlaces"][str(i)].split(",")[0]+","+places["SaftyPlaces"][str(i)].split(",")[1]
                            sendstr+=places["EvacuationPlaces"]["0"]["coordinates"][0]+","+places["EvacuationPlaces"]["0"]["coordinates"][1]
                            wes.send(sendstr)
                            while True:
                                result =  wes.recv()
                                ravel=result.split(":")
                                if ravel[0] == "value":
                                    print(ravel[1])
                                    optimaldist=float(ravel[1])
                                    optimaltime=float(ravel[2])
                                    break
                            wes.close()


                    
                        tmpimg = Image.open("../img/route.png").convert("P")
                        with io.BytesIO() as output:
                            tmpimg.save(output,format="PNG")
                            contents = output.getvalue()#バイナリ取得
                        length=len(contents)
                        sendsize=4096
                        left=0
                        right=sendsize

                        time.sleep(0.5)

                        if(optimaldist>=distLogs[int(splited[1])]):
                            #rate+=(100/100*0.2)
                            rate+=str(100)+":"
                            print("Dist:",1)
                        elif(optimaldist==0):
                            if(distLogs[int(splited[1])]>100):
                                distLogs[int(splited[1])]=100
                            print("Dist:",(100-distLogs[int(splited[1])]*100))
                            rate+=str(100-distLogs[int(splited[1])])+":"
                            #rate+=(100/(100-distLogs[int(splited[1])]+0.01)*0.2)
                        else:
                            print("Dist:",(optimaldist/(distLogs[int(splited[1])])*100))
                            rate+=str(optimaldist/(distLogs[int(splited[1])])*100)+":"
                            #rate+=(1/(optimaldist/(distLogs[int(splited[1])]+0.01))*0.2)
                        optimaltime*=60.0
                        resultTime=float(splited[3])
                        if(optimaltime==0 and optimaldist!=0):
                            optimaltime=optimaldist/(5000/3600)
                        if(optimaltime>=resultTime):
                            print("Time:",100)
                            rate+=str(100)
                            #rate+=(100/100*0.2)
                        elif(optimaltime==0):
                            if(resultTime>100):
                                resultTime=100
                            print("Time:",100-resultTime)
                            rate+=str(100-resultTime)
                            #rate+=(100/(100-resultTime+0.01)*0.2)
                        else:
                            print("Time:",optimaltime/(resultTime)*100)
                            rate+=str(optimal/(resultTime)*100)
                            #rate+=(1/(optimaltime/(resultTime+0.01))*0.2)

                        #rate=int(1/rate*100)
                        params=rate.split(":")
                        evacuValue=int(100/(100/(float(params[0])+0.01)*0.4+100/(float(params[1])+0.01)*0.2+100/(float(params[2])+0.01)*0.2+100/(float(params[3])+0.01)*0.2))
                        print("Eva:",evacuValue)
                        conn.sendall(("Result:"+str(evacuValue)+":"+str(length)+":"+message+":"+rate).encode())#Result:Aliverate:byteLength

                        while True:
                            time.sleep(1)
                            if left>length:
                                break
                            conn.sendall(contents[left:right])
                            left+=sendsize
                            right+=sendsize
                            
                        print("ImageSended")
                    elif splited[0]=="End" and message=="":#主催者からのメッセージがまだ送られていなければ待たせる
                        conn.sendall("Waiting...".encode())
                    elif splited[0]=="Coordinates":#全参加者の現在地を送る
                        allplayer="Coordinates" 
                        for i in range(n):
                            allplayer+=":"
                            allplayer+=(CoordinateLogs[i][len(CoordinateLogs[i])-1][0]+","+CoordinateLogs[i][len(CoordinateLogs[i])-1][1])
                        conn.sendall(allplayer.encode())
                    elif splited[0]=="Image":
                        conn.sendall(contents)
                        continue
                    if(startflg==1):
                        count=getplace.Calcudens(Coordinates)
                    #conn.sendall(send.encode())
                    print(CoordinateLogs)
                    

if __name__=="__main__":
    try:
        server()
    except KeyboardInterrupt:
        print("server was stopped by keybord")
