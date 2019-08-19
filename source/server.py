import socket
import getplace

# AF = IPv4 という意味
# TCP/IP の場合は、SOCK_STREAM を使う
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # IPアドレスとポートを指定
    n=0
    Coordinates=[]
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
                hoge=rec.split(":")
                if(hoge[0]=="Coordinates"):
                    Coordinates.append(hoge[1].split(","))
                elif hoge[0]=="Start":
                    n=len(Coordinates)
                    getplace.Calcudens(n,Coordinates)
                print(Coordinates)
                conn.sendall(b'Hello')