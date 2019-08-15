# クライアントを作成

import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('10.10.54.102', 4000))
    # サーバにメッセージを送る

    s.sendall(input().encode())
    # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
    data = s.recv(1024)
    #
    print(data.decode())