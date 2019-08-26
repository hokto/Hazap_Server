# クライアントを作成

import socket
import numpy
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('192.168.0.11', 4000))
    # サーバにメッセージを送る
    print("Connected!")
    s.sendall(input().encode())
    # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
    data = s.recv(1024)
    data=numpy.fromstring(data,dtype=numpy.unit8)
    print("receved:"+data.decode())
