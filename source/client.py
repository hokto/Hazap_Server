import io
#from PIL import Image
import socket
import numpy
import HazapModules
with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect((HazapModules.addres,4000))
    #s.connect(("192.168.0.13",4000))

    # サーバにメッセージを送る
    print("Connected!")
    i=input()
    #i="Start:31.760254,131.080396"
    if i=="End":
        s.sendall(i.encode())
        s.close()
    else:
        s.sendall(i.encode("utf-8"))
    # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
        data = s.recv(1024*(2**10))
        print("receved:"+data.decode("utf-8"))
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
