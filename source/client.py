# クライアントを作成

import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('192.168.11.133', 4000))
    # サーバにメッセージを送る
    print("Connected!")
    i=input()
    if i=="End":
        s.sendall(i.encode())
        s.close()
    else:
        s.sendall(i)
    # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
        data = s.recv(1024)
        print("receved:"+data.decode())
