import io
from PIL import Image
import socket
import numpy

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('192.168.11.133', 4000))
    # サーバにメッセージを送る
    print("Connected!")
    i=input()
    if i=="End":
        s.sendall(i.encode())
        s.close()
    else:
        s.sendall(i.encode())
    # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
        data = s.recv(1024*(2**10))
        print("receved:"+data.decode())
        s.close()
    # サーバにメッセージを送る
    print("Connected!")
    #h=input()
    #s.sendall(h.encode())
    # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
    #data = s.recv(262144)
    #if h =="Image":
    #	tmpimg2 = Image.open(io.BytesIO(data))#バイナリから画像に変換
    #	tmpimg2.save('../img/convrted.png')
    #elif h.split(":")[0]=="End":
    	#tmpimg2 = Image.open(io.BytesIO(data))#バイナリから画像に変換
    	#tmpimg2.save('../img/End.png')

    print(data)
