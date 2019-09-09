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
import  time

def server():
    contents=None
    startflg=0
    count={}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        # IPアドレスとポートを指定
        n=0
        #s.bind(('192.168.0.49', 4000))
        s.bind(('127.0.0.1',4000))
        Coordinates={}#最新の位置情報を格納している辞書
        CoordinateLogs={}#最新の座標も含めてそれぞれの人の今までの座標を記録している辞書
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
                        conn.sendall(send.encode())
                    elif splited[0]=="Recruit" and startflg==1:
                        send="started"
                        conn.sendall(send.encode())
                    elif splited[0]=="Cancel":
                        if len(splited)>1:
                            if (int(splited[1]) in CoordinateLogs):
                                CoordinateLogs.pop(int(splited[1]))
                                send="Canceled"
                                conns.sendall(send.encode())
                    elif splited[0]=="Start":
                        message=""
                        startflg = 1
                        disaster=splited[2]
                        disasterScale=splited[3]
                        print("serverstart")
                        #(主催者からStartが送られれば開始場所からのシミュレーションを開始
                        startPos.lat,startPos.lon=map(float,splited[1].split(","))
                        Earthquake.get_Dangerplaces(startPos)
                        conn.sendall("DisasterStart:".encode())
                    elif splited[0]=="Allpeople":
                        conn.sendall(("Allpeople:"+str(n)).encode())
                    elif splited[0]=="Message":
                        message=splited[1]
                        conn.sendall("OK".encode())
                    elif splited[0]=="Number" and startflg==1:
                        if int(splited[1]) in CoordinateLogs:
                            Coordinates[int(splited[1])]=splited[2].split(",")
                            CoordinateLogs[int(splited[1])].append(splited[2].split(","))
                            send="Around:"+str(count[int(splited[1])])+",N:"+str(n)
                            print(splited)
                        else:
                            send="Failed"
                        conn.sendall(send.encode())
                    elif (splited[0]=="Number" or splited[0]=="Wait") and startflg==0:
                        send="Waiting..."
                        conn.sendall(send.encode())
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
                    elif splited[0]=="End" and message!="":#End:number:hp
                        main.Result(startPos,list(map(lambda data:",".join(data),CoordinateLogs[int(splited[1])])))
                        #print(type(Coordinates[int(splited[1])]))
                        #main.Result(startPos,list(map(lambda data:",".join(data),CoordinateLogs[int(splited[1])])))
                        hoge=HazapModules.Coordinates()
                        print(Coordinates[int(splited[1])])
                        hoge.lat=float(Coordinates[int(splited[1])][0])
                        hoge.lon=float(Coordinates[int(splited[1])][1])
                        getplace.GenerateHazard(hoge)
                        tmpimg = Image.open("../img/route.png").convert("P")
                        with io.BytesIO() as output:
                            tmpimg.save(output,format="PNG")
                            contents = output.getvalue()#バイナリ取得
                        length=len(contents)
                        sendsize=8192
                        left=0
                        right=sendsize

                        print("length=",length)
                        conn.sendall(("Result:"+str(length)).encode())#Result:Aliverate:byteLength
                        time.sleep(1)
                        while True:
                            if left>length:
                                break
                            conn.sendall(contents[left:right])
                            for i in range(len(contents[left:right])):
                                print(contents[left+i],end=" ")
                            left+=sendsize
                            right+=sendsize
                    elif splited[0]=="End" and message=="":
                        conn.sendall("Waiting...".encode())
                    elif splited[0]=="Coordinates":
                        allplayer="Coordinates" 
                        for i in range(n):
                            allplayer+=":"
                            allplayer+=(CoordinateLog[i][0]+","+CoordinateLog[i][1])
                        conn.sendall(allplayer.encode())
                    elif splited[0]=="Image":
                        conn.sendall(contents)
                        continue
                    if(startflg==1):
                        count=getplace.Calcudens(Coordinates)
                    #conn.sendall(send.encode())
                    print(CoordinateLogs)
                    

if __name__=="__main__":
    server()
