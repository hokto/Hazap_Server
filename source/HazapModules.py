import math
class Coordinates:#緯度、経度格納クラス
    lat=0.0
    lon=0.0
def TwoDimensionsSort(data,targetIdx,left,right):#二次元配列用ソート。引数にそれぞれ、ソートしたいデータのリスト、ソートする対象となるデータが入っている要素番号、リストの先頭、リストの末尾を入れる。
    i=left+1
    k=right
    while(i<k):
        while(float(data[i][targetIdx])<float(data[left][targetIdx]) and i<right):
            i+=1
        while(float(data[k][targetIdx])>=float(data[left][targetIdx]) and k>left):
            k-=1
        if(i<k):
            data[i],data[k]=data[k],data[i]
        if(float(data[left][targetIdx])>float(data[k][targetIdx])):
            data[left],data[k]=data[k],data[left]
        if(left<k-1):
            TwoDimensionsSort(data,targetIdx,left,k-1)
        if(k+1<right):
            TwoDimensionsSort(data,targetIdx,k+1,right)
    return data
def Calculatedistance(pos1,pos2):
    r=6378100
    return math.sqrt((r*math.radians(abs(pos1.lon-pos2.lon)))**2+(r*math.radians(abs(pos1.lat-pos2.lat)))**2)
IpAdress="192.168.0.49"
