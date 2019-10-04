import io
#from PIL import Image
import socket
import numpy
import HazapModules
import time
strings=[
    "Recruit:31.760254,131.080396",
    "Recruit:31.760254,131.080396",
    "Start:31.760254,131.080396:地震:震度3",
    "Message:hoge",
    "Number:0:31.760254,131.080396",
    "End:0:60:100"
]
for i in range(len(strings)):
    time.sleep(1)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((HazapModules.addres,4000))
        s.sendall(strings[i].encode("utf-8"))
        data = s.recv(2**7)
        s.close()
        print(data.decode())
