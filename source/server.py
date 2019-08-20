import socket
import getplace


def server():
    startflg=0
    count={}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # IPアドレスとポートを指定
        n=0
        Coordinates={}
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
                    if(splited[0]=="Coordinates" and startflg==0):
                        Coordinates[len(Coordinates)]=splited[1].split(",")
                        send="your number is"+str(len(Coordinates)-1)
                    elif splited[0]=="Coordinates" and startflg==1:
                        send="started"
                    elif splited[0]=="Start":
                        startflg += 1
                        send="start!"
                    elif splited[0]=="Number":
                        send=str(count[int(splited[1])])
                    elif splited[0]=="End":
                        send="OK"
                        conn.sendall(send.encode())
                        return 0
                    if(startflg==1):
                        count=getplace.Calcudens(Coordinates)
                    conn.sendall(send.encode())

if __name__=="__main__":
    server()