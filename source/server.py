import socket
import getplace


def server():
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
                    if(splited[0]=="Coordinates"):
                        Coordinates[len(Coordinates)]=splited[1].split(",")
                    elif splited[0]=="Start":
                        getplace.Calcudens(Coordinates)
                    elif splited[0]=="exit":
                        return 0
                    print(Coordinates)
                    send="your number is"+str(len(Coordinates)-1)
                    conn.sendall(send.encode())

if __name__=="__main__":
    server()