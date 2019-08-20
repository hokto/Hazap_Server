import socket
import getplace


def server():
    startflg=0
    count={}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # IPアドレスとポートを指定
        n=0
        Coordinates={}
        CoordinateLogs=[]
        s.bind(('192.168.11.2', 4000))
        # 1 接続
        s.listen(1)
        # connection するまで待つ
        while True:
            # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
            conn, addr = s.accept()
            with conn:
                while True:
                    # データを受け取る
                    data = conn.recv(2048)
                    if not data:
                        break
                    rec=data.decode()
                    splited=rec.split(":")
                    if(splited[0]=="Recruit" and startflg==0):
                        send="your number is"+str(n)
                        CoordinateLogs.append([])
                        CoordinateLogs[n].append(splited[1].split(","))
                        Coordinates[n]=splited[1].split(",")
                        n+=1
                    elif splited[0]=="Recruit" and startflg==1:
                        send="started"
                    elif splited[0]=="Start":
                        startflg = 1
                        send="start!"
                    elif splited[0]=="Number" and startflg==1:
                        Coordinates[int(splited[1])]=splited[2].split(",")
                        CoordinateLogs[int(splited[1])].append(splited[2].split(","))
                        send=str(count[int(splited[1])]/len(count))
                    elif splited[0]=="End":
                        send="OK"
                        conn.sendall(send.encode())
                        return 0
                    if(startflg==1):
                        print("CoordinateLogs",CoordinateLogs[1])
                        count=getplace.Calcudens(Coordinates)
                    conn.sendall(send.encode())
                    

if __name__=="__main__":
    server()