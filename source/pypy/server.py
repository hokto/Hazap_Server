import socket

# AF = IPv4 という意味
# TCP/IP の場合は、SOCK_STREAM を使う
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # IPアドレスとポートを指定
    s.bind(('10.10.54.102', 4000))
    # 1 接続
    s.listen(1)
    # connection するまで待つ
    while True:
        # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
        conn, addr = s.accept()
        with conn:
            while True:
                # データを受け取る
                data = conn.recv(1024)
                if not data:
                    break
                if data.decode()=="Hello,world!!":
                    print("received Hello,world!!")
                    conn.sendall(b"Hello,world!!")
                    break
                print(data.decode())
                # クライアントにデータを返す(b -> byte でないといけない)
                conn.sendall(b'Hello')