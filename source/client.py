import io
from PIL import Image
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('192.168.11.2', 4000))
    # サーバにメッセージを送る
    print("Connected!")
    s.sendall(input().encode())
    # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
    data = s.recv(262144)
    tmpimg2 = Image.open(io.BytesIO(data))#バイナリから画像に変換
    tmpimg2.save('../img/convrted.png')

