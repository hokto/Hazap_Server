import socket
import getplace


def server():
    startflg=0
    count={}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # IPアドレスとポートを指定
        n=0
        Coordinates={}
        CoordinateLogs={}
        s.bind(('192.168.11.2', 4000))
        # 1 接続
        s.listen(1)
        # connection するまで待つ
        while True:
            send="Invalid"
            # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
            conn, addr = s.accept()
            with conn:
                while True:
                    # データを受け取る
                    data = conn.recv(4096)
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
                    elif splited[0]=="Number" and startflg==1:
                        if int(splited[1]) in CoordinateLogs:
                            Coordinates[int(splited[1])]=splited[2].split(",")
                            CoordinateLogs[int(splited[1])].append(splited[2].split(","))
                            send="Around:"+str(count[int(splited[1])])+",N:"+str(n)
                        else:
                            send="Failed"
                    elif splited[0]=="Number" and startflg==0:
                        send="Waiting..."
                    elif splited[0]=="End":
                        send="OK"
                        conn.sendall(send.encode())
                        return 0
                    if(startflg==1):
                        count=getplace.Calcudens(Coordinates)
                    conn.sendall(send.encode())
                    print(CoordinateLogs)
                    

if __name__=="__main__":
    server()