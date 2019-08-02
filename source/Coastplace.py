import zipfile
import os.path
import requests
from lxml import etree


def Coastplaces_get():
    url="http://nlftp.mlit.go.jp/ksj/api/1.0b/index.php/app/getKSJURL.xml?appId={key}&lang={lang}&dataformat=1&identifier=C23&prefCode={pref}&fiscalyear={year}"
    url=url.format(key="ksjapibeta1",lang="J",pref="45",year="2006")
    result=requests.get(url)
    tree=etree.fromstring(result.content)
    for i in tree.iter():
        if(i.tag=="zipFileUrl"):
            Download_zip(i.text)
    Xml_parse()
    
def Xml_parse():
    tree=etree.ElementTree(file="../data/C23-06_45-g.xml")
    xml=tree.getroot()
    for Curve in xml:
        for segments in Curve:
            for LineStringSegment in segments:
                for coastplace in LineStringSegment:
                    print(coastplace.text)
def Download_zip(text):
    filename=text.split("/")[-1]
    result=requests.get(text)
    with open(filename,"wb")as f:
        for chunk in result.iter_content(chunk_size=1024):
            if(chunk):
                f.write(chunk)
                f.flush()
        Uncompress_zip(filename)


def Uncompress_zip(filename):
    filepath="../data"
    zfile=zipfile.ZipFile(filename)
    zfile.extractall(filepath)


Coastplaces_get()
