import socket
import getplace
import Earthquake
import HazapModules
import main
import json
def server():
    startflg=0
    count={}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        # IPアドレスとポートを指定
        n=0
        Coordinates={}
        CoordinateLogs={}
        s.bind(('192.168.11.133', 4000))
        # 1 接続
        s.listen(1)
        # connection するまで待つ
        startPos=HazapModules.Coordinates()
        while True:
            send="Invalid"
            # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
            conn, addr = s.accept()
            with conn:
                while True:
                    # データを受け取る
                    data = conn.recv(10240)
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
                        send="start!"
                        #(主催者からStartが送られれば開始場所からのシミュレーションを開始
                        startPos.lat,startPos.lon=map(float,splited[1].split(","))
                        Earthquake.get_Dangerplaces(startPos)
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
                        send="Wait:True"
                        f=open("../data/dangerplaces.json","r")
                        data=json.load(f)
                        print(data)
                        #conn.sendall(send.encode())
                        conn.sendall(json.dumps(data).encode())
                        print("ReturnJson")#jsonファイル送信する処理 
                    
                    elif splited[0]=="End":
                        send="OK"
                        conn.sendall(send.encode())
                        main.Result(startPos,list(map(lambda data:",".join(data),CoordinateLogs[int(splited[1])])))
                        return 0
                    if(startflg==1):
                        count=getplace.Calcudens(Coordinates)
                    conn.sendall(send.encode())
                    print(CoordinateLogs)
                    

if __name__=="__main__":
    server()
