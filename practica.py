#!/usr/bin/python
#-*- coding: utf-8 -*-
import urllib
import xml.etree.ElementTree as ET
import unicodedata
import math
import codecs
import webbrowser
import os

class Activitat:
    'classe per guardar la informació de les activitats'

    def __init__(self,ID,root):
        self.adreca = {}
        self.id = ID
        self.root = root
        self.nom = root.find("nom").text
        self.nom_lloc = root.find("lloc_simple").find("nom").text
        adreca_simple = root.find("lloc_simple").find("adreca_simple")
        self.adreca["carrer"] = adreca_simple.find("carrer").text
        self.adreca["numero"] = int(adreca_simple.find("numero").text)
        self.adreca["municipi"] = (adreca_simple.find("municipi").text)
        self.districte = adreca_simple.find("districte").text
        self.data = root.find("data").find("data_proper_acte").text
        coords = adreca_simple.find("coordenades").find("googleMaps").attrib
        self.lat = eval(coords["lat"])
        self.lon = eval(coords["lon"])

    def distancia(self,lat,lon):
        lat1 = math.radians(lat)
        lat2 = math.radians(self.lat)
        diffLat = lat2 - lat1
        diffLon = math.radians(self.lon) - math.radians(lon)
        a = math.pow(math.sin(diffLat/2),2) + \
            math.cos(lat1) * math.cos(lat2) * \
            math.pow(math.sin(diffLon/2),2)
        c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        return 6371000 * c


ids_map = {}

def estilar(html):
    style = ET.SubElement(html,"style")
    style.text = "body { font-family: Trebuchet MS,Lucida Grande,Lucida Sans Unicode,Lucida Sans,Tahoma,sans-serif;  }" + \
        "h1 { font-size: 2.5em; }" + \
        "h2 { font-size: 1.875em; }" + \
        "p { font-size: 0.875em; } " + \
        "p.error { color: red; }" + \
        "th,tr,td { padding:0.8em; }" + \
        "th.activitat { background-color:rgb(43,160,194); text-align:center; }" + \
        "tr:nth-child(even){background-color:rgb(206,230,247);}" +\
        "tr:nth-child(odd){background-color:rgb(200,231,238);}" +\
        "th {  background-color:rgb(51,172,206); color: white; text-align:left;}";

def crear_taula(body):
    fila_nom = ET.SubElement(table,"tr")
    nomH = ET.SubElement(fila_nom,"th")
    nomH.text = "Nom"
    nom = ET.SubElement(fila_nom,"td")
    nom.text = act.nom

    fila_data = ET.SubElement(table,"tr")
    dataH = ET.SubElement(fila_data,"th")
    dataH.text = "Data"
    data = ET.SubElement(fila_data,"td")
    data.text = act.data

    fila_lloc = ET.SubElement(table,"tr")
    llocH = ET.SubElement(fila_lloc,"th")
    llocH.text = "Lloc"
    lloc = ET.SubElement(fila_lloc,"td")
    lloc.text = act.nom_lloc

    fila_adreca = ET.SubElement(table,"tr")
    adrecaH = ET.SubElement(fila_adreca,"th")
    adrecaH.text = u"Adreça"
    adreca = ET.SubElement(fila_adreca,"td")
    adreca.text = act.adreca["carrer"] + " " + repr(act.adreca["numero"]) + " " + act.adreca["municipi"]

    fila_districte = ET.SubElement(table,"tr")
    districteH = ET.SubElement(fila_districte,"th")
    districteH.text = "Districte"
    districte = ET.SubElement(fila_districte,"td")
    districte.text = act.districte

def normalitzar(name):

    if isinstance(name,unicode):
        name = unicodedata.normalize('NFKD', name)
    elif isinstance(name,str):
        name = unicodedata.normalize('NFKD', unicode(name, 'utf8'))
    name = u"".join([c for c in name if not unicodedata.combining(c)])
    return name.lower()


def trobar_actes_nom(nom,root):
    result = set([])
    for acte in root.iter("acte"):
        if normalitzar(nom) in normalitzar(acte.find("nom").text):
            i = int(acte.find("id").text)
            result.add(i)
            ids_map[i] = acte
        elif normalitzar(nom) in normalitzar(acte.find("lloc_simple").find("nom").text):
            i = int(acte.find("id").text)
            result.add(i)
            ids_map[i] = acte
        elif normalitzar(nom) in normalitzar(acte.find("lloc_simple").find("adreca_simple").find("districte").text):
            i = int(acte.find("id").text)
            result.add(i)
            ids_map[i] = acte
    return result

def trobar_actes(entrada,root):
    if isinstance(entrada,str):
        return trobar_actes_nom(entrada,root)
    elif isinstance(entrada,list):
        sets = []
        for elem in entrada:
            sets.append(trobar_actes(elem,root))
            result = sets[0]
        for elem in sets:
            result = result | elem
        return result
    elif isinstance(entrada,tuple):
        sets = []
        for elem in entrada:
            sets.append(trobar_actes(elem,root))
            result = sets[0]
        for elem in sets:
            result = result & elem
        return result
    else:
        print "L'entrada no és correcte"



activitats = {}
entrada1 = eval(eval(raw_input("Entra la primera entrada \n")))
entrada2 = eval(eval(raw_input("Entra la segona entrada \n")))
print "obrint url's....."
params = urllib.urlencode({"id":199})
fActes = urllib.urlopen("http://w10.bcn.es/APPS/asiasiacache/peticioXmlAsia?",params)
xml = fActes.read();
actesRoot = ET.fromstring(xml)
params = urllib.urlencode({"v":1})
fBicing = urllib.urlopen("http://wservice.viabicing.cat/v1/getstations.php?",params)
xml = fBicing.read()
bicngRoot = ET.fromstring(xml)
print "OK"

ids = trobar_actes(entrada1,actesRoot)

codecs.open("result.html","w","utf-8")
html = ET.Element("html")
estilar(html)
head = ET.SubElement(html,"head")
body = ET.SubElement(head,"body")
h1 = ET.SubElement(body,"h1")
h1.text = "Activitats Barcelona"
if len(ids) == 0:
    p = ET.SubElement(body,"p")
    p.set("class","error")
    p.text = "No hi ha activitats que compleixin els criteris introduits"
else:
    p = ET.SubElement(body,"p")
    p.text = "S'han trobat "+ repr(len(ids)) + " activitats"
n_act = 0
table = ET.SubElement(body,"table")
for elem in ids:
    n_act+=1
    tr = ET.SubElement(table,"tr")
    th = ET.SubElement(tr,"th")
    th.set("colspan","2")
    th.set("class","activitat")
    th.text = "Activitat " + repr(n_act)
    act = Activitat(elem,ids_map[elem])
    crear_taula(body)
    activitats[elem] = act
tree = ET.ElementTree(html)
tree.write("result.html")
webbrowser.open('file://' + os.path.realpath("result.html"))
