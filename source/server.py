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


def server():
    contents=None
    startflg=0
    endflg=0
    count={}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        # IPアドレスとポートを指定
        n=0
        s.bind(('192.168.11.2', 4000))
        Coordinates={}#最新の位置情報を格納している辞書
        CoordinateLogs={}#最新の座標も含めてそれぞれの人の今までの座標を記録している辞書
        disaster=""#災害の種類
        disasterScale=""#災害の規模
        # 1 接続
        s.listen(1)
        # connection するまで待つ
        startPos=HazapModules.Coordinates()
        while True:
            send="Invalid"
            # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
            conn, addr = s.accept()
            print("connected from:",addr)
            with conn:
                while True:
                    # データを受け取る
                    data = conn.recv(1024*(2**5))
                    send="Invalid"
                    if not data:
                        break
                    rec=data.decode()
                    splited=rec.split(":")
                    if(splited[0]=="Recruit" and startflg==0):
                        send=str(n)
                        CoordinateLogs[n]=[]
                        pl=splited[1].split(",")
                        CoordinateLogs[n].append(pl)
                        Coordinates[n]=splited[1].split(",")
                        send="number:"+str(n)
                        n+=1
                        print(splited)

                    elif splited[0]=="Recruit" and startflg==1:
                        send="started"
                    elif splited[0]=="Cancel":
                        if len(splited)>1:
                            if (int(splited[1]) in CoordinateLogs):
                                CoordinateLogs.pop(int(splited[1]))
                                send="Canceled"
                    elif splited[0]=="Start":
                        startflg = 1
                        disaster=splited[2]
                        disasterScale=splited[3]
                        print("serverstart")
                        send="start!"
                        #(主催者からStartが送られれば開始場所からのシミュレーションを開始
                        startPos.lat,startPos.lon=map(float,splited[1].split(","))
                        Earthquake.get_Dangerplaces(startPos)
                    elif splited[0]=="Allpeople":
                        conn.sendall(("Allpeople:"+n).encode())
                    elif splited[0]=="Number" and startflg==1:
                        if int(splited[1]) in CoordinateLogs:
                            Coordinates[int(splited[1])]=splited[2].split(",")
                            CoordinateLogs[int(splited[1])].append(splited[2].split(","))
                            send="Around:"+str(count[int(splited[1])])+",N:"+str(n)
                            print(splited)
                        else:
                            send="Failed"
                    elif (splited[0]=="Number" or splited[0]=="Wait") and startflg==0:
                        send="Waiting..."
                    elif splited[0]=="Wait" and startflg==1:
                        send="Start:"
                        with open("../data/dangerplaces.json",encoding="utf_8_sig") as f:
                            jsonData=json.load(f)
                            sendData=json.dumps(jsonData,ensure_ascii=False).encode()
                        length=len(sendData)
                        sendSize=1024
                        left=0
                        right=sendSize
                        conn.sendall(("Start:"+str(length)+":"+disaster+":"+disasterScale).encode("utf-8"))#プレイヤーにjsonファイルのデータの長さ、災害の種類、規模の大きさを送る
                        time.sleep(1)
                        while True:
                            time.sleep(1)
                            if(left>length):
                                break
                            conn.sendall(sendData[left:right])
                            left+=sendSize
                            right+=sendSize
                        print("Sended") 
                    elif splited[0]=="End":
                        endflg=1
                        startpoint=HazapModules.Coordinates()
                        startpoint.lat=float(CoordinateLogs[int(splited[1])][0][0])
                        startpoint.lon=float(CoordinateLogs[int(splited[1])][0][1])
                        endpoint=HazapModules.Coordinates()
                        endpoint.lat=float(CoordinateLogs[int(splited[1])][len(CoordinateLogs[int(splited[1])])-1][0])
                        endpoint.lon=float(CoordinateLogs[int(splited[1])][len(CoordinateLogs[int(splited[1])])-1][1])
                        
                        main.Result(startPos,list(map(lambda data:",".join(data),CoordinateLogs[int(splited[1])])))
                        getplace.GenerateHazard(startpoint,endpoint)
                        tmpimg = Image.open("../img/Generate.png").convert("P")
                        main.Result(startPos,list(map(lambda data:",".join(data),CoordinateLogs[int(splited[1])])))
                        places=json.load(open("../data/result.json",encoding="utf-8_sig"))
                        Bestroutelength=0
                        if places["SaftyPlaces"]== None:
                            Bestroutelength=places["EvacuationPlaces"]["0"]["range"]
                        else:
                            wes = create_connection("ws://192.168.11.2:5000")
                            sendstr="long:"+str(startpoint.lat)+","+str(startpoint.lon)

                            for i in range(len(places["SaftyPlaces"])):
                                sendstr+=":"+places["SaftyPlaces"][str(i)].split(",")[0]+","+places["SaftyPlaces"][str(i)].split(",")[1]
                            dist=0
                            sendstr+=places["EvacuationPlaces"]["0"]["coordinates"][0]+","+places["EvacuationPlaces"]["0"]["coordinates"][1]
                            wes.send(sendstr)
                            while True:
                                result =  wes.recv()
                                ravel=result.split(":")
                                if ravel[0] == "value":
                                    print(ravel[1])
                                    dist=float(ravel[1])
                                    break
                            Bestroutelength=dist
                            wes.close()

                        print("aiusfsfvg",Bestroutelength)
                        with io.BytesIO() as output:
                            tmpimg.save(output,format="PNG")
                            contents = output.getvalue()#バイナリ取得
                        length=len(contents)
                        sendsize=8192
                        left=0
                        right=sendsize

                        
                        time.sleep(0.5)

                        #ルートの長さを格納している変数
                        dist=0
                        #スタート地点とゴール地点とそこまでの経由地点の座標をなげて、正しい反応が返ってくるまでまつ。
                        webserversend="long"
                        coorsize=len(CoordinateLogs[int(splited[1])])
                        for i in range(coorsize):
                            webserversend+=":"+CoordinateLogs[int(splited[1])][i][0]+","+CoordinateLogs[int(splited[1])][i][1]
                        print(webserversend)

                        wes = create_connection("ws://192.168.11.2:5000")
                        wes.send(webserversend)

                        while True:
                            result =  wes.recv()
                            ravel=result.split(":")
                            if ravel[0] == "value":
                                print(ravel[1])
                                dist=float(ravel[1])
                                break
                        survival=str(dist).encode()
                        wes.close()
                        contents+=survival
                        print("length=",length)
                        conn.sendall((str(length)+":"+str(len(survival))).encode())
                        while True:
                            time.sleep(0.5)
                            if left>length+len(survival):

                                send=conn.sendall(contents[left:right])
                                break
                            conn.sendall(contents[left:right])
                            left+=sendsize
                            right+=sendsize


                        
                        #os.remove("../img/Generate.png")
                        #os.remove("../data/result.json")
                        #os.remove("../data/dangerplaces.json")
                        return 0
                    elif splited[0]=="Image":
                        conn.sendall(contents)
                        continue
                    if(startflg==1):
                        count=getplace.Calcudens(Coordinates)
                    conn.sendall(send.encode())
                    print(CoordinateLogs)
                    

if __name__=="__main__":
    server()
