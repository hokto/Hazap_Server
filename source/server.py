import socket

# AF = IPv4 という意味
# TCP/IP の場合は、SOCK_STREAM を使う
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # IPアドレスとポートを指定
    s.bind(('192.168.11.133', 4000))
    # 1 接続
    s.listen(1)
    # connection するまで待つ
    while True:
        # 誰かがアクセスしてきたら、コネクションとアドレスを入れる
        conn, addr = s.accept()
        with conn:
            while True:
                # データを受け取る
                data = conn.recv(4096)
                print(type(data))
                if not data:
                    print("Test02")
                    break
                if data.decode()=="Hello,world!!":
                    print("Test03")
                    print("received Hello,world!!")
                    conn.sendall(b"Hello,world!!")
                    break
                print(data.decode())
                conn.sendall(b'Hello')
                break
